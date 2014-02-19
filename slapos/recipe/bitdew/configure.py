##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os
import subprocess
import time
import sys
import socket
def putData(args):
  print "USE : python put.py serverIP inputname"
  host =args['host']
  #host ='196.203.126.15'
  protocol = args['protocol']
  file_name =args['file_name']
  bitdew=args['jar_file']
  java_bin=args['java_bin']
  data_dir=args['data_dir']
  package=args['package']
  try:
    os.chdir(package)
    #log=data_dir+'/put.log'
    #cmd=java_bin+"/java -jar "+bitdew+" --help >>"+log
    #os.system(cmd)
    log=data_dir+'/put.log'
    cmd=java_bin+"/java -cp bitdew.jar xtremweb.role.cmdline.CommandLineTool --protocol="+protocol+" --host="+host+" put "+file_name+" >>"+log
    os.system(cmd)
    print 'OKKKKKKKKKKKKKKKK'
    sys.exit(0)
  except Exception, e:
    print str(e)
    sys.exit(1)
def getData(args):
  print "USE : python put.py serverIP inputname"
  host =args['host']
  protocol = args['protocol']
  file_name =args['file_name']
  bitdew=args['jar_file']
  java_bin=args['java_bin']
  data_dir=args['data_dir']
  package=args['package']
  ID=args['ID']
  
  try:
    os.chdir(package)
    os.system('export CLASSPATH=bitdew.jar')
    log=data_dir+'/get.log'
    cmd=java_bin+"/java -cp "+bitdew+" xtremweb.role.cmdline.CommandLineTool --protocol="+protocol+" --host="+host+" get "+ID+" "+file_name+" >>"+log
    os.system(cmd)
    print 'OKKKKKKKKKKKKKKKK', host
    sys.exit(0)
  except Exception, e:
    print str(e)
    sys.exit(1)

def BitdewStart(args):
    """Start Bitdew Server """
    bitdew=args['jar_file']
    #bitdew='bitdew-stand-alone-1.2.0.jar'
    java_bin=args['java_bin']
    host=args['host']
    package=args['package']
    os.chdir(package)
    os.system('export CLASSPATH=bitdew.jar')
    #print(socket.gethostname()),'aaaaaaaaaaaaaaaaaaaaa'
    cmd=java_bin+"/java -jar "+bitdew+" --host="+host+" serv dc dt dr ds >>server.log"
    os.system(cmd)
    os.system('export CLASSPATH=bitdew.jar')
    
    
  
