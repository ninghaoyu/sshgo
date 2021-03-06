# -*- coding: UTF-8 -*-
import yaml,getpass
import pexpect,socket
import os,signal,re,os
import struct, fcntl, termios, sys
try:
    import json
except ImportError:
    import simplejson as json

#*************************************************************************#

class parseConfig():

    def __init__(self,configfile):
        self.__key = 19
        self.__configfile = None
        self._userInfo = dict()
        self.__configfile = configfile

    def getUserPasswd(self,user):
        cfstream = open(self.__configfile,'r')
        self._userInfo= yaml.load(cfstream)
        cfstream.close()
        #print('I am here',self.__show(self._userInfo[user].encode('utf-8')))
        #print('I am here',self.__show(self._userInfo[user]))
        #return  self.__show(self._userInfo[user].encode('utf-8'))
        return  self.__show(self._userInfo[user])

    def overWriteConfig(self):
            outfile=open(self.__configfile, 'w+') 
            try:
                #yaml.dump(self._userInfo, outfile, default_flow_style=False,allow_unicode = True, encoding = 'utf-8')
                yaml.dump(self._userInfo, outfile, default_flow_style=False)
            except Exception as e:
                print(e)
                print("file write error")
                outfile.close()
                return False

            outfile.close()
            return True

    def encrypt(self,s): 
        b = bytearray(str(s).encode("gbk")) 
        n = len(b) # 求出 b 的字节数 
        c = bytearray(n*2) 
        j = 0 
        for i in range(0, n): 
            b1 = b[i] 
            b2 = b1 ^ self.__key # b1 = b2^ key 
            c1 = b2 % 16 
            c2 = b2 // 16 # b2 = c2*16 + c1 
            c1 = c1 + 65 
            c2 = c2 + 65 # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码 
            c[j] = c1 
            c[j+1] = c2 
            j = j+2 
        return c.decode("gbk") 

 
    def __show(self, s): 
        c = bytearray(str(s).encode("gbk"))
        n = len(c) # 计算 b 的字节数 
        if n % 2 != 0 : 
            return "" 
        n = n // 2 
        b = bytearray(n) 
        j = 0 
        for i in range(0, n): 
            c1 = c[j] 
            c2 = c[j+1] 
            j = j+2 
            c1 = c1 - 65 
            c2 = c2 - 65 
            b2 = c2*16 + c1 
            b1 = b2^ self.__key 
            b[i]= b1 
        try: 
            return b.decode("gbk") 
        except: 
            return "failed" 
 



#*************************************************************************#

class Message():
    __HEADER = '\033[95m'
    __OKBLUE = '\033[94m'
    __OKGREEN = '\033[92m'
    __WARNING = '\033[93m'
    __FAIL = '\033[91m'
    __ENDC = '\033[0m'
    __BOLD = '\033[1m'
    __UNDERLINE = '\033[4m'
    def __init__(self):
        pass

    def Warning(self,msg):
        return self.__WARNING+msg+self.__ENDC

    def Failed(self,msg):
        return self.__FAIL+msg+self.__ENDC

    def UnderLine(self,msg):
        return self.__UNDERLINE+msg+self.__ENDC

    def OkBlue(self,msg):
        return self.__OKBLUE+msg+self.__ENDC

    def OkGreen(self,msg):
        return self.__OKGREEN+msg+self.__ENDC

    def Bold(self,msg):
        return self.__BOLD+msg+self.__ENDC

    def Header(self,msg):
        return self.__HEADER+msg+self.__ENDC


#*************************************************************************#
class AutoSSH():

    def __init__(self,hostname,sshuser,configfile,sshport,suUser=None,jumphost=None,jumphostsshport=22,identity_file=None,sshbin='/usr/bin/ssh'):

        self.__sshoptions = ''
        self.__hostname= hostname
        self.__sshjumphost = jumphost
        self.__identity_file = identity_file
        if identity_file != None:
            self.__sshoptions += ' -i ' + identity_file
        self.__sshbin = sshbin
        self.__sshport=sshport
        self.__nosshport = re.compile(str.encode('.*port %s: Connection refused.*' % self.__sshport))
        self.__sshtimeout = re.compile(str.encode('.*port %s: Connection timed out.*' % self.__sshport))
        self.__sudoprompt = '::::'
        self.__userprompt = re.compile(str.encode('.*[\$>%#] $'))
        self.__passwdprompt = re.compile(str.encode('assword: *$'))
        if self.__sshjumphost == None:
            self.__sshoptions += ' -o VerifyHostKeyDNS=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
            self.__useJumpHost = False
        else:
            self.__sshoptions += ' -o ProxyCommand="' \
                + self.__sshbin + ' -o VerifyHostKeyDNS=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p ' \
                + self.__sshjumphost \
                + ' -p %s " -o VerifyHostKeyDNS=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ' % jumphostsshport

            self.__useJumpHost = True

        self._msg = Message()

        ''' check ssh jump host reslove and target ssh host reslove '''
        if self.__useJumpHost :
            if self.hostname_resolves(self.__sshjumphost) == False:
                raise Exception(self._msg.Warning('The ssh jump hostname "%s" is not resolve!!!' % self.__sshjumphost))

        if self.hostname_resolves(self.__hostname) == False:
            raise Exception(self._msg.Warning('The hostname "%s" is not resolve!!!' % self.__hostname))


        ''' parse config file get user password '''
        self.__sshpassword = parseConfig(configfile).getUserPasswd(sshuser)
        #print("----->",self.__sshpassword)
        if self.__sshpassword == None:
            raise Exception(self._msg.Failed('The file %s is not find or config was error!' % configfile))

        #self.__SSH = 'ssh -o VerifyHostKeyDNS=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p %s -t -l %s %s' % (self.__sshport,sshuser,hostname)
        self.__SSH = self.__sshbin + self.__sshoptions + ' -p %s -t -l %s %s' % (self.__sshport,sshuser,hostname)
        if suUser != None:
            self.__SSH += " sudo -p '%s' su %s" % (self.__sudoprompt,suUser)

        self.__sshlogin()

    def _resizeWin(self,sig,data):
        self.__setWinSize()

    def __setWinSize(self):
        #get local terminal winsize
        rows, cols = map(int, os.popen('stty size', 'r').read().split())
        #set remote expect terminal window size
        self._sshobj.setwinsize(rows, cols)

    def hostname_resolves(self,hostname):
        isIP = re.compile('\d+.\d+.\d+.\d+')
        if isIP.match(hostname) == False:
            return True

        try:
            socket.gethostbyname(hostname)
            return True
        except socket.error:
            return False


    def json_format_dict(self, data, pretty=False):
        ''' Converts a dict to a JSON object and dumps it as a formatted
        string '''

        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data)


    def __sshlogin(self):
        try:

            self._sshobj = pexpect.spawn(self.__SSH)
            self.__setWinSize()
            ''' when use ssh jump host to connect remote target host, login in jump host first '''
            if self.__useJumpHost:
                spawnJumpHost = self._sshobj.expect([self.__sshtimeout,self.__nosshport,self.__passwdprompt])
                if spawnJumpHost == 0:
                    raise Exception(self._msg.Failed("jump ssh host port %s time out!" % self.__sshport))
                elif spawnJumpHost == 1:
                    raise Exception(self._msg.Failed("jump host no SSH port %s opened !" % self.__sshport))
                elif spawnJumpHost == 2:
                    self._sshobj.sendline(self.__sshpassword)

            ''' ssh remote target host, login now '''
            sshspawnstatus = self._sshobj.expect([self.__sshtimeout,self.__nosshport,self.__passwdprompt])
            if sshspawnstatus == 0:
                raise Exception(self._msg.Failed("ssh port %s time out!" % self.__sshport))
            elif sshspawnstatus == 1:
                raise Exception(self._msg.Failed("no SSH port %s opened !" % self.__sshport))
            elif sshspawnstatus == 2:
                self._sshobj.sendline(self.__sshpassword)

            #print(self._sshobj.before.decode("utf-8"))
            print(self._sshobj.before.decode()+self._sshobj.after.decode())


            ''' when logined target host,if use sudo user to do soming '''

            login =  self._sshobj.expect([self.__userprompt,self.__passwdprompt,self.__sudoprompt,pexpect.EOF,pexpect.TIMEOUT])
            if login == 0: #not use sudo user
                pass
            elif login == 1 : # no sudo
                raise Exception(self._msg.Failed("Bad password"))
            elif login == 2 : #type sudo password
                self._sshobj.sendline(self.__sshpassword)
                j = self._sshobj.expect([self.__userprompt])
                if j != 0:
                    raise Exception(self._msg.Failed("sudo Failed"))
            elif login == 3 :
                #print(self._sshobj.before.decode("utf-8"))
                print(self._sshobj.before+self._sshobj.after)

        except Exception as e:
            print(self._msg.Failed("ssh failed on login."))
            print(e)

    def sshInteract(self):
        #self._sshobj.sendline('\n')
        self._sshobj.sendline('uptime')
        self._sshobj.interact()

