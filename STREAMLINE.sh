#!/bin/bash

experimental='false'
directed=''
local='false'
global='false'
statistical='false'
epr='false'

while getopts 'edslgp' flag; do
    case "${flag}" in
        e) experimental='true' ;;
        d) directed='--directed' ;;
        s) statistical='true' ;;
        l) local='true' ;;
        g) global='true' ;;
        p) epr='true' ;;
    esac
done

echo "Running STREAMLINE..."
cd STREAMLINE/

if [ $global ==  "true" ]; then
    echo "Evaluating Curated networks (global)"
    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml --STREAMLINE_global $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml --STREAMLINE_global $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml --STREAMLINE_global $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml --STREAMLINE_global $directed
fi

if [ $local ==  "true" ]; then
    echo "Evaluating Curated networks (local)"
    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml --STREAMLINE_local $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml --STREAMLINE_local $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml --STREAMLINE_local $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml --STREAMLINE_local $directed
fi

if [ $epr ==  "true" ]; then
    echo "Evaluating Curated networks (local)"
    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml --epr $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml --epr $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml --epr $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml --epr $directed

    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml --sepr
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml --sepr
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml --sepr
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml --sepr
fi

if [ $statistical ==  "true" ]; then
    echo "Evaluating Curated networks (EPr)"
    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml -e $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml -e $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml -e $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml -e $directed
    
    echo "Evaluating synthetic networks (AUC)"
    python  BLEvaluator_adapted.py --config config-files/Curated/config_mCAD.yaml -a $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_VSC.yaml -a $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_HSC.yaml -a $directed
    python  BLEvaluator_adapted.py --config config-files/Curated/config_GSD.yaml -a $directed
fi

if [ $experimental ==  "true" ]; then
    if [ $global ==  "true" ]; then
        echo "Evaluating experimental networks (global)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_yeast.yaml --STREAMLINE_global $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_hESC.yaml --STREAMLINE_global $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mDC.yaml --STREAMLINE_global $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mESC.yaml --STREAMLINE_global $directed
    fi
    
    if [ $local ==  "true" ]; then
        echo "Evaluating experimental networks (local)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_yeast.yaml --STREAMLINE_local $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_hESC.yaml --STREAMLINE_local $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mDC.yaml --STREAMLINE_local $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mESC.yaml --STREAMLINE_local $directed
    fi
    
    if [ $statistical ==  "true" ]; then
        echo "Evaluating experimental networks (EPr)"
        python  BLEvaluator_adapted.py --config config-files/experimental/config_yeast.yaml -e $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_hESC.yaml -e $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mDC.yaml -e $directed
        python  BLEvaluator_adapted.py --config config-files/experimental/config_mESC.yaml -e $directed
    fi
fi




