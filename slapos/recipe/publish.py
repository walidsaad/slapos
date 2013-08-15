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
import zc.buildout
from slapos.recipe.librecipe import wrap
from slapos.recipe.librecipe import GenericSlapRecipe

CONNECTION_PARAMETER_STRING = 'connection-'

class Recipe(GenericSlapRecipe):
  def _install(self):
    publish_dict = dict()
    options = self.options.copy()
    del options['recipe']
    slave_reference = options.pop('-slave-reference', None)
    for k, v in options.iteritems():
      if k[:1] == '-':
        continue
      publish_dict[k] = v
    self._setConnectionDict(publish_dict, slave_reference)
    return []

  def _setConnectionDict(self, publish_dict, slave_reference=None):
    return self.setConnectionDict(publish_dict, slave_reference)

SERIALISED_MAGIC_KEY = '_'

class Serialised(Recipe):
  def _setConnectionDict(self, publish_dict, slave_reference=None):
    return super(Serialised, self)._setConnectionDict(wrap(publish_dict), slave_reference)



class PublishSection(GenericSlapRecipe):
  """
  Take a list of "request" sections, and publish every connection parameter.
  
  Input:
    section-list: String, representing the list of sections to fetch
                  parameters to publish, in order, separated by a space.
  """
  def _install(self):
    publish_dict = dict()
    for section in self.options['section-list'].strip().split():
      section = section.strip()
      options = self.buildout[section].copy()
      for k, v in options.iteritems():
        if k.startswith(CONNECTION_PARAMETER_STRING):
          print k, v
          publish_dict[k.lstrip(CONNECTION_PARAMETER_STRING)] = v
    self.setConnectionDict(publish_dict)
    return []

