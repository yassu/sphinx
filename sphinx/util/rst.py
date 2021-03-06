# -*- coding: utf-8 -*-
"""
    sphinx.util.rst
    ~~~~~~~~~~~~~~~

    reST helper functions.

    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import

import re
from contextlib import contextmanager

from docutils.parsers.rst import roles
from docutils.parsers.rst.languages import en as english
from docutils.utils import Reporter

from sphinx.locale import __
from sphinx.util import docutils
from sphinx.util import logging

if False:
    # For type annotation
    from typing import Generator  # NOQA
    from docutils.statemachine import StringList  # NOQA
    from sphinx.util.typing import unicode  # NOQA

logger = logging.getLogger(__name__)

docinfo_re = re.compile(':\\w+:.*?')
symbols_re = re.compile(r'([!-\-/:-@\[-`{-~])')  # symbols without dot(0x2e)


def escape(text):
    # type: (unicode) -> unicode
    text = symbols_re.sub(r'\\\1', text)
    text = re.sub(r'^\.', r'\.', text)  # escape a dot at top
    return text


@contextmanager
def default_role(docname, name):
    # type: (unicode, unicode) -> Generator
    if name:
        dummy_reporter = Reporter('', 4, 4)
        role_fn, _ = roles.role(name, english, 0, dummy_reporter)
        if role_fn:
            docutils.register_role('', role_fn)
        else:
            logger.warning(__('default role %s not found'), name, location=docname)

    yield

    docutils.unregister_role('')


def prepend_prolog(content, prolog):
    # type: (StringList, unicode) -> None
    """Prepend a string to content body as prolog."""
    if prolog:
        pos = 0
        for line in content:
            if docinfo_re.match(line):
                pos += 1
            else:
                break

        if pos > 0:
            # insert a blank line after docinfo
            content.insert(pos, '', '<generated>', 0)
            pos += 1

        # insert prolog (after docinfo if exists)
        for lineno, line in enumerate(prolog.splitlines()):
            content.insert(pos + lineno, line, '<rst_prolog>', lineno)

        content.insert(pos + lineno + 1, '', '<generated>', 0)


def append_epilog(content, epilog):
    # type: (StringList, unicode) -> None
    """Append a string to content body as epilog."""
    if epilog:
        content.append('', '<generated>', 0)
        for lineno, line in enumerate(epilog.splitlines()):
            content.append(line, '<rst_epilog>', lineno)
