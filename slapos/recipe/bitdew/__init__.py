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
from slapos.recipe.librecipe import GenericBaseRecipe
import os
import subprocess
import zc.buildout
import filecmp
import urlparse
import shutil
import re
import json
import commands

class Recipe(GenericBaseRecipe):
  """Deploy a Bitdew Server."""
  def __init__(self, buildout, name, options):
    self.environ = {}
    self.role = ''
    environment_section = options.get('environment-section', '').strip()
    if environment_section and environment_section in buildout:
      # Use environment variables from the designated config section.
      self.environ.update(buildout[environment_section])
    for variable in options.get('environment', '').splitlines():
      if variable.strip():
        try:
          key, value = variable.split('=', 1)
          self.environ[key.strip()] = value
        except ValueError:
          raise zc.buildout.UserError('Invalid environment variable definition: %s', variable)
    # Extrapolate the environment variables using values from the current
    # environment.
    for key in self.environ:
      self.environ[key] = self.environ[key] % os.environ
    return GenericBaseRecipe.__init__(self, buildout, name, options)
    
  def install(self):
    path_list = []
    #get UID and GID for current slapuser
    stat_info = os.stat(self.options['rootdirectory'].strip())
    slapuser = str(stat_info.st_uid)+"."+str(stat_info.st_gid)
    #create bitdew binary launcher for slapos
    if not os.path.exists(self.options['wrapper']):
      os.makedirs(self.options['wrapper'], int('0744', 8))
    
    
    
    
    #generate script for start bitdew
    
    start_bitdew = os.path.join(self.options['wrapper-dir'], 'start_bitdew')
    jar_file = self.options['server-jar'].strip()
    #jar_file = os.path.join(self.options['wrapper'], 'bitdew.jar')
    javabin=self.options['java-bin'].strip()
    wrapper = self.createPythonScript(start_bitdew,
        '%s.configure.BitdewStart' % __name__,
        dict(jar_file=jar_file,java_bin=javabin,host=self.options['ip'].strip(),configfile=javabin+'/etc/proprietes.json',package=self.options['package'].strip()))
    path_list.append(wrapper)
    return path_list
    
class AppSubmit(GenericBaseRecipe):
  """Client Put and Get into an existing Bitdew server instance"""
  def install(self):
    path_list = []
    #create bitdew client put and get directories

    if not os.path.exists(self.options['data-dir']):
      os.makedirs(self.options['data-dir'], int('0744', 8))
    #generate wrapper for put input data into bitdew server cache
    

    jar_file = self.options['server-jar'].strip()
    #jar_file = os.path.join(self.options['wrapper'], 'bitdew.jar')
    
    package = self.options['package'].strip()
    javabin=self.options['java-bin'].strip()
    host=self.options['ip'].strip()
    protocol=self.options['protocol'].strip()
    datadir=self.options['data-dir'].strip()
    
    put_data=os.path.join(self.options['wrapper-dir'], 'share_data')
    file = self.options['file-name'].strip()
    parameter = dict(jar_file=jar_file, package=package,
                      java_bin=javabin,
                      host=host,
                      protocol=protocol,
                      file_name=file, data_dir=datadir)
    wrapperput = self.createPythonScript(put_data,
        '%s.configure.putData' % __name__, parameter
      )
    path_list.append(wrapperput)
    
    
    #generate wrapper for get input data from bitdew server cache
    (error,dataid)=commands.getstatusoutput('head '+datadir+'put.log'+' -n 1 | tail -1 | cut -f2 -d "[" | cut -f1 -d "]"')
    get_data=os.path.join(self.options['wrapper-dir'], 'get_data')
    #id="fadr123443543"
    parameter = dict(jar_file=jar_file, package=package,
                      java_bin=javabin,
                      host=host,
                      protocol=protocol,
                      file_name='input-copy.txt',ID=dataid, data_dir=datadir)
    wrapperget = self.createPythonScript(get_data,
        '%s.configure.getData' % __name__, parameter
      )
  
    path_list.append(wrapperget)
    return path_list
    
