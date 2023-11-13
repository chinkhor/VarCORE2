#!/bin/bash
echo "Setting up Environment"
bash ./setup_env.sh
echo
echo "Installing axTLS"
wget https://sourceforge.net/projects/axtls/files/2.1.5/axTLS-2.1.5.tar.gz
tar -xvf axTLS-2.1.5.tar.gz
rm axTLS-2.1.5.tar.gz
echo
echo "Generating feature model"
python3 genFM.py -i RTW_axtls.txt -m axtls_map 
echo
echo "Generating ACTS input file"
python3 genACTSInput.py -a axtls_ACTS_input.txt
echo
echo "Generating ACTS output file (2-way combinations)"
echo "Linux_OS = true" >> axtls_ACTS_input.txt
echo "LUA_Build_Install = false" >> axtls_ACTS_input.txt
echo "CSharp_Bindings = false" >> axtls_ACTS_input.txt
echo "LUA_Bindings = false" >> axtls_ACTS_input.txt
echo "VB_NET_Bindings = false" >> axtls_ACTS_input.txt
java -Ddoi=2 -Dchandler=solver -jar acts_3.2.jar axtls_ACTS_input.txt axtls_ACTS_output2.txt
echo
echo "Generating configuration files for axTLS"
if test -d "config"; then
    rm -rf config
fi
mkdir config
python3 genCitCfg.py -a axtls_ACTS_output2.txt -c axtls
echo
echo "Running axTLS Build Test"
cp -r config axtls-code/config/.
cp runAxtlsBuildTest.sh axtls-code/.
cd axtls-code
bash ./runAxtlsBuildTest.sh > result.txt
echo
echo "Analyzing axTLS Build Test result"
cd ..
cp axtls-code/result.txt .
python3 analyzeResult.py -r result.txt

