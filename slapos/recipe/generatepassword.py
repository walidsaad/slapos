# vim: set et sts=2:
##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
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

import errno
import os
import random
import string

def generatePassword(length):
  return ''.join(random.SystemRandom().sample(string.ascii_lowercase, length))


class Recipe(object):
  """Generate a password that is only composed of lowercase letters

    This recipe only makes sure that ${:passwd} does not end up in `.installed`
    file, which is world-readable by default. So be careful not to spread it
    throughout the buildout configuration by referencing it directly: see
    recipes like slapos.recipe.template:jinja2 to safely process the password.

    Options:
    - bytes: password length (default: 8 characters)
    - storage-path: plain-text persistent storage for password,
                    that can only be accessed by the user
      (default: ${buildout:parts-directory}/${:_buildout_section_name_})
  """

  def __init__(self, buildout, name, options):
    options_get = options.get
    try:
      self.storage_path = options['storage-path']
    except KeyError:
      self.storage_path = options['storage-path'] = os.path.join(
        buildout['buildout']['parts-directory'], name)
    try:
      with open(self.storage_path) as f:
        passwd = f.read()
    except IOError, e:
      if e.errno != errno.ENOENT:
        raise
      passwd = None
    if not passwd:
      passwd = self.generatePassword(int(options_get('bytes', '8')))
      self.update = self.install
    self.passwd = passwd
    # Password must not go into .installed file, for 2 reasons:
    # security of course but also to prevent buildout to always reinstall.
    options.get = lambda option, *args, **kw: passwd \
      if option == 'passwd' else options_get(option, *args, **kw)

  generatePassword = staticmethod(generatePassword)

  def install(self):
    if self.storage_path:
      try:
        os.unlink(self.storage_path)
      except OSError, e:
        if e.errno != errno.ENOENT:
          raise
      fd = os.open(self.storage_path,
        os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0600)
      try:
        os.write(fd, self.passwd)
      finally:
        os.close(fd)
    return self.storage_path

  def update(self):
    return ()
