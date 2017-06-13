#!/usr/bin/python

import re
import sys, posix, time, md5, binascii, socket, select

class ApiRos:
    "Routeros api"
    def __init__(self, sk):
        self.sk = sk
        self.currenttag = 0
        
    def login(self, username, pwd):
        for repl, attrs in self.talk(["/login"]):
            chal = binascii.unhexlify(attrs['=ret'])
        md = md5.new()
        md.update('\x00')
        md.update(pwd)
        md.update(chal)
        self.talk(["/login", "=name=" + username,
                   "=response=00" + binascii.hexlify(md.digest())])

    def talk(self, words):
        if self.writeSentence(words) == 0: return
        r = []
        while 1:
            i = self.readSentence();
            if len(i) == 0: continue
            reply = i[0]
            attrs = {}
            for w in i[1:]:
                j = w.find('=', 1)
                if (j == -1):
                    attrs[w] = ''
                else:
                    attrs[w[:j]] = w[j+1:]
            r.append((reply, attrs))
            if reply == '!done': return r

    def writeSentence(self, words):
        ret = 0
        for w in words:
            self.writeWord(w)
            ret += 1
        self.writeWord('')
        return ret

    def readSentence(self):
        r = []
        while 1:
            w = self.readWord()
            if w == '': return r
            r.append(w)
            
    def writeWord(self, w):
        print "<<< " + w
        self.writeLen(len(w))
        self.writeStr(w)

    def readWord(self):
        ret = self.readStr(self.readLen())
        print ">>> " + ret
        return ret

    def writeLen(self, l):
        if l < 0x80:
            self.writeStr(chr(l))
        elif l < 0x4000:
            l |= 0x8000
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        elif l < 0x200000:
            l |= 0xC00000
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        elif l < 0x10000000:        
            l |= 0xE0000000         
            self.writeStr(chr((l >> 24) & 0xFF))
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        else:                       
            self.writeStr(chr(0xF0))
            self.writeStr(chr((l >> 24) & 0xFF))
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))

    def readLen(self):              
        c = ord(self.readStr(1))    
        if (c & 0x80) == 0x00:      
            pass                    
        elif (c & 0xC0) == 0x80:    
            c &= ~0xC0              
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xE0) == 0xC0:    
            c &= ~0xE0              
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xF0) == 0xE0:    
            c &= ~0xF0              
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xF8) == 0xF0:    
            c = ord(self.readStr(1))     
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        return c                    

    def writeStr(self, str):        
        n = 0;                      
        while n < len(str):         
            r = self.sk.send(str[n:])
            if r == 0: raise RuntimeError, "connection closed by remote end"
            n += r                  

    def readStr(self, length):      
        ret = ''                    
        while len(ret) < length:    
            s = self.sk.recv(length - len(ret))
            if s == '': raise RuntimeError, "connection closed by remote end"
            ret += s
        return ret

   
    def get_num(x):
	return int (''.join(ele for ele in x if ele.isdigit()))

    def printpool(self):
	self.inputSentence = ['/ip/pool/print']
	self.inputSentence.append('=count-only=')
	self.writeSentence(self.inputSentence)
	count = int(self.readSentence()[1][5:])
	
	if (isinstance(count, int)):
		number = 0
		while (number <= count): 
			self.inputSentence = ['/ip/pool/print']
			self.writeSentence(self.inputSentence)
			self.readSentence()

			number = number+4
	else:
		print "not integer"

    def printnet(self):
        self.inputSentence = ['/ip/dhcp-server/network/print']
        self.inputSentence.append('=count-only=')
        self.writeSentence(self.inputSentence)
        count = int(self.readSentence()[1][5:])

	if (isinstance(count, int)):
		number = 0
		while (number <= count):
			self.inputSentence = ['/ip/dhcp-server/network/print']
			self.writeSentence(self.inputSentence)
			self.readSentence()

			number = number+1
	else:
		print "not integer"

    def printserver(self):
        self.inputSentence = ['/ip/dhcp-server/print']
        self.inputSentence.append('=count-only=')
        self.writeSentence(self.inputSentence)
        count = int(self.readSentence()[1][5:])
	
	if (isinstance(count, int)):
		number = 0
		while (number <= count):
			self.inputSentence = ['/ip/dhcp-server/print']
			self.writeSentence(self.inputSentence)
			self.readSentence()

			number= number+1
	else:
		print "not integer"

    def addpool(self, name, range):
	self.inputSentence = ['/ip/pool/add']
        self.inputSentence.append('=name='+ name)
        self.inputSentence.append('=ranges='+ range)
        self.writeSentence(self.inputSentence)
        self.readSentence()    

    def addnetwork(self, subnet, ipaddr):
	self.inputSentence = ['/ip/dhcp-server/network/add']
        self.inputSentence.append('=address='+ subnet)
        self.inputSentence.append('=gateway='+ ipaddr)
        self.writeSentence(self.inputSentence)
        self.readSentence()

    def addserver(self, interface, name):
	self.inputSentence = ['/ip/dhcp-server/add']
	self.inputSentence.append('=interface=' + interface)
	self.inputSentence.append('=address-pool=' + name)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delpool(self, ans):
	self.inputSentence = ['/ip/pool/remove']
	self.inputSentence.append('=numbers='+ ans)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delnetwork(self, ans):
	self.inputSentence = ['/ip/dhcp-server/network/remove']
	self.inputSentence.append('=numbers='+ ans)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delserver(self, ans):
	self.inputSentence = ['/ip/dhcp-server/remove']
	self.inputSentence.append('=numbers='+ ans)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def addDHCP(self):
	reply="no"
	while ( reply == "no"):
		print '1. Add Address Pool'
		print '2. Add Network'
		print '3. Add Server'
		print '4. Quit to main menu'
		reply2 = raw_input ('Task: ')

		if (reply2 == '1'):
			self.addpool()

		elif (reply2 == '2'):
			self.addnetwork()

		elif (reply2 == '3'):
			self.addserver()

		elif (reply2 == '4'):
			main()
		
		else:
			print 'incorrect Input'

		reply = raw_input ('Return to main menu?: ')

    def updatepool(self, range, number):
	self.inputSentence = ['/ip/pool/set']
	self.inputSentence.append('=ranges='+ range)
	self.inputSentence.append('=numbers='+ number)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def updatenetwork(self, address, gateway, number):
	self.inputSentence = ['/ip/dhcp-server/network/set']
	self.inputSentence.append('=address='+ address)
	self.inputSentence.append('=gateway='+ gateway)
	self.inputSentence.append('=numbers='+ number)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def updateserver(self, address, number):
	self.inputSentence = ['/ip/dhcp-server/set']
	self.inputSentence.append('=src-address='+ address)
	self.inputSentence.append('=numbers='+ number)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def updateDHCP(self):
	reply="no"
	while ( reply == "no"):
                print '1. Update Address Pool'
                print '2. Update Network'
                print '3. Update Server'
                print '4. Quit to main menu'
                reply2 = raw_input ('Task: ')

                if (reply2 == '1'):
                        self.updatepool()

                elif (reply2 == '2'):
                        self.updatenetwork()

                elif (reply2 == '3'):
                        self.updateserver()

                elif (reply2 == '4'):
                        main()

                else:
                        print 'incorrect Input'

                reply = raw_input ('Return to main menu?: ')

    def delDHCP(self):
        reply="no"
        while ( reply == "no"):
                print '1. Delete Address Pool'
                print '2. Delete Network'
                print '3. Delete Server'
                print '4. Quit to main menu'
                reply2 = raw_input ('Task: ')

                if (reply2 == '1'):
                        self.delpool()

                elif (reply2 == '2'):
                        self.delnetwork()

                elif (reply2 == '3'):
                        self.delserver()

                elif (reply2 == '4'):
                        main()

                else:
                        print 'incorrect Input'

                reply = raw_input ('Return to main menu?: ')

    def emptyline(self):
	self.inputSentence = ['']
	self.writeSentence(self.inputSentence)
	self.readSentence()

def main():
    #serverip = raw_input("What is your router ip: ")
    #loginid = raw_input("Login ID: ")
    #passwd = raw_input("Password: ")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.0.1.1", 8728))  
    apiros = ApiRos(s);             
    apiros.login("admin", "");

    if sys.argv[1] == "printpool":
	apiros.printpool();
	
    elif sys.argv[1] == "printnet":
	apiros.printnet();

    elif sys.argv[1] == "printserver":
	apiros.printserver();

    elif sys.argv[1] == "addpool":
	apiros.addpool(sys.argv[2], sys.argv[3]);

    elif sys.argv[1] == "addnetwork":
	apiros.addnetwork(sys.argv[2], sys.argv[3]);

    elif sys.argv[1] == "addserver":
	apiros.addserver(sys.argv[2], sys.argv[3]);

    elif sys.argv[1] == "updatepool":
	apiros.updatepool(sys.argv[2], sys.argv[3]);

    elif sys.argv[1] == "updatenetwork":
	apiros.updatenetwork(sys.argv[2], sys.argv[3], sys.argv[4]);

    elif sys.argv[1] == "updateserver":
	apiros.updateserver(sys.argv[2], sys.argv[3]);

    elif sys.argv[1] == "delpool":
	apiros.delpool(sys.argv[2]);

    elif sys.argv[1] == "delnetwork":
	apiros.delnetwork(sys.argv[2]);

    elif sys.argv[1] == "delserver":
	apiros.delserver(sys.argv[2]);
    
if __name__ == '__main__':
	main()

