#!/bin/bash

experimental='false'
directed=''
local='false'
global='false'
statistical='false'

while getopts 'edslgp' flag; do
    case "${flag}" in
        e) experimental='true' ;;
        d) directed='--directed' ;;
        s) statistical='true' ;;
        l) local='true' ;;
        g) global='true' ;;
    esac
done

echo "Running STREAMLINE..."
cd STREAMLINE/


if [ $experimental ==  "true" ]; then
    if [ $global ==  "true" ]; then
        echo "Evaluating experimental networks (global)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_ESC.yaml --STREAMLINE_global $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_HEP.yaml --STREAMLINE_global $directed
    fi
    
    if [ $local ==  "true" ]; then
        echo "Evaluating experimental networks (local)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_ESC.yaml --STREAMLINE_local $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_HEP.yaml --STREAMLINE_local $directed
    fi
    
    if [ $statistical ==  "true" ]; then
        echo "Evaluating experimental networks (EPr)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_ESC.yaml -e $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_HEP.yaml -e $directed

        #echo "Evaluating experimental networks (AUC)"
        #python  BLEvaluator_adapted.py --config config-files/experimental/config_ESC.yaml -a $directed
        #python  BLEvaluator_adapted.py --config config-files/experimental/config_HEP.yaml -a $directed
        
    fi
fi
