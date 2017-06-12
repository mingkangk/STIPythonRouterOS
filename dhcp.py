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

    def printdhcpcount(self):
	global b
	self.inputSentence = ['/ip/dhcp-server/print']
	self.inputSentence.append('=count-only=')
	self.writeSentence(self.inputSentence)
	count = self.readSentence()
	for letters in count:
		if "=ret=" in letters:
			b = letters;

	counts = b[5]
	return counts

    def addpool(self):
	name = raw_input('Pool Name: ')
	range = raw_input('Pool Range: ')
	self.inputSentence = ['/ip/pool/add']
        self.inputSentence.append('=name='+ name)
        self.inputSentence.append('=ranges='+ range)
        self.writeSentence(self.inputSentence)
        self.readSentence()    

    def addnetwork(self):
	subnet = raw_input('Network Address(with mask): ')
	ipaddr = raw_input('Gateway: ')
	self.inputSentence = ['/ip/dhcp-server/network/add']
        self.inputSentence.append('=address='+ subnet)
        self.inputSentence.append('=gateway='+ ipaddr)
        self.writeSentence(self.inputSentence)
        self.readSentence()

    def addserver(self):
	interface = raw_input('Interface: ')
	name = raw_input('Pool Name: ')
	self.inputSentence = ['/ip/dhcp-server/add']
	self.inputSentence.append('=interface=' + interface)
	self.inputSentence.append('=address-pool=' + name)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delpool(self):
	ans = raw_input ('Which pool would you like to delete?: ')

	self.inputSentence = ['/ip/pool/remove']
	self.inputSentence.append('=numbers='+ ans)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delnetwork(self):
	ans = raw_input ('Network Number: ')
	self.inputSentence = ['/ip/dhcp-server/network/remove']
	self.inputSentence.append('=numbers='+ ans)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def delserver(self):
	ans = raw_input('DHCP Number: ')

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

    def updatepool(self):

	range = raw_input('New Address Range: ')
	number = raw_input('Number: ')

	self.inputSentence = ['/ip/pool/set']
	self.inputSentence.append('=ranges='+ range)
	self.inputSentence.append('=numbers='+ number)
	self.writeSentence(self.inputSentence)
	self.readSentence()

    def updatenetwork(self):
	address = raw_input('Network Address: ')
	gateway = raw_input('Gateway: ')
	dns = raw_input('DNS Address: ')

	self.inputSentence = ['/ip/dhcp-server/network']
	self.inputSentence.append('=address='+ address)
	self.inputSentence.append('=gateway='+ gateway)
	self.inputSentence.append('=dns='+ dns)

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

    ans = "yes"
    counts = apiros.printdhcpcount()

    while (ans == "yes"):
	
	print "1. Print all DHCP"
        print "2. Add DHCP"
        print "3. Edit a DHCP"
        print "4. Delete a DHCP"
        print "5. Quit"
        ans2 = raw_input ("What would you like to do: ")
	
	
	if (ans2 == "1"):
		count = apiros.printdhcpcount()
		if (isinstance(int(count), int)):
			count = int(count)
			count = count+2
			while count != 0:
			
				inputsentence = ['/ip/dhcp-server/print'];
				r = select.select([s, sys.stdin], [], [], None)
				if s in r[0]:
					x = apiros.readSentence()

				if sys.stdin in r[0]:
					l = sys.stdin.readline()
					l = l[:-1]
					if l == '':
						apiros.writeSentence(inputsentence)
						inputsentence = []
					else:
						inputsentence.append(l)
				count = count-1;
		else:
			print "not integer"

        elif (ans2 == "2"):
		 	
    		apiros.addDHCP();

	elif (ans2 == "3"):

    		apiros.updateip();

    		apiros.emptyline();
	
	elif (ans2 == "4"):

    		apiros.delDHCP();

	else:

		print "Input is incorrect";
	
	ans = raw_input ("Do you want to continue?")

if __name__ == '__main__':
	main()
