# multirate class for interpolation and decimation 
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 03.11.2017 17:44
import numpy as np
import scipy.signal as sig
import tempfile
import subprocess
#import shlex
#import time

from refptr import *
from thesdk import *

#function for factoring integers
def factor(argdict={'n':1}):
    #This is a function to calculate factors of an integer as in Matlab
    # "Everything in Matlab is available in Python" =False.
    reminder=argdict['n']
    factors=np.array([])
    while reminder >1:
        notfound=True
        for i in range(2,int(np.sqrt(reminder)+2)):
            if reminder % i == 0:
                factors=np.r_[ factors, i]
                reminder=reminder/i
                notfound=False
                break
        if notfound==True:
                factors=np.r_[ factors, reminder]
                reminder=0
    return factors


def generate_interpolation_filterlist(argdict={'interp_factor':1}):
    #Use argument dictionary. Makes modifications easier.
    interp_factor=argdict['interp_factor']
    
    attenuation=70 #Desired attenuation in decibels
    factors=factor({'n':interp_factor})
    #print(factors)
    fsample=1
    BW=0.45
    numtaps=65     # TAps for the first filterThis should be somehow verified
    #Harris rule. This is to control stability of Rmez
    #numtaps= int(np.ceil(attenuation*fsample*factors[0]/(fsample/2-BW)))    # TAps for the first filterThis should be somehow verified
    desired=np.array([ 1, 10**(-attenuation/10)] )
    #check the mask specs from standard 
    #mask=np.array([ 1, 10**(-28/10)    ] )
    filterlist=list()
    if interp_factor >1:
        for i in factors:
            fact=i
            #print(fsample)
            if  fsample/(0.5)<= 8: #FIR is needed
                msg= "BW to sample rate ratio is now %s" %(fsample/0.5)
                #self.print_log(type='I', msg=msg )
                msg="Interpolation by %i" %(fact)
                #thesdk.print_log({'type': 'I', 'msg':msg })
                bands=np.array([0, BW, (fsample*fact/2-BW), fact*fsample/2])
                filterlist.append(sig.remez(numtaps, bands, desired, Hz=fact*fsample))
                fsample=fsample*fact #increase the sample frequency
                numtaps=np.amax([3, int(np.floor(numtaps/fact)) + int((np.floor(numtaps/fact)%2-1))]) 
            else:
                msg="BW to sample rate ratio is now %s" %(fsample/0.5)
                #thesdk.print_log({'type': 'I', 'msg':msg })
                #print("BW to sample rate ratio is now %s" %(fsample/0.5))
                fact=fnc.reduce(lambda x,y:x*y,factors)/fsample
                print("Interpolation with 3-stage CIC-filter by %i" %(fact))
                fircoeffs=np.ones(int(fact))/(fact) #do the rest of the interpolation with 3-stage CIC-filter
                fircoeffs=fnc.reduce(lambda x,y: np.convolve(x,y),list([fircoeffs, fircoeffs, fircoeffs]))
                filterlist.append(fircoeffs)
                #print(filterlist)
                fsample=fsample*fact #increase the sample frequency
                print("BW to sample rate ratio is now %s" %(fsample/0.5))
                break
    else:
        print("Interpolation ratio is 1. Generated unit coefficient")
        filterlist.append([1.0]) #Ensure correct operation in unexpected situations.
    return filterlist


class multirate(thesdk):
    pass    
#def __init__(self,*arg): 
#    self.proplist = [ 'Rs' ];    #properties that can be propagated from parent
#    self.Rs = 1;                 # sampling frequency
#    self.iptr_A = IO();
#    self.model='py';             #can be set externally, but is not propagated
#    self._Z = IO();
#    self._classfile=__file__
#    if len(arg)>=1:
#        parent=arg[0]
#        self.copy_propval(parent,self.proplist)
#        self.parent =parent;
#def init(self):
#    self.def_rtl()
#    rndpart=os.path.basename(tempfile.mkstemp()[1])
#    self._infile=self._rtlsimpath +'/A_' + rndpart +'.txt'
#    self._outfile=self._rtlsimpath +'/Z_' + rndpart +'.txt'
#    self._rtlcmd=self.get_rtlcmd()
#
#def get_rtlcmd(self):
#    #the could be gathered to rtl class in some way but they are now here for clarity
#    submission = ' bsub -q normal '  
#    rtllibcmd =  'vlib ' +  self._workpath + ' && sleep 2'
#    rtllibmapcmd = 'vmap work ' + self._workpath
#
#    if (self.model is 'vhdl'):
#        rtlcompcmd = ( 'vcom ' + self._rtlsrcpath + '/' + self._name + '.vhd '
#                      + self._rtlsrcpath + '/tb_'+ self._name+ '.vhd' )
#        rtlsimcmd =  ( 'vsim -64 -batch -t 1ps -g g_infile=' + 
#                       self._infile + ' -g g_outfile=' + self._outfile 
#                       + ' work.tb_' + self._name + ' -do "run -all; quit -f;"')
#        rtlcmd =  submission + rtllibcmd  +  ' && ' + rtllibmapcmd + ' && ' + rtlcompcmd +  ' && ' + rtlsimcmd
#
#    elif (self.model is 'sv'):
#        rtlcompcmd = ( 'vlog -work work ' + self._rtlsrcpath + '/' + self._name + '.sv '
#                       + self._rtlsrcpath + '/tb_' + self._name +'.sv')
#        rtlsimcmd = ( 'vsim -64 -batch -t 1ps -voptargs=+acc -g g_infile=' + self._infile
#                      + ' -g g_outfile=' + self._outfile + ' work.tb_' + self._name  + ' -do "run -all; quit;"')
#
#        rtlcmd =  submission + rtllibcmd  +  ' && ' + rtllibmapcmd + ' && ' + rtlcompcmd +  ' && ' + rtlsimcmd
#
#    else:
#        rtlcmd=[]
#    return rtlcmd
#
#def run(self,*arg):
#    if len(arg)>0:
#        par=True      #flag for parallel processing
#        queue=arg[0]  #multiprocessing.Queue as the first argument
#    else:
#        par=False
#
#    if self.model=='py':
#        out=np.array(self.iptr_A.Data)
#        if par:
#            queue.put(out)
#        self._Z.Data=out
#    else: 
#      try:
#          os.remove(self._infile)
#      except:
#          pass
#      fid=open(self._infile,'wb')
#      np.savetxt(fid,np.transpose(self.iptr_A.Data),fmt='%.0f')
#      #np.savetxt(fid,np.transpose(inp),fmt='%.0f')
#      fid.close()
#      while not os.path.isfile(self._infile):
#          #print("Wait infile to appear")
#          time.sleep(1)
#      try:
#          os.remove(self._outfile)
#      except:
#          pass
#      print("Running external command \n", self._rtlcmd , "\n" )
#      subprocess.call(shlex.split(self._rtlcmd));
#      
#      while not os.path.isfile(self._outfile):
#          #print("Wait outfile to appear")
#          time.sleep(1)
#      fid=open(self._outfile,'r')
#      #fid=open(self._infile,'r')
#      #out = .np.loadtxt(fid)
#      out = np.transpose(np.loadtxt(fid))
#      fid.close()
#      if par:
#          queue.put(out)
#      self._Z.Data=out
#      os.remove(self._infile)
#      os.remove(self._outfile)

