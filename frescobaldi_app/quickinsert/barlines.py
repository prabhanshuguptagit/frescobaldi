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

from __future__ import unicode_literals

"""
The Quick Insert panel barlines and breathing sings Tool.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import app
import symbols

import tool
import buttongroup


class BarLines(tool.Tool):
    """Barlines tool in the quick insert panel toolbox.
    
    """
    def __init__(self, panel):
        super(BarLines, self).__init__(panel)
        self.layout().addWidget(BarlinesGroup(self))
        self.layout().addWidget(BreatheGroup(self))
        self.layout().addStretch(1)

    def icon(self):
        """Should return an icon for our tab."""
        return symbols.icon("bar_single")
    
    def title(self):
        """Should return a title for our tab."""
        return _("Bar Lines")
  
    def tooltip(self):
        """Returns a tooltip"""
        return _("Bar lines, breathing signs, etcetera.")


class BarlinesGroup(buttongroup.ButtonGroup):
    def translateUI(self):
        self.setTitle(_("Bar Lines"))
        
    def barlines(self):
        yield "bar_double", "||", _("Double bar line")
        yield "bar_end", "|.", _("Ending bar line")
        yield "bar_dotted", ":", _("Dotted bar line")
        yield "bar_dashed", "dashed", _("Dashed bar line")
        yield "bar_invisible", "", _("Invisible bar line")
        yield "bar_repeat_start", "|:", _("Repeat start")
        yield "bar_repeat_double", ":|:", _("Repeat both")
        yield "bar_repeat_end", ":|", _("Repeat end")
        yield "bar_cswc", ":|.:", _("Repeat both (old)")
        yield "bar_cswsc", ":|.|:", _("Repeat both (classic)")
        yield "bar_tick", "'", _("Tick bar line")
        yield "bar_single", "|", _("Single bar line")
        yield "bar_sws", "|.|", _("Small-Wide-Small bar line")
        yield "bar_ws", ".|", _("Wide-Small bar line")
        yield "bar_ww", ".|.", _("Double wide bar line")
        yield "bar_segno", "S", _("Segno bar line")
        
    def actionData(self):
        self._barlines = {}
        for name, ly_text, title in self.barlines():
            yield name, symbols.icon(name), None
            self._barlines[name] = ly_text
        
    def actionTexts(self):
        for name, ly_text, title in self.barlines():
            yield name, title
    
    
class BreatheGroup(buttongroup.ButtonGroup):
    def translateUI(self):
        self.setTitle(_("Breathing Signs"))

    def actionData(self):
        for name, title in self.actionTexts():
            yield name, symbols.icon(name), None
            
    def actionTexts(self):
        yield 'breathe_rcomma', _("Default Breathing Sign")
        yield 'breathe_rvarcomma', _("Straight Breathing Sign")
        yield 'breathe_caesura_curved', _("Curved Caesura")
        yield 'breathe_caesura_straight', _("Straight Caesura")


