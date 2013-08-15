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
  def install(self):
    path_list = []

    #generate script for start bitdew
    bitdew_server = self.options['server_script'].strip()
    python = self.options['python-bin'].strip()
    jar_file = self.options['server-jar'].strip()
    javabin=self.options['java-bin'].strip()
    wrapper = self.createPythonScript(self.options['wrapper'],
        'slapos.recipe.librecipe.execute.execute',
        ([python, bitdew_server,jar_file,javabin,
        ])
    )
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
    python = self.options['python-bin'].strip()
    jar_file = self.options['server-jar'].strip()
    package = self.options['package'].strip()
    javabin=self.options['java-bin'].strip()
    host=self.options['bitdew_host'].strip()
    protocol=self.options['protocol'].strip()
    datadir=self.options['data-dir'].strip()
    promise_put = self.options['promise_put'].strip()
    put_script=self.options['put_script'].strip()
    file = self.options['file-name'].strip()
    wrapperput = self.createPythonScript(promise_put,
        'slapos.recipe.librecipe.execute.execute',
        ([python,put_script,jar_file,javabin,host,protocol,file,datadir,package,
        ])
    )
    path_list.append(wrapperput)
    
    #generate wrapper for get input data from bitdew server cache
    (error,dataid)=commands.getstatusoutput('head '+datadir+'put.log'+' -n 1 | tail -1 | cut -f2 -d "[" | cut -f1 -d "]"')
    get_script =self.options['get_script'].strip()
    promise_get = self.options['promise_get'].strip()
    #id="fadr123443543"
    wrapperget = self.createPythonScript(promise_get,
        'slapos.recipe.librecipe.execute.execute',
        ([python,get_script,jar_file,javabin,host,protocol,'input-copy.txt',dataid,datadir,package,
        ])
    )
    
    path_list.append(wrapperget)
    return path_list