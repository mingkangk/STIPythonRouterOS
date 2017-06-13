#!/bin/bash

choice=$1
argument1=$2
argument2=$3
argument3=$4
argument4=$5

if [ "$choice" == "printpool" ]
then
	python dhcp.py printpool > printpool.txt

elif [ "$choice" == "printnet" ]
then
	python dhcp.py printnet > printnet.txt

elif [ "$choice" == "printserver" ]
then
	python dhcp.py printserver > printserver.txt

elif [ "$choice" == "addpool" ]
then
	python dhcp.py addpool $argument1 $argument2 > addpool.txt

elif [ "$choice" == "addnetwork" ]
then
	python dhcp.py addnetwork $argument1 $argument2 > addnetwork.txt

elif [ "$choice" == "addserver" ]
then
	python dhcp.py addserver $argument1 $argument2 > addserver.txt

elif [ "$choice" == "updatepool" ]
then
	python dhcp.py updatepool $argument1 $argument2 > updatepool.txt

elif [ "$choice" == "updatenetwork" ]
then
	python dhcp.py updatenetwork $argument1 $argument2 $argument3 > updatenetwork.txt

elif [ "$choice" == "updateserver" ]
then
	python dhcp.py updateserver $argument1 $argument2 > updateserver.txt

elif [ "$choice" == "delpool" ]
then
	python dhcp.py delpool $argument1 > delpool.txt

elif [ "$choice" == "delnetwork" ]
then
	python dhcp.py delnetwork $argument1 > delnetwork.txt

elif [ "$choice" == "delserver" ]
then
	python dhcp.py delserver $argument1 > delserver.txt

fi

