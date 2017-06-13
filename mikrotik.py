#!flask/bin/python
from flask import Flask, jsonify, abort, request, url_for, make_response, json
import dhcp, os, csv, subprocess, json

mikrotik = Flask(__name__)

@mikrotik.route('/print/pool', methods=['GET'])
def printpool():
	subprocess.call(['./dhcp.sh', 'printpool'])
	with open('printpool.txt') as f:
		output = f.read()
	return jsonify({'DHCP pool' : output})

@mikrotik.route('/print/net', methods=['GET'])
def printnetwork():
	subprocess.call(['./dhcp.sh', 'printnet'])
	with open('printnet.txt') as f:
		output = f.read()
	return jsonify({'DHCP Network' : output})

@mikrotik.route('/print/server', methods=['GET'])
def printserver():
	subprocess.call(['./dhcp.sh', 'printserver'])
	with open('printserver.txt') as f:
		output = f.read()
	return jsonify({'DHCP Server' : output})

@mikrotik.route('/add/pool/<name>', methods=['POST'])
def addpool(name):
	range = request.json['range']
	subprocess.call(['./dhcp.sh', 'addpool', name, range])
	with open('addpool.txt') as f:
		output = f.read()
	return jsonify({'Pool' : output})

@mikrotik.route('/add/network', methods=['POST'])
def addnetwork():
	subnet = request.json['subnet']
	gateway = request.json['gateway']
	subprocess.call(['./dhcp.sh', 'addnetwork', subnet, gateway])
	with open('addnetwork.txt') as f:
		output = f.read()
	return jsonify({'Network' : output})

@mikrotik.route('/add/server/<interface>', methods=['POST'])
def addserver(interface):
	poolname = request.json['poolname']
        subprocess.call(['./dhcp.sh', 'addserver', interface, poolname])
        with open('addserver.txt') as f:
                output = f.read()
        return jsonify({'Server' : output})

@mikrotik.route('/update/pool/<number>', methods=['PUT'])
def updatepool(number):
	range = request.json['range']
        subprocess.call(['./dhcp.sh', 'updatepool', range, number])
        with open('updatepool.txt') as f:
                output = f.read()
        return jsonify({'Pool' : output})

@mikrotik.route('/update/network/<number>', methods=['PUT'])
def updatenetwork(number):
	address = request.json['address']
	gateway = request.json['gateway']
        subprocess.call(['./dhcp.sh', 'updatenetwork', address, gateway, number])
        with open('updatenetwork.txt') as f:
                output = f.read()
        return jsonify({'Network' : output})

@mikrotik.route('/update/server/<number>', methods=['PUT'])
def updateserver(number):
	address = request.json['address']
        subprocess.call(['./dhcp.sh', 'updateserver', address, number])
        with open('updateserver.txt') as f:
                output = f.read()
        return jsonify({'Server' : output})

@mikrotik.route('/delete/pool/<number>', methods=['DELETE'])
def delpool(number):
        subprocess.call(['./dhcp.sh', 'delpool', number])
        with open('delpool.txt') as f:
                output = f.read()
        return jsonify({'Pool' : output, 'Delete': True})

@mikrotik.route('/delete/network/<number>', methods=['DELETE'])
def delnetwork(number):
        subprocess.call(['./dhcp.sh', 'delnetwork', number])
        with open('delnetwork.txt') as f:
                output = f.read()
        return jsonify({'Network' : output, 'Delete': True})

@mikrotik.route('/delete/server/<number>', methods=['DELETE'])
def delIp(number):
	subprocess.call(['./dhcp.sh', 'delserver', number])
	with open('delserver.txt') as f:
		output = f.read()
	return jsonify({'Server': output, 'Delete': True})

if __name__ == '__main__':
	mikrotik.run(debug=True)
