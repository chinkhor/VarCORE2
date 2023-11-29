#!/bin/bash
if test -e "buildtest.log"; then
    rm buildtest.log
fi
sed -i "s: ssltest: ./ssltest:g" Makefile
make linuxconf >>buildtest.log 2>&1
make clean >>buildtest.log 2>&1
# apply fixes (next 3 lines) to resolve build error caused by enabling CONFIG_JAVA_BINDINGS
cp ../axtls_fix/generate_SWIG_interface.pl bindings/.
cp ../axtls_fix/Makefile bindings/java/.
cp ../axtls_fix/SSLClient.java bindings/java/.
cp ../axtls_fix/ssltest.c ssl/test/.
# inject 3-way error
cp ../axtls_inject/tls1.c ssl/.
sed -i 's:JAVA_EXE=/usr/java/default/bin/java:JAVA_EXE=/usr/bin/java:g' ssl/test/test_axssl.sh
cd config
sed -i 's:CONFIG_JAVA_HOME="":CONFIG_JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64":g' .config
sed -i 's:CONFIG_JAVA_HOME "":CONFIG_JAVA_HOME "/usr/lib/jvm/java-11-openjdk-amd64":g' config.h
# workaround config.h errors
sed -i 's:#define MUL_KARATSUBA_THRESH:#define MUL_KARATSUBA_THRESH 0:g' config.h
sed -i 's:#define SQU_KARATSUBA_THRESH:#define SQU_KARATSUBA_THRESH 0:g' config.h
cd config
num=$(ls -1 --file-type | grep -v '/$' | wc -l)
for (( i = 1; i <= $num; i++ )) 
do
    filename="cfg$i"
    while read line; do
        set -- $line
        replace_str=$line
        if [[ "$1" == "#" ]]; then
            search_str="$2=y"
	    search_str1="#define $2 1" 
	    replace_str1="#undef $2" 
        else
            feature=$1
            feature=${feature:0:-2}
            search_str="# $feature is not set"
            search_str1="#undef $feature"
            replace_str1="#define $feature 1"
        fi
        sed -i "s/$search_str/$replace_str/g" ../.config
        sed -i "s/$search_str1/$replace_str1/g" ../config.h
    done < $filename
    echo "############ Build $filename ########################" >../../buildtest_tmp.log
    echo >>../../buildtest_tmp.log
    cd ../..
    if test -d "_stage"; then
        rm -rf _stage
    fi
    make clean >>buildtest_tmp.log 2>&1
    make >>buildtest_tmp.log 2>&1 
    echo "########### Done Build $filename ###################" >>buildtest_tmp.log
    echo >>buildtest_tmp.log
    if grep -Fq Error buildtest_tmp.log > /dev/null
    then
        echo "Build $filename failed"    
    else
        echo "Build $filename passed"
    fi
    cat buildtest_tmp.log >>buildtest.log 2>&1
    rm buildtest_tmp.log
    cd config/config
done
