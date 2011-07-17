# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Internationalisation.
"""

import __builtin__
import os

from . import mofile

podir = __path__[0]

def available():
    """Returns a list of language shortnames for which a MO file is available."""
    return [name[:-3] for name in os.listdir(podir) if name.endswith(".mo")]
 
def find(language):
    """Returns a .mo file for the given language.
    
    Returns None if no suitable MO file can be found.
    
    """
    filename = os.path.join(podir, language + ".mo")
    if os.path.exists(filename):
        return filename
    elif '_' in language:
        return find(language.split('_')[0])
    
def translator(mofile):
    """Returns a function that can translate messages using the specified MoFile object.
    
    The returned function can be called with one to four arguments:
    
    - message
    - context, message
    - message, plural_message, count
    - context, message, plural_message, count

    In all cases a single string (the translation) is returned.
    
    If mofile is None, returns a dummy translator that returns strings untranslated.
    
    """
    if mofile:
        funcs = (
            lambda: None,
            mofile.gettext,
            mofile.pgettext,
            mofile.ngettext,
            mofile.npgettext,
        )
    else:
        funcs = (
            lambda: None,
            lambda message: message,
            lambda context, message: message,
            lambda message, plural, count: message if count == 1 else plural,
            lambda context, message, plural, count: message if count == 1 else plural,
        )
    def translate(*args):
        """Translates a message.
        
        Can be called with one to four arguments:
        
        - message
        - context, message
        - message, plural_message, count
        - context, message, plural_message, count

        In all cases a single string (the translation) is returned.
        
        """
        return funcs[len(args)](*args)
    return translate
    
def install(filename):
    """Installs the translations from the given .mo file."""
    __builtin__._ = translator(mofile.MoFile(filename))

def remove():
    """Removes installed translations, reverting back to untranslated."""
    __builtin__._ = translator(None)


