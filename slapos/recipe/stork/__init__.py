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
  """Deploy a fully operational condor architecture."""

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

  def _options(self, options):
    #Path of stork compiled package
    self.package = options['package'].strip()
    self.rootdir = options['rootdirectory'].strip()
    #Other stork dependances
    self.javabin = options['java-bin'].strip()
    self.dash = options['dash'].strip()
    #Directory to deploy stork
    self.prefix = options['rootdirectory'].strip()
    self.wrapperdir = options['wrapper-dir'].strip()
    self.wrapper = options['local-dir'].strip()
    self.wrapper_bin = options['bin'].strip()
    self.wrapper_sbin = options['sbin'].strip()
    self.wrapper_log= options['log'].strip()
    self.wrapper_tmp= options['tmp'].strip()
    self.ipv6 = options['ip'].strip()
    self.stork_host = options['stork_host'].strip()
    self.stork_port = options['stork_port'].strip()

  def install(self):
    path_list = []
    #get UID and GID for current slapuser
    stat_info = os.stat(self.rootdir)
    slapuser = str(stat_info.st_uid)+"."+str(stat_info.st_gid)
    domain_name = 'slapos%s.com' % stat_info.st_uid


    #Generate stork_config file
    stork_config = os.path.join(self.rootdir, 'etc/stork_config')
    stork_configure = dict(stork_host=self.stork_host, releasedir=self.wrapper,
                  storkpackage=self.package,
                  slapuser=slapuser, ipv6=self.ipv6)
    destination = os.path.join(stork_config)
    config = self.createFile(destination,
      self.substituteTemplate(self.getTemplateFilename('stork_config.generic'),
      stork_configure))
    path_list.append(config)

    #create stork binary launcher for slapos
    if not os.path.exists(self.wrapper_bin):
      os.makedirs(self.wrapper_bin, int('0744', 8))
    if not os.path.exists(self.wrapper_sbin):
      os.makedirs(self.wrapper_sbin, int('0744', 8))
    if not os.path.exists(self.wrapper_log):
      os.makedirs(self.wrapper_log, int('0744', 8))
    if not os.path.exists(self.wrapper_tmp):
      os.makedirs(self.wrapper_tmp, int('0744', 8))
    #generate script for each file in prefix/bin
    for binary in os.listdir(self.package+'/bin'):
      wrapper_location = os.path.join(self.wrapper_bin, binary)
      current_exe = os.path.join(self.package, 'bin', binary)
      wrapper = open(wrapper_location, 'w')
      content = """#!%s
      export LD_LIBRARY_PATH=%s
      export PATH=%s
      export STORK_CONFIG=%s
      export STORK_HOME=%s
      export STORK_IDS=%s
      export HOSTNAME=%s
      exec %s $*""" % (self.dash,
              self.environ['LD_LIBRARY_PATH'], self.environ['PATH'],
              stork_config, self.prefix, slapuser,
              self.environ['HOSTNAME'], current_exe)
      wrapper.write(content)
      wrapper.close()
      path_list.append(wrapper_location)
      os.chmod(wrapper_location, 0744)

    #generate script for each file in prefix/sbin
    for binary in os.listdir(self.package+'/sbin'):
      wrapper_location = os.path.join(self.wrapper_sbin, binary)
      current_exe = os.path.join(self.package, 'sbin', binary)
      wrapper = open(wrapper_location, 'w')
      content = """#!%s
      export LD_LIBRARY_PATH=%s
      export PATH=%s
      export STORK_CONFIG=%s
      export STORK_HOME=%s
      export STORK_IDS=%s
      export HOSTNAME=%s
      exec %s $*""" % (self.dash,
              self.environ['LD_LIBRARY_PATH'], self.environ['PATH'],
              stork_config, self.prefix, slapuser,
              self.environ['HOSTNAME'], current_exe)
      wrapper.write(content)
      wrapper.close()
      path_list.append(wrapper_location)
      os.chmod(wrapper_location, 0744)

    #generate script for start stork
    start_stork = os.path.join(self.wrapperdir, 'start_stork')
    start_bin = os.path.join(self.wrapper_sbin, 'stork_server')
    wrapper = self.createPythonScript(start_stork,
        '%s.configure.storkStart' % __name__,
        dict(start_bin=start_bin,port=self.stork_port,configfile=self.rootdir+'/etc/stork_config')
    )
    path_list.append(wrapper)
    return path_list

class AppSubmit(GenericBaseRecipe):
  """Submit a stork job into an existing Stork server instance"""

  def download(self, url, filename=None, md5sum=None):
    cache = os.path.join(self.options['rootdirectory'].strip(), 'tmp')
    if not os.path.exists(cache):
      os.mkdir(cache)
    downloader = zc.buildout.download.Download(self.buildout['buildout'],
                    hash_name=True, cache=cache)
    path, _ = downloader(url, md5sum)
    if filename:
      name = os.path.join(cache, filename)
      os.rename(path, name)
      return name
    return path

  def copy_file(self, source, dest):
    """"Copy file with source to dest with auto replace
        return True if file has been copied and dest ha been replaced
    """
    result = False
    if source and os.path.exists(source):
      if os.path.exists(dest):
        if filecmp.cmp(dest, source):
          return False
        os.unlink(dest)
      result = True
      shutil.copy(source, dest)
    return result

  def getFiles(self):
    """This is used to download app files if necessary and update options values"""
    app_list = json.loads(self.options['stork-app-list'])
    if not app_list:
      return None
    for app in app_list:
      if app_list[app].get('files', None):
        file_list = app_list[app]['files']
        for file in file_list:
          if file and (file.startswith('http') or file.startswith('ftp')):
            file_list[file] = self.download(file_list[file])
          os.chmod(file_list[file], 0600)
      else:
        app_list[app]['files'] = {}

      submit_file = app_list[app].get('description-file', '')
      if submit_file and (submit_file.startswith('http') or submit_file.startswith('ftp')):
        app_list[app]['description-file'] = self.download(submit_file, 'submit-dap')
        os.chmod(app_list[app]['description-file'], 0600)

    return app_list

  def install(self):
    path_list = []
    #check if curent stork instance is an stork server
    if self.options['machine-role'].strip() != "server":
      raise Exception("Cannot submit a job to stork client instance")

    #Setup directory
    datadir = self.options['data-dir'].strip()
    if not os.path.exists(datadir):
      os.mkdir(datadir)
    app_list = self.getFiles()
    for appname in app_list:
      appdir = os.path.join(datadir, appname)
      if not os.path.exists(appdir):
        os.mkdir(appdir)
      submitfile = os.path.join(appdir, 'submit-dap')
  
      install = self.copy_file(app_list[appname]['description-file'], submitfile)
      sig_install = os.path.join(appdir, '.install')
      if install:
        with open(sig_install, 'w') as f:
          f.write('to_install')
      for file in app_list[appname]['files']:
        destination = os.path.join(appdir, file)
        if os.path.exists(destination):
          os.unlink(destination)
        os.symlink(app_list[appname]['files'][file], destination)
      #generate wrapper for submitting stork job
      #self.stork_host = self.options['stork_host'].strip()
      self.stork_host = self.options['ip'].strip()
      self.stork_port = self.options['stork_port'].strip()
      stork_submit = os.path.join(self.options['bin'].strip(), 'stork_submit')
        #change default SRC and DEST URLs by user URLs
      (error,success)=commands.getstatusoutput('sed -i "s#REPLACE WITH USER REPOSITORY URL#'+self.options['src_url'].strip()+'#" '+datadir+'stork_test/submit-dap')
      (error,success)=commands.getstatusoutput('sed -i "s#REPLACE WITH BONJOURGRID DATA REPOSITORY URL#'+'file:'+datadir+''+self.options['data_package'].strip()+'#" '+datadir+'stork_test/submit-dap')
      parameter = dict(submit=stork_submit, sig_install=sig_install,
                      submit_file=submitfile,
                      stork_server=self.stork_host,
                      server_port=self.stork_port,
                      appname=appname, appdir=appdir)
      submit_job = self.createPythonScript(
        os.path.join(self.options['wrapper-dir'].strip(), appname),
        '%s.configure.submitJob' % __name__, parameter
      )
      path_list.append(submit_job)
    return path_list