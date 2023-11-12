#!/bin/bash
T="true"
F="false"
if test -e "buildtest.log"; then
	rm buildtest.log
fi
#make SIMULATION=native ENABLE_UNIT_TESTS=true prep
make clean >>buildtest.log
make SIMULATION=native prep >>buildtest.log
cd cfe/modules/time/config
sed -i "s/CFE_MISSION_TIME_AT_TONE_WAS     true/CFE_MISSION_TIME_AT_TONE_WAS true/g" default_cfe_time_interface_cfg.h
sed -i "s/CFE_MISSION_TIME_AT_TONE_WAS     false/CFE_MISSION_TIME_AT_TONE_WAS false/g" default_cfe_time_interface_cfg.h
cd ../../../../config
num=$(ls -1 --file-type | grep -v '/$' | wc -l)
for (( i = 1; i <= $num; i++ )) 
do
	filename="cfg$i"
	while read line; do
		set -- $line
		directive=$1
		setting=$2
		if [[ "$setting" == "$T" ]]; then
			original=$F
		else
			original=$T
		fi
		cd ../cfe/modules/time/config
		search_str="$directive $original"
		replace_str="$directive $setting"
		sed -i "s/$search_str/$replace_str/g" default_cfe_time_internal_cfg.h
		sed -i "s/$search_str/$replace_str/g" default_cfe_time_interface_cfg.h
		cd ../../../../config
	done < $filename
	cd ..
	echo "############ Build $filename ########################" >>buildtest.log
	echo >>buildtest.log
	if test -d "build/exe"; then
		rm -r build/exe
	fi
	make install >>buildtest.log 2>&1 
	#make test
	#make lcov
	#lcov_file="lcov_$filename"
	#cp -r build/native/default_cpu1/lcov $lcov_file 
	echo "########### Done Build $filename ###################" >>buildtest.log
	echo >>buildtest.log
	if test -d "build/exe"; then
		echo "Build $filename passed"
	else
		echo "Build $filename failed"
	fi
	cd config
done
