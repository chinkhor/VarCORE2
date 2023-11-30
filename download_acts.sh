#!/bin/bash
wget -O ACTS3.2.zip "https://drive.google.com/uc?id=1TERK99sNwSrKaUbHfvjojogfdjxqP7cp&export=download&confirm=yes"
unzip ACTS3.2.zip
rm ACTS3.2.zip
mv ACTS3.2/acts_3.2.jar .
rm -r __MACOSX
rm -r ACTS3.2

