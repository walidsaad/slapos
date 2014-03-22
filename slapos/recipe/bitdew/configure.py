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
import datetime
import sys
import socket
import commands
def putData(args):
  print "USE : python put.py serverIP inputname"
  host =args['host']
  protocol = args['protocol']
  file_name =args['file_name']
  bitdew=args['jar_file']
  java_bin=args['java_bin']
  data_dir=args['data_dir']
  package=args['package']
  try:
    os.chdir(package)
    print 'BEGIN PUT',datetime.datetime.now();
    os.environ['CLASSPATH'] =bitdew
    print os.environ['CLASSPATH']
    ########log=data_dir+'/put.log'
    log='/tmp/put.log'
    cmd=java_bin+"/java -cp "+bitdew+" xtremweb.role.cmdline.CommandLineTool --protocol="+protocol+" --host="+host+" put "+file_name+" >>"+log
    cmd1="echo "+host+" >>/tmp/server"
    os.system(cmd1)
    time.sleep(20)
    os.system(cmd)
    print 'END PUT',datetime.datetime.now();
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
  dataid=args['dataid']
  print 'BEGIN GET',datetime.datetime.now();
  try:
    #os.chdir(package)
    os.environ['CLASSPATH'] =bitdew
    log=data_dir+'/get.log'
    time.sleep(10)
    #(error,dataid)=commands.getstatusoutput('head '+data_dir+'put.log'+' -n 1 | tail -1 | cut -f3 -d "[" | cut -f1 -d "]"')
    cmd=java_bin+"/java -cp "+bitdew+" xtremweb.role.cmdline.CommandLineTool --protocol="+protocol+" --host="+host+" get "+dataid+" >>"+log
    os.system(cmd)
    print 'END GET', datetime.datetime.now();
    sys.exit(0)
  except Exception, e:
    print str(e)
    sys.exit(1)

def BitdewStart(args):
    print 'Start Bitdew Server',datetime.datetime.now();
    bitdew=args['jar_file']
    java_bin=args['java_bin']
    host=args['host']
    package=args['package']
    #os.chdir(package)
    os.system('export CLASSPATH='+bitdew)
    os.environ['CLASSPATH'] =bitdew
    print os.environ['CLASSPATH']
    cmd=java_bin+"/java -jar "+bitdew+" --host="+host+" serv dc dt dr ds"
    os.system(cmd)
    print 'END Bitdew Server',datetime.datetime.now();
