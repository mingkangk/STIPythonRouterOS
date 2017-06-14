#!/bin/bash

echo "What do you want to do? "

read ans

if [ $ans == "printpool" ];
then
	curl -u admin:python -i http://localhost:5000/print/pool
elif [ $ans == "printnet" ];
then
	curl -u admin:python -i http://localhost:5000/print/net
elif [ $ans == "printserver" ];
then
	curl -u admin:python -i http://localhost:5000/print/server
elif [ $ans == "addpool" ];
then
	echo "Pool Name"
	read name

	echo "Range"
	read range

	curl -u admin:python -i -H "Content-Type: application/json" -X POST -d '{"range":'$range'}' http://localhost:5000/add/pool/$name
elif [ $ans == "addnetwork" ];
then
	echo "Subnet"
	read subnet

	echo "gateway"
	read gateway

	curl -u admin:python -i -H "Content-Type: application/json" -X POST -d '{"subnet":'$subnet', "gateway":'$gateway'}' http://localhost:5000/add/network
elif [ $ans == "addserver" ];
then
	echo "Interface"
	read interface

	echo "Pool Name"
	read poolname

	curl -u admin:python -i -H "Content-Type: application/json" -X POST -d '{"poolname":'$poolname'}' http://localhost:5000/add/server/$interface
elif [ $ans == "updatepool" ];
then
	echo "Number"
	read number

	echo "Range"
	read range

	curl -u admin:python -i -H "Content-Type: application/json" -X PUT -d '{"range":'$range'}' http://localhost:5000/update/pool/$number
elif  [ $ans == "updatenetwork" ];
then
	echo "Number"
	read number

	echo "Address"
	read address

	echo "Gateway"
	read gateway

	curl -u admin:python -i -H "Content-Type: application/json" -X PUT -d '{"address":'$address', "gateway":'$gateway'}' http://localhost:5000/update/network/$number
elif [ $ans == "updateserver" ];
then
	echo "Number"
	read number

	echo "Address"
	read address

	curl -u admin:python -i -H "Content-Type: application/json" -X PUT -d '{"address":'$address'}' http://localhost:5000/update/server/$number
elif [ $ans == "deletepool" ];
then
	echo "Number"
	read number

	curl -u admin:python -i -X DELETE http://localhost:5000/delete/pool/$number
elif [ $ans == "deletenetwork" ];
then
	echo "Number"
	read number

	curl -u admin:python -i -X DELETE http://localhost:5000/delete/network/$number
elif [ $ans == "deleteserver" ];
then
	echo "Number"
	read number

	curl -u admin:python -i -X DELETE http://localhost:5000/delete/server/$number
fi
