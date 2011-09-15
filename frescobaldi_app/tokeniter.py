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
Use this module to get the parsed tokens of a document.

The tokens are created by the syntax highlighter, see highlighter.py.
The core methods of this module are tokens() and state(). These access
the token information from the highlighter, and also run the highlighter
if it has not run yet.

If you alter the document and directly after that need the new tokens,
use update().

"""

from __future__ import unicode_literals

import collections

from PyQt4.QtGui import QTextBlock, QTextCursor

import cursortools
import highlighter


def tokens(block):
    """Returns the tokens for the given block as a (possibly empty) tuple."""
    try:
        return highlighter.userData(block).tokens
    except AttributeError:
        highlighter.highlighter(block.document()).rehighlight()
    try:
        return highlighter.userData(block).tokens
    except AttributeError:
        return ()


def state(blockOrCursor):
    """Returns a thawn ly.lex.State() object at the beginning of the given QTextBlock.
    
    If the argument is a QTextCursor, uses the current block or the first block of its selection.
    
    """
    if isinstance(blockOrCursor, QTextCursor):
        if blockOrCursor.hasSelection():
            block = blockOrCursor.document().findBlock(blockOrCursor.selectionStart())
        else:
            block = blockOrCursor.block()
    else:
        block = blockOrCursor
    if block.userState() == -1:
        highlighter.highlighter(block.document()).rehighlight()
    return highlighter.highlighter(block.document()).state(block)


def update(block):
    """Retokenizes the given block, saving the tokens in the UserData."""
    highlighter.highlighter(block.document()).rehighlightBlock(block)


def cursor(block, token, start=0, end=None):
    """Returns a QTextCursor for the given token in the given block.
    
    If start is given the cursor will start at position start in the token
    (from the beginning of the token). Start defaults to 0.
    If end is given, the cursor will end at that position in the token (from
    the beginning of the token). End defaults to the length of the token.
    
    """
    if end is None:
        end = len(token)
    cursor = QTextCursor(block)
    cursor.setPosition(block.position() + token.pos + start)
    cursor.setPosition(block.position() + token.pos + end, QTextCursor.KeepAnchor)
    return cursor


def index(cursor):
    """Returns the index of the token at the cursor (right or overlapping).
    
    The index can range from 0 (if there are no tokens or the cursor is in the
    first token) to the total count of tokens in the cursor's block (if the
    cursor is at the very end of the block).
    
    """
    tokens_ = tokens(cursor.block())
    if cursor.atBlockEnd():
        return len(tokens_)
    pos = cursor.position() - cursor.block().position()
    lo, hi = 0, len(tokens_)
    while lo < hi:
        mid = (lo + hi) // 2
        if pos < tokens_[mid].pos:
            hi = mid
        else:
            lo = mid + 1
    return lo - 1


Partition = collections.namedtuple('Partition', 'left middle right')


def partition(cursor):
    """Returns a named three-tuple (left, middle, right).
    
    left is a tuple of tokens left to the cursor.
    middle is the token that overlaps the cursor at both sides (or None).
    right is a tuple of tokens right to the cursor.
    
    """
    t = tokens(cursor.block())
    i = index(cursor)
    if t:
        if i < len(t) and t[i].pos < cursor.position() - cursor.block().position():
            return Partition(t[:i], t[i], t[i+1:])
    return Partition(t[:i], None, t[i:])


def allTokens(document):
    """Yields all tokens of a document."""
    return (token for block in cursortools.allBlocks(document) for token in tokens(block))


def fromCursor(cursor, state=None, first=1):
    """Yields block, tokens starting at the cursor position.
    
    If state is given, it should be the state at the start of the block
    the selection begins. (Use state(cursor) to get that.)
    
    If first is -1: starts with the token that touches the cursor at the right
    If first is 0: starts with the token that overlaps the cursor
    If first is 1 (default): starts with the first token to the right.
    
    """
    block = cursor.document().findBlock(cursor.selectionStart())
    pos = cursor.selectionStart() - block.position()
    if state:
        def token_source(block):
            for t in tokens(block):
                state.follow(t)
                yield t
    else:
        def token_source(block):
            return iter(tokens(block))
    if first == -1:
        pred = lambda t: t.end < pos
    elif first == 0:
        pred = lambda t: t.end <= pos
    else:
        pred = lambda t: t.pos < pos
    def source_start(block):
        source = token_source(block)
        for t in source:
            if not pred(t):
                yield t
                for t in source:
                    yield t
    source = source_start
    while block.isValid():
        yield block, source(block)
        block = block.next()
        source = token_source


def selection(cursor, state=None, partial=True):
    """Yields block, selected_tokens for every block that has selected tokens.
    
    Usage:
    
    for block, tokens in selection(cursor):
        for token in tokens:
            do_something() ...
    
    If state is given, it should be the state at the start of the block
    the selection begins. (Use state(cursor) to get that.)
    
    If partial is True (the default), also tokens that are partially inside
    the selection are yielded.
    
    """
    block = cursor.document().findBlock(cursor.selectionStart())
    endblock = cursor.document().findBlock(cursor.selectionEnd())
    pos = cursor.selectionStart() - block.position()
    endpos = cursor.selectionEnd() - endblock.position()
    
    if state:
        follow = state.follow
        def follower(source):
            for t in source:
                follow(t)
                yield t
    else:
        follow = lambda t: None
        follower = lambda i: i
    if partial:
        start_pred = lambda t: t.end <= pos
        end_pred = lambda t: t.pos >= endpos
    else:
        start_pred = lambda t: t.pos < pos
        end_pred = lambda t: t.end > endpos
    def token_source(block):
        return iter(tokens(block))
    def source_start(block):
        source = iter(tokens(block))
        for t in source:
            if start_pred(t):
                follow(t)
                continue
            else:
                yield t
                for t in source:
                    yield t
    def source_end(source):
        for t in source:
            if end_pred(t):
                break
            yield t
    source = source_start
    while block != endblock:
        yield block, follower(source(block))
        block = block.next()
        source = token_source
    yield block, follower(source_end(source(block)))


class Source(object):
    """Helper iterator.
    
    Iterates over the (block, tokens) tuples such as yielded by selection()
    and fromCursor(). Stores the current block in the block attribute and the
    tokens (which also should be a generator) in the tokens attribute. 
    
    Iterating over the source object itself just yields the tokens, while the
    block attribute contains the current block.
    
    You can also iterate over the tokens attribute, which will yield the
    remaining tokens of the current block and then stop.
    
    Use the fromCursor() and selection() class methods with the same arguments
    as the corresponding global functions to create a source iterator.
    
    So this:
    
    import tokeniter
    s = tokeniter.Source(tokeniter.selection(cursor))
    
    is equivalent to:
    
    import tokeniter
    s = tokeniter.Source.selection(cursor)
    
    And then you can do:
    
    for token in s:
        ... # do something with every token
        ...
        for token in s.tokens:
            ... # do something with the remaining tokens on the line
    
    """
    def __init__(self, gen, state=None):
        """Initializes ourselves with a generator returning (block, tokens)."""
        self.state = state
        for self.block, self.tokens in gen:
            break
        def g():
            for t in self.tokens:
                yield t
            for self.block, self.tokens in gen:
                for t in self.tokens:
                    yield t
        self.gen = g()
    
    def __iter__(self):
        return self.gen
    
    def __next__(self):
        return self.gen.next()
    
    next = __next__
    
    def cursor(self, token, start=0, end=None):
        """Returns a QTextCursor for the token in the current block.
        
        See the global cursor() function for more information.
        
        """
        return cursor(self.block, token, start, end)
    
    @classmethod
    def fromCursor(cls, cursor, state=None, first=1):
        """Initializes a source object with a fromCursor generator.
        
        If state is True, the state(cursor) module function is called and the
        result is put in the state attribute. Otherwise state is just passed to
        the global fromCursor() function.
        See the documentation for the global fromCursor() function.
        
        """
        if state is True:
            state = globals()['state'](cursor)
        return cls(fromCursor(cursor, state, first), state)
    
    @classmethod
    def selection(cls, cursor, state=None, partial=True):
        """Initializes a source object with a fromCursor generator.
        
        If state is True, the state(cursor) module function is called and the
        result is put in the state attribute. Otherwise state is just passed to
        the global selection() function.
        See the documentation for the global selection() function.
        
        """
        if state is True:
            state = globals()['state'](cursor)
        return cls(selection(cursor, state, partial), state)


class Runner(object):
    """Iterates back and forth over tokens.
    
    A Runner can stop anywhere and remembers its current token.
    
    """
    def __init__(self, block, atEnd=False):
        """Positions the token iterator at the start of the given QTextBlock.
        
        If atEnd == True, the iterator is positioned past the end of the block.
        
        """
        self.block = block
        self._tokens = tokens(block)
        self._index = len(self._tokens) if atEnd else -1
    
    def forward_line(self):
        """Yields tokens in forward direction in the current block."""
        while self._index + 1 < len(self._tokens):
            self._index += 1
            yield self._tokens[self._index]
    
    def forward(self):
        """Yields tokens in forward direction across blocks."""
        while self.block.isValid():
            for t in self.forward_line():
                yield t
            self.__init__(self.block.next())
    
    def backward_line(self):
        """Yields tokens in backward direction in the current block."""
        while self._index > 0:
            self._index -= 1
            yield self._tokens[self._index]
    
    def backward(self):
        """Yields tokens in backward direction across blocks."""
        while self.block.isValid():
            for t in self.backward_line():
                yield t
            self.__init__(self.block.previous(), True)
    
    def atBlockStart(self):
        """Returns True if the iterator is at the start of the current block."""
        return self._index <= 0
    
    def atBlockEnd(self):
        """Returns True if the iterator is at the end of the current block."""
        return self._index >= len(self._tokens) - 1
        
    def token(self):
        """Re-returns the last yielded token."""
        return self._tokens[self._index]
        
    def cursor(self, start=0, end=None):
        """Returns a QTextCursor for the last token.
        
        If start is given the cursor will start at position start in the token
        (from the beginning of the token). Start defaults to 0.
        If end is given, the cursor will end at that position in the token (from
        the beginning of the token). End defaults to the length of the token.
        
        """
        return cursor(self.block, self._tokens[self._index], start, end)

    def copy(self):
        obj = object.__new__(self.__class__)
        obj.block = self.block
        obj._tokens = self._tokens
        obj._index = self._index
        return obj


