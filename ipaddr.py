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

    def printipcount(self):
	global b
	self.inputSentence = ['/ip/address/print']
	self.inputSentence.append('=count-only=')
	self.writeSentence(self.inputSentence)
	count = self.readSentence()
	for letters in count:
		if "=ret=" in letters:
			b = letters;

	counts = b[5]
	number = int(counts)
	if (isinstance(number,int)):
		return number
	else:
		return b
    
    def createip(self, ip, interface):
	self.inputSentence = ['/ip/address/add']
	self.inputSentence.append('=address='+ ip)
	self.inputSentence.append('=interface='+ interface)
	self.writeSentence(self.inputSentence)
	self.readSentence()
    
    def updateip(self):
	newerip = raw_input("Enter new ip with subnet mask: ")
	number = raw_input("Numbers: ")
	
	self.inputSentence = ['/ip/address/set']
	self.inputSentence.append('=numbers=' + number)
	self.inputSentence.append('=address=' + newerip)
   	self.writeSentence(self.inputSentence)
	self.readSentence()

    def deleteip(self):
        number = raw_input("Delete Number: ")	
	self.inputSentence =['/ip/address/remove']
	self.inputSentence.append('=numbers='+ number)
	self.writeSentence(self.inputSentence)
	self.readSentence()

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
    counts = apiros.printipcount()

    while (ans == "yes"):
	
	print "1. Print all IP"
        print "2. Add an IP"
        print "3. Edit a IP"
        print "4. Delete a IP"
        print "5. Quit"
        ans2 = raw_input ("What would you like to do: ")
	
	
	if (ans2 == "1"):
		count = apiros.printipcount()
		if (isinstance(count, int)):
			count = count+2
			while count != 0:
			
				inputsentence = ['/ip/address/print'];
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

   		newip = raw_input("IP to add: ");
    		newipinterface = raw_input("Interface: "); 	
    		apiros.createip(newip,newipinterface);

	elif (ans2 == "3"):

    		apiros.updateip();

    		apiros.emptyline();
	
	elif (ans2 == "4"):

    		apiros.deleteip();

	else:

		print "Input is incorrect";
	
	ans = raw_input ("Do you want to continue?")

if __name__ == '__main__':
	main()
