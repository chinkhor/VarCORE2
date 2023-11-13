class RTW_Entry:
    # number of elements per RTW entry
    elements = 7
    
    def __init__(self):
        # requirement ID, for traceability
        self.ID = ""
        # indicator whether the entry is valid, 0: invalid, 1: valid
        self.Valid = 0
        # rules for parent-child relationship, including cross-tree constraint (between features of different parents) 
        # R1: root
        # R2: mandatory child
        # R3: optional child
        # R4: alternative child, select only one
        # R5: either child, select at least one
        # R6: combinations of R2 and R3
        # R7: cross-tree constraint, only use for features of different parents
        self.Rule = ""
        # parent feature, for R7 it represents first feature
        self.Parent = ""
        # children features, for R7 it represents second feature
        self.Children = []
        # requirement specification
        self.Req = ""
        # source of requirement for traceability
        self.Source = ""
        
    def printEntry(self):
        print("ID : {}, Valid : {}, Rule : {}, Parent : {}, Children : {}".format(self.ID, self.Valid, self.Rule, self.Parent, self.Children))
        print("Req: {}".format(self.Req))
        print("Source: {}".format(self.Source))
        print()
        
# RTW node is a feature (unit of functionality) 
class RTW_Node:
    def __init__(self, name):
        self.parent = None
        self.children = []
        # abstract feature, does not exist in the implementation, use to group concrete features
        self.abstract = False
        self.name = name
        self.rule = ""
        # private use variable
        # use to indicate the original rule (either R2 or R3) between parent and single child before combining become R6
        self.private = ""
        self.valid = 0
        # trace the requirements (IDs) associated with the feature
        self.tracedReq = []
    
    # the feature is a terminal node, no child
    def isLeaf(self):
        if len(self.children) > 0:
            return False
        else:
            return True
        
    def printNode(self):
        print("Node: {}, valid {}, Abstract: {}, Rule: {}, private: {}".format(self.name, self.valid, self.abstract, self.rule, self.private))
        if self.parent != None:
            print("   Parent: {}".format(self.parent.name))
        else:
            print("   Parent: None")
        if len(self.children) > 0:
            for child in self.children:
                print("   Child: {}".format(child.name))
        else:
            print("   Children: None")
        print("   Requirements Traceability: {}".format(self.tracedReq))
        
            
class RTW:
    def __init__(self, filename, feature_map=None):
        self.root = None
        self.sentences = []
        self.solutions = []
        self.FM_XML = []
        self.constraints = {}
        self.features = {}
        self.table = {}
        self.feature_map = {}
        self.dict_result = {}
        self.dict_formula = {'R2': self.R2Formula, 'R3': self.R3Formula, 'R4': self.R4Formula, 'R5': self.R5Formula}
        # sequence of method calls, the order is crucial to ensure dependencies
        # build RTW table (1st thing to do)
        self.parseRTW(filename)
        # construct RTW features/nodes (2nd thing to do) - depend on RTW table
        self.constructRTWFeatures()
        # construct feature map between feature model and code implementation - need RTW nodes
        if feature_map is not None:
            self.setupFeatureMap(feature_map)
        # construct feature diagram in tree - need RTW table and RTW nodes
        self.constructRTWTree()
        # construct feature model constraints - need RTW table
        # but need to reconstruct when RTW table is changed (e.g. entry validity is changed)
        self.constructRTWConstraints()
        # analyze feature model tree - need RTW nodes and RTW tree
        self.analyzeRTWTree()
        # construct feature model sentences (propositional logic expression)
        # need RTW nodes, RTW tree and RTW constraints
        self.constructFMSentences()
        # construct feature model in XML form - need RTW table, RTW nodes, RTW tree, RTW constraints 
        self.constructXMLFeatureModel()
        # export RTW table to CSV file - need RTW table
        self.exportRTW2CSV(filename.replace(".txt",".csv"))
        # export feature model to XML file - need feature model in XML form (represented by self.FM_XML)
        self.exportFeatureModel2XML(self.root.name.replace('_','') + "FeatureModel.xml")
        
    # validate the input file has a block of valid elements for single RTW entry
    def validateRTWEntry(self, index, lines):
        if ((index + RTW_Entry.elements - 1 < len(lines)) and
            lines[index].strip().startswith('ID') and 
            lines[index+1].strip().startswith('Valid') and
            lines[index+2].strip().startswith('Rule') and
            lines[index+3].strip().startswith('Parent') and
            lines[index+4].strip().startswith('Child') and
            lines[index+5].strip().startswith('Req') and
            lines[index+6].strip().startswith('Source')):
            return True
        else:
            return False
    
    # parse single RTW entry which consists of ID, valid, rule, parent feature, children features, requirement
    # specification and source of requirements (for traceability)
    def parseRTWEntry(self, line, multi_entry):
        separator = '-->'
        if not multi_entry:
            return line[line.find(separator) + len(separator):].strip()
        # multiple terms such as children
        else:
            words = line[line.find(separator) + len(separator):].strip().split(',')
            for i in range(len(words)):
                words[i] = words[i].strip()
            return words

    # construct a single RTW entry
    def constructRTWEntry(self, index, lines):
        entry = RTW_Entry()
        entry.ID = self.parseRTWEntry(lines[index], False)
        entry.Valid = int(self.parseRTWEntry(lines[index+1], False))
        entry.Rule = self.parseRTWEntry(lines[index+2], False)
        entry.Parent = self.parseRTWEntry(lines[index+3], False)
        entry.Children = self.parseRTWEntry(lines[index+4], True)
        entry.Req = self.parseRTWEntry(lines[index+5], False)
        entry.Source = self.parseRTWEntry(lines[index+6], False)
        self.table[entry.ID] = entry
        
    # parse the input RTW file to extract and construct RTW entries
    def parseRTW(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            f.close()
        for index in range(len(lines)):
            # every valid RTW entry starts with ID (first element of RTW entry) 
            if lines[index].strip().startswith('ID'):
                if self.validateRTWEntry(index, lines):
                    self.constructRTWEntry(index, lines)
                    index += RTW_Entry.elements
    
    # export the RTW table to CSV file
    # can be use for import to popular requirement management tools such as Jira, DOOR, etc
    def exportRTW2CSV(self, filename):
        with open(filename, 'w') as f:
            for ID in self.table:
                entry = self.table[ID]
                if entry.Rule == 'R1':
                    f.write("\"# " + entry.Req.replace('"','') + "\"\n")
            f.write("\n")
            f.write("Requirement ID,Requirement Specification,Rule,Parent Feature,Children Features,Source of Requirement\n")
            for ID in self.table:
                entry = self.table[ID]
                if entry.Valid and (entry.Rule != 'R1'):
                    children_str = ""
                    for child in entry.Children:
                        children_str = children_str + child + ", "
                    children_str = children_str[:-2]
                    f.write("\"" + entry.ID + "\",\"" + entry.Req.replace('"','') + "\",\"" + entry.Rule + "\",\"" + entry.Parent + "\",\"" + children_str + "\",\"" + entry.Source + "\"\n")
            f.close()
    
    # extract cross-tree constraints from RTW table, maintain in "self.constraints" dictionary
    # key of dictionary: requirement ID 
    # value of dictionary: propositional logic formula
    def constructRTWConstraints(self):
        self.constraints = {}
        for ID in self.table:
            entry = self.table[ID]
            if entry.Rule == 'R7':
                if not entry.Valid:
                    continue
                if 'require' in entry.Req.lower():
                    self.constraints[ID] = entry.Parent + " => " + entry.Children[0]
                else:
                    self.constraints[ID] = entry.Parent + " => !" + entry.Children[0]
    
    # extract features from RTW table, maintain in "self.features" dictionary
    # key of dictionary: feature (name)
    # valud of dictionary: RTW node (object) corresponding to the feature
    def constructRTWFeatures(self):
        self.features = {}
        for ID in self.table:
            entry = self.table[ID]
            if (not entry.Valid) or (entry.Parent == 'root'):
                continue
            node = entry.Parent
            if node not in self.features:
                self.features[node] = RTW_Node(node)
            # add requirement ID to the node's requirement tracing list (variable tracedReq)
            if entry.ID not in self.features[node].tracedReq:
                self.features[node].tracedReq.append(entry.ID)
            for child in entry.Children:
                if child not in self.features:
                    self.features[child] = RTW_Node(child)
                if entry.ID not in self.features[child].tracedReq:
                    self.features[child].tracedReq.append(entry.ID)
                    
    # map features to pre-processor directive macros (codes) in implementation
    # has dependency on constructRTWFeatures to construct RTW node first
    def setupFeatureMap(self, filename):
        self.feature_map = {}
        with open(filename, 'r') as f:
            lines = f.readlines();
            for line in lines:
                line = line.split()
                # if len is 1 or less, not a valid entry
                if len(line) <= 1:
                    continue
                self.feature_map[line[0]] = line[1]
            f.close()
        for feature in self.features:
            if feature not in self.feature_map:
                node = self.features[feature]
                node.abstract = True
                
    # construct the tree for features to show hierarchy of parents and children features relationship 
    # tree node is RTW node of the feature
    def constructRTWTree(self):
        for ID in self.table:
            entry = self.table[ID]
            # exclude constraints, which are tracked using "self.constraints" dictionary 
            if entry.Rule == 'R7':
                continue
            # identify the root feature
            if entry.Rule == 'R1':
                node = self.features[entry.Children[0]]
                self.root = node
                continue
            node = self.features[entry.Parent]
            if node.rule == "":
                node.rule = entry.Rule
            else:
                # change rule to R6 when combining R2 and R3
                node.rule = 'R6'
            for child in entry.Children:
                childnode = self.features[child]
                # variable "private" is used to indicate the original parent-child relationship (e.g. R2 and R3)
                # R2 and R3 may be combined and become R6
                childnode.private = entry.Rule 
                childnode.parent = node
                node.children.append(childnode)

    # analyze the RTW tree using "BFS" and set each node's validity
    # call out the node(s) which are not valid (disconnected nodes which have no parent, not appear in the tree)
    def analyzeRTWTree(self):
        priorityQ = []
        priorityQ.append(self.root)
        while len(priorityQ) > 0:
            node = priorityQ.pop(0)
            node.valid = 1
            for childnode in node.children:
                priorityQ.append(childnode)
        for feature in self.features:
            node = self.features[feature]
            if (node.parent == None) and (not node.valid):
                print("Feature: {} is not defined".format(node.name))
                node.printNode()
                # invalidate the entry in the RTW table
                for ID in node.tracedReq:
                    entry = self.table[ID]
                    entry.Valid = 0
                # reconstruct the self.constraints using new information 
                self.constructRTWConstraints()

    # construct feature model constraints in XML form 
    # the syntax is compatible for the featureIDE tool (for feature diagram rendering)
    def constructXMLFeaturModelConstraints(self):
        self.FM_XML.append('\t<constraints>\n') 
        for ID in self.constraints:
            constraint = self.constraints[ID].split("=>")
            self.FM_XML.append('\t\t<rule>\n')
            self.FM_XML.append('\t\t<description>Constraint Requirement: ' + ID + '</description>\n')
            self.FM_XML.append('\t\t\t<imp>\n')
            for c in constraint:
                if c.strip().startswith('!'):
                    self.FM_XML.append('\t\t\t\t<not>\n')
                    self.FM_XML.append('\t\t\t\t<var>' + c.strip().replace('!','') + '</var>\n')
                    self.FM_XML.append('\t\t\t\t</not>\n')
                else:
                    self.FM_XML.append('\t\t\t\t<var>' + c.strip() + '</var>\n')
            self.FM_XML.append('\t\t\t</imp>\n')
            self.FM_XML.append('\t\t</rule>\n')
        self.FM_XML.append('\t</constraints>\n')
      
    # construct feature model in XML form 
    # the syntax is compatible for the featureIDE tool (for feature diagram rendering)
    def constructXMLFeatureModel(self):
        self.FM_XML = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n',
                    '<featureModel>\n',
                    '\t<properties>\n',
                    '\t\t<graphics key="autolayoutconstraints" value="false"/>\n',
                    '\t\t<graphics key="legendposition" value="1223,200"/>\n',
                    '\t\t<graphics key="legendautolayout" value="false"/>\n',
                    '\t\t<graphics key="showconstraints" value="true"/>\n',
                    '\t\t<graphics key="showshortnames" value="false"/>\n',
                    '\t\t<graphics key="layout" value="horizontal"/>\n',
                    '\t\t<graphics key="showcollapsedconstraints" value="true"/>\n',
                    '\t\t<graphics key="legendhidden" value="false"/>\n',
                    '\t\t<graphics key="layoutalgorithm" value="1"/>\n',
                    '\t</properties>\n',
                    '\t<struct>\n']
        # use dfs to construct the "struct" of feature model
        # "struct" shows the parent-child hierarchical releationship
        self.constructXMLFeatureDiagram(self.root)
        self.FM_XML.append('\t</struct>\n')
        # construct feature model constraints
        self.constructXMLFeaturModelConstraints()
        self.FM_XML.append('</featureModel>\n')
        
    # use DFS to construct the feature diagram to show the parent-child hierarchical releationship 
    # the syntax is compatible for the featureIDE tool (for feature diagram rendering)
    def constructXMLFeatureDiagram(self, node):
        dict_keyword_start = {'R2': '\t\t<and ', 'R3': '\t\t<and ', 'R4': '\t\t<alt ', 'R5': '\t\t<or ', 'R6': '\t\t<and '}
        dict_keyword_end = {'R2': '\t\t</and>\n', 'R3': '\t\t</and>\n', 'R4': '\t\t</alt>\n', 'R5': '\t\t</or>\n', 'R6': '\t\t</and>\n'}
        if node.isLeaf():
            self.FM_XML.append('\t\t\t<feature name="' + node.name + '">\n')
             # add requirement ID as description for traceability
            self.FM_XML.append('\t\t\t<description>Requirements: ' + str(node.tracedReq) + '</description>\n')
            self.FM_XML.append('\t\t\t</feature>\n')
            return
        else:
            line = dict_keyword_start[node.rule]
            if node.abstract:
                line = line + 'abstract="true" '
            if node.rule == 'R2' or node.private == 'R2' or node.name == self.root.name:
                line = line + 'mandatory="true" '
            line = line + 'name="' + node.name + '">\n'
            self.FM_XML.append(line)
            # add requirement ID as description for traceability
            self.FM_XML.append('\t\t<description>Requirements: ' + str(node.tracedReq) + '</description>\n')
            for child in node.children:
                # recurcisve call using DFS to build feature diagram
                self.constructXMLFeatureDiagram(child)
            self.FM_XML.append(dict_keyword_end[node.rule])        
      
    # export the feature model to XML file
    def exportFeatureModel2XML(self, filename):
        with open(filename, 'w') as f:
            for line in self.FM_XML:
                f.write(line)
            f.close()
    
    # construct sentences for feature model (FM)
    # sentence is a propositional logic expression for parent-child relationship or cross-tree constraint releationship
    # the propositional logic definition is based on rules (R2, R3, R4, R5 and R7)
    def constructFMSentences(self):
        root = self.root.name
        self.sentences.append(root + " = true")    
        priorityQ = []
        priorityQ.append(self.root)
        while len(priorityQ) > 0:
            node = priorityQ.pop(0)
            rule = node.rule
            children = []
            for childnode in node.children:
                priorityQ.append(childnode)
                children.append(childnode.name)
                # R6 is combination of R2 and R3, so break down to R2 and R3
                # individual parent-child's rule is stored in private field of child's node 
                if rule == 'R6':
                    self.dict_formula[childnode.private](node.name, [childnode.name])  
            # construct the formula for each individual parent-child based on its rule
            if rule != 'R6' and (not node.isLeaf()):
                self.dict_formula[rule](node.name, children)
        # add feature model's cross-tree constraints to sentences list
        for ID in self.constraints:
            constraint = self.constraints[ID]
            self.sentences.append(constraint)        
        
    # construct sentence using given terms and operator
    # e.g. terms = FeatureA, FeatureB, ... and operator = &&
    # sentence = (FeatureA && FeatureB && ...)
    def constructSentence(self, terms, operator):
        sentence = "("
        for term in terms:
            sentence = sentence + term + operator
        sentence = sentence[:-4] + ")"
        return sentence
    
    # apply formula for R2 rule (mandatory child): parent <=> child
    # convert <=> to => for ACTS tool compatibility, i.e. parent => child, child => parent
    def R2Formula(self, parent, child):
        self.sentences.append(parent + " => " + child[0])
        self.sentences.append(child[0] + " => " + parent)
    
    # apply formula for R3 rule (optional child): child => parent
    def R3Formula(self, parent, child):
        self.sentences.append(child[0] + " => " + parent)
    
    # apply formula for R4 rule (select exactly only one child, i.e. xor): 
    # parent <=> (childA && !childB && ...) || (!childA && childB && ...)
    # convert <=> to => for ACTS tool compatibility, i.e. 
    # parent => (childA && !childB && ...) || (!childA && childB && ...), 
    # (childA && !childB && ...) || (!childA && childB && ...) => parent
    def R4Formula(self, parent, children):
        sentences = []
        n = len(children)
        for i in range(n):
            terms = []
            # R4 (xor): terms = childA or !childA, ...
            #           sentences = (childA && !childB && ...), (!childA && childB && ...)
            for j in range(n):
                term = "!" + children[j]
                if i == j:
                    term = children[j]
                terms.append(term)
             
            # construct "AND" sentence
            sentence = self.constructSentence(terms, " && ")
            sentences.append(sentence)
        
        # reuse R5 formula to perform OR operation for all the sentences
        self.R5Formula(parent, sentences)
        # add additional constraint: !parent => !childA && !childB && ...
        terms = []
        for child in children:
            terms.append("!" + child)
        sentence = self.constructSentence(terms, " && ")
        self.sentences.append("!" + parent + " => " + sentence)
      
    # apply formula for R5 rule (select at least one child, i.e. or): 
    # parent <=> (childA || childB || ...) 
    # convert <=> to => for ACTS tool compatibility, i.e. 
    # parent => (childA || childB || ...) 
    # (childA || childB ||..) => parent
    def R5Formula(self, parent, children):
        # construct "OR" sentence
        sentence = self.constructSentence(children, " || ") 
        self.sentences.append(parent + " => " + sentence)
        self.sentences.append(sentence + " => " + parent) 

    # generate input file for ACTS tool
    # the input file consists of system name, boolean parameters and constraints
    # boolean parameters and constraints are extracted from feature model
    def generateACTSInputFile(self, filename):
        with open(filename, 'w') as f:
            f.write("[System]\n")
            f.write("Name: {}\n\n".format(self.root.name))
            f.write("[Parameter]\n")
            for feature in self.features:
                node = self.features[feature]
                if node.valid:
                    f.write(feature + " (boolean): true, false\n")
            f.write("\n")
            f.write("[Constraint]\n")
            for s in self.sentences:
                f.write(s + "\n")
            f.write("\n")
            f.close()

    # generate configuration files based on ACTS output file
    # ACTS tool is used to generate test sets for 1-way, 2-way, 3-way combinations of features
    def generateCitCfgFiles(self, filename, component):
        with open(filename, 'r') as f:
            lines = f.readlines()
            f.close()
        # current support cFS Time and axTLS build system
        dict_createFileFunc = {'cfs': self.createCfsCfgFiles, 'axtls': self.createAxtlsCfgFiles}
        if component not in dict_createFileFunc:
            print("Invalid component {}".format(component))
            return
        # format of dict: cfg #: [start, end]
        dict_cfg = {}
        # clear the solutions
        self.solutions = []
        cfg_no = 0
        # l is the line #
        # find a block of feature lines for specific configuration
        for l in range(len(lines)):
            if "Configuration #" in lines[l]:
                line = lines[l].strip().split()
                cfg_no = int(line[1][1:-1])
                dict_cfg[cfg_no] = [l, -1]
            # ----...---- is the terminator of each configuration
            elif "-------------------------------------" in lines[l]:
                dict_cfg[cfg_no][1] = l
        for cfg_no in dict_cfg:
            start = dict_cfg[cfg_no][0]
            end = dict_cfg[cfg_no][1]
            self.constructCitCfgSolution(lines[start:end])    
            dict_createFileFunc[component]()
            
    # decode configurations from ACTS output file
    # each configuration is a solution that satisfies feature model
    def constructCitCfgSolution(self, lines):
        dict_solution = {}
        for line in lines:
            line = line.split()
            # if len is 1 or less, not a valid entry
            if len(line) <= 1:
                continue
            word = line[-1]
            if "=true" in word:
                word = word.replace("=true", "").strip()
                if word in self.feature_map:
                    dict_solution[word] = "True"
            elif "=false" in word:
                word = word.replace("=false", "").strip()
                if word in self.feature_map:
                    dict_solution[word] = "False"
        self.solutions.append(dict_solution)
            
    # get the test result from file
    def getTestResult(self, filename):
        self.dict_result = {'passed': [], 'failed': []}
        with open(filename, 'r') as f:
            for line in f:
                # file entry format: 
                #   Build cfg1 failed
                #   Build cfg6 passed
                # line[2] is either "failed" or "passed"
                # line[1] is cfgN where N is the cfg #
                line = line.split()
                cfg = line[1].replace("cfg", "")
                self.dict_result[line[2]].append(cfg)
            f.close()
        self.showTestResult()
         
    # check if number of tests matchs total configurations (represented by self.solutions)
    # one test per configuration
    def isCfgSetCompatible(self):
        total_tests = len(self.dict_result['passed']) + len(self.dict_result['failed'])
        if len(self.solutions) == total_tests:
            return True
        else:
            return False
        
    # analyze the test result to indetify failures triggered by single parameter or 2-way feature interaction 
    def analyzeTestResult(self, filename):
        self.getTestResult(filename)
        # abort test analysis if total tests do not match total configurations (represented by self.solutions) 
        if not self.isCfgSetCompatible():
            total_tests = len(self.dict_result['passed']) + len(self.dict_result['failed'])
            print("Total tests ({}) do not match with total configurations ({}), aborted test analysis!".format(total_tests, len(self.solutions)))
            return
        if len(self.dict_result['failed']) == 0:
            print("All tests passed, stop the analysis.")
            return
        # check if failures are due to single parameter configuration
        dict_feature_fail = self.findFailuresBySingleParameter()
        if len(dict_feature_fail) > 0:
            print("Failure triggered by single parameter, potential candidates: ")
            for key in dict_feature_fail:
                print("  {}".format(key))
        else:
            # if failures are not triggered by single parameter, 
            # proceed to check if it is triggered by 2-way feature interaction
            print("No failure triggered by single parameter\n")
            dict_interaction_fail = self.findFailuresBy2WayInteraction()
            if len(dict_interaction_fail) > 0:
                print("Failure triggered by 2-way feature interaction, potential candidates: ")
                for interaction in dict_interaction_fail:
                    print("  {}".format(interaction))
            else:
                print("No failure triggered by 2-way feature interaction")
  
    # find failures caused by single parameters, report all single parameters     
    def findFailuresBySingleParameter(self):
        dict_feature_fail = {}  
        # get all assignments of single parameters in configurations that failed build test
        # into a dictionary
        for cfg_no in self.dict_result['failed']:
            solution = self.solutions[int(cfg_no)-1]
            for feature in solution:
                key = feature + " = " + solution[feature]
                dict_feature_fail[key] = 1
        # remove those assignments in dictionary if the assignments appear in the configurations
        # that passed build test
        for cfg_no in self.dict_result['passed']:
            solution = self.solutions[int(cfg_no)-1]
            for feature in solution:
                key = feature + " = " + solution[feature]
                if key in dict_feature_fail:
                     del dict_feature_fail[key]
        # return the remaining parameters' assignments which are "potential candidates" for 
        # single parameter's failure
        return dict_feature_fail
    
    # find failures caused by 2-way (pair-wise) feature interaction, report the combination of two parameters     
    def findFailuresBy2WayInteraction(self):
        # find feature interaction failures
        dict_interaction_fail = {}
        # get all 2-way combinations of parameters' assignments from configurations that failed build test
        # into a dictionary
        for cfg_no in self.dict_result['failed']:
            solution = self.solutions[int(cfg_no)-1]
            assignments = []
            for feature in solution:
                assignment = feature + " = " + solution[feature]
                assignments.append(assignment)
            for i in range (len(assignments)):
                for j in range (i, len(assignments)):
                    if assignments[i] != assignments[j]:
                        interaction = assignments[i] + " && " + assignments[j]
                        dict_interaction_fail[interaction] = 1  
        # remove those combinations' assignments in dictionary if the combinations appear in the configurations
        # that passed build test
        for cfg_no in self.dict_result['passed']:
            solution = self.solutions[int(cfg_no)-1]
            assignments = []
            for feature in solution:
                assignment = feature + " = " + solution[feature]
                assignments.append(assignment)
            for i in range (len(assignments)):
                for j in range (i, len(assignments)):
                    if assignments[i] != assignments[j]: 
                        interaction = assignments[i] + " && " + assignments[j]
                        if interaction in dict_interaction_fail:
                            del dict_interaction_fail[interaction]
        # return the remaining parameters' assignments which are "potential candidates" for 
        # 2-way feature interaction failure
        return dict_interaction_fail
    
    def showRTWConstraints(self):
        print("Constraints:")
        for ID in self.constraints:
            print(self.constraints[ID])
        print()
        
    def showRTWTable(self):
        print("RTW Entries:")
        for ID in self.table:
            entry = self.table[ID]
            entry.printEntry()
        print()
        
    def showRTWFeatures(self):
        for feature in self.features:
            node = self.features[feature]
            node.printNode()
    
    def showSentences(self):
        print("\nSentences list: ")
        for s in self.sentences:
            print(s)
        print()
 
    def showSolutions(self):
        print("\nModel Solutions: ")
        for count in range(len(self.solutions)):
            print("solution " + str(count) + " :")
            solutions = self.solutions[count]
            for feature in solutions:
                print('   {0:15s} : {1:5s}'.format(feature, solutions[feature]))   
                
    def showFeatureMap(self):
        print("\nFeature Map: ")
        for feature in self.feature_map:
            print('   {0:15s} : {1:30s}'.format(feature, self.feature_map[feature]))
            
    def showTestResult(self):
        print("\nTest Result:")
        for status in self.dict_result:
            print("  {}: {}".format(status, self.dict_result[status]))
        print()
  
    # --------------------------------------------------------------------------
    # the following methods are specific and depending on system's build system
    # --------------------------------------------------------------------------
      
    # create configuration files for cFS Time, compatible for cFS Time build system only
    def createCfsCfgFiles(self):
        for count in range(len(self.solutions)):
            filename = "config/cfg" + str(count + 1)
            with open(filename, 'w') as f:
                solutions = self.solutions[count]
                for feature in solutions:
                    f.write(self.feature_map[feature] + " " + solutions[feature].lower() + '\n')
                f.close()
 
    # create configuration files for axTLS, compatible for axTLS build system only
    def createAxtlsCfgFiles(self):
        for count in range(len(self.solutions)):
            filename = "config/cfg" + str(count + 1)
            with open(filename, 'w') as f:
                solutions = self.solutions[count]
                for feature in solutions:
                    if solutions[feature] == "True":
                        f.write(self.feature_map[feature] + "=y\n")
                    else:
                        f.write("# " + self.feature_map[feature] + " is not set\n")
                f.close() 
