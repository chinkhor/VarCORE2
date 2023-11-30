#!/bin/bash
echo "Setting up Environment"
bash ./setup_env.sh
echo
echo "Downloading ACTS3.2"
bash ./download_acts.sh
echo
echo "Installing cFS"
bash ./create_cfs.sh
echo
echo "Generating feature model"
python3 genFM.py -i RTW_cfs.txt -m cfs_time_map 
echo
echo "Generating ACTS input file"
python3 genACTSInput.py -a cFS_Time_ACTS_input.txt
echo
echo "Generating ACTS output file (2-way combinations)"
java -Ddoi=2 -Dchandler=solver -jar acts_3.2.jar cFS_Time_ACTS_input.txt cFS_Time_ACTS_output2.txt
echo
echo "Generating configuration files for cFS Time"
if test -d "config"; then
    rm -rf config
fi
mkdir config
python3 genCitCfg.py -a cFS_Time_ACTS_output2.txt -c cfs
echo
echo "Running cFS Time Build Test"
cp -r config cFS/.
cp runCfsBuildTest.sh cFS/.
cd cFS
bash ./runCfsBuildTest.sh > result.txt
echo
echo "Analyzing cFS Build Test result"
cd ..
cp cFS/result.txt .
python3 analyzeResult.py -r result.txt
