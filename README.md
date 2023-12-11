# VarCORE<sup>+</sup>

VarCORE<sup>+</sup> is a framework used for requirement analysis and verification. 

## Setup (Linux only)

Ensure the following software are installed: Git, Make, CMake, GCC.

Download VarCORE<sup>+</sup>:

    git clone https://github/chinkhor/VarCORE2.git
    cd VarCORE2

## Evaluation

Evaluate VarCORE<sup>+</sup> on cFE TIME (TIME module of NASA cFS):

    ./runCfsRTW.sh  

Evaluate VarCORE<sup>+</sup> on axTLS:

    ./runAxtlsRTW.sh

## Evaluation Automation Notes:

The scripts (runCfsRTW.sh and runAxtlsRTW.sh) will run the following automatically:

     1. Download ACTS3.2
     2. Download and install cFS or axTLS
     3. Generate feature model for cFE TIME or axTLS
     4. Generate pair-wise combinatorial configurations using ACTS for cFE TIME or axTLS
     5. Build product variants for cFE TIME or axTLS 
     6. Analyze the build result to identify faulty feature setting(s)

## Utilities
- genFM.py: generate feature model from Requirement Traceability Worksheet (RTW)

     - input: Requirements Traceability Worksheet (RTW) (see RTW_cfs.txt for template)
     - input: Features to Code Variables mapping (see cfs_time_map for example)
     - output: RTW in csv format
     - output: feature model in XML format

- genACTSInput.py: construct input file for ACTS from feature model

     - input: file name for ACTS input file
     - output: constructed ACTS input file
     - dependency: shared.rtw generated by genFM.py

- genCitCfg.py: convert combinatorial interaction configurations to code configuration files

     - input: ACTS output file (i.e. combinatorial interaction configurations generated by ACTS)
     - input: component type: "cfs" or "axtls"
     - dependency: shared.rtw generated by genFM.py
     - dependency: ACTS output file generated by ACTS3.2.jar

- analyzeResult.py: analyze build result to identify faulty feature setting(s)

     - input: build test result
     - output: (console) build result and analysis
     - dependency: shared.rtw updated by genCitCfg.py
     - dependency: compile the product using config files generated by genCitCfg.py 

