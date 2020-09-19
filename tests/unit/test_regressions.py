"""A growing set of tests designed to ensure isort doesn't have regressions in new versions"""
from io import StringIO

import isort


def test_isort_duplicating_comments_issue_1264():
    """Ensure isort doesn't duplicate comments when force_sort_within_sections is set to `True`
    as was the case in issue #1264: https://github.com/pycqa/isort/issues/1264
    """
    assert (
        isort.code(
            """
from homeassistant.util.logging import catch_log_exception

# Loading the config flow...
from . import config_flow
""",
            force_sort_within_sections=True,
        ).count("# Loading the config flow...")
        == 1
    )


def test_moving_comments_issue_726():
    test_input = (
        "from Blue import models as BlueModels\n"
        "# comment for PlaidModel\n"
        "from Plaid.models import PlaidModel\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input

    test_input = (
        "# comment for BlueModels\n"
        "from Blue import models as BlueModels\n"
        "# comment for PlaidModel\n"
        "# another comment for PlaidModel\n"
        "from Plaid.models import PlaidModel\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input


def test_blank_lined_removed_issue_1275():
    """Ensure isort doesn't accidentally remove blank lines after doc strings and before imports.
    See: https://github.com/pycqa/isort/issues/1275
    """
    assert (
        isort.code(
            '''"""
My docstring
"""

from b import thing
from a import other_thing
'''
        )
        == '''"""
My docstring
"""

from a import other_thing
from b import thing
'''
    )

    assert (
        isort.code(
            '''"""
My docstring
"""

from b import thing
from a import other_thing
''',
            add_imports=["from b import thing"],
        )
        == '''"""
My docstring
"""

from a import other_thing
from b import thing
'''
    )


def test_blank_lined_removed_issue_1283():
    """Ensure isort doesn't accidentally remove blank lines after __version__ identifiers.
    See: https://github.com/pycqa/isort/issues/1283
    """
    test_input = """__version__ = "0.58.1"

from starlette import status
"""
    assert isort.code(test_input) == test_input


def test_extra_blank_line_added_nested_imports_issue_1290():
    """Ensure isort doesn't added unecessary blank lines above nested imports.
    See: https://github.com/pycqa/isort/issues/1290
    """
    test_input = '''from typing import TYPE_CHECKING

# Special imports
from special import thing

if TYPE_CHECKING:
    # Special imports
    from special import another_thing


def func():
    """Docstring"""

    # Special imports
    from special import something_else
    return
'''
    assert (
        isort.code(
            test_input,
            import_heading_special="Special imports",
            known_special=["special"],
            sections=["FUTURE", "STDLIB", "THIRDPARTY", "SPECIAL", "FIRSTPARTY", "LOCALFOLDER"],
        )
        == test_input
    )


def test_add_imports_shouldnt_make_isort_unusable_issue_1297():
    """Test to ensure add imports doesn't cause any unexpected behaviour when combined with check
    See: https://github.com/pycqa/isort/issues/1297
    """
    assert isort.check_code(
        """from __future__ import unicode_literals

from os import path
""",
        add_imports={"from __future__ import unicode_literals"},
    )


def test_no_extra_lines_for_imports_in_functions_issue_1277():
    """Test to ensure isort doesn't introduce extra blank lines for imports within function.
    See: https://github.com/pycqa/isort/issues/1277
    """
    test_input = """
def main():
    import time

    import sys
"""
    expected_output = """
def main():
    import sys
    import time
"""
    assert isort.code(isort.code(isort.code(test_input))) == expected_output


def test_no_extra_blank_lines_in_methods_issue_1293():
    """Test to ensure isort isn't introducing extra lines in methods that contain imports
    See: https://github.com/pycqa/isort/issues/1293
    """
    test_input = """

class Something(object):
    def on_email_deleted(self, email):
        from hyperkitty.tasks import rebuild_thread_cache_new_email

        # update or cleanup thread                  # noqa: E303 (isort issue)
        if self.emails.count() == 0:
            ...
"""
    assert isort.code(test_input) == test_input
    assert isort.code(test_input, lines_after_imports=2) == test_input


def test_force_single_line_shouldnt_remove_preceding_comment_lines_issue_1296():
    """Tests to ensure force_single_line setting doesn't result in lost comments.
    See: https://github.com/pycqa/isort/issues/1296
    """
    test_input = """
# A comment
# A comment

# Oh no, I'm gone
from moo import foo
"""
    # assert isort.code(test_input) == test_input
    assert isort.code(test_input, force_single_line=True) == test_input


def test_ensure_new_line_before_comments_mixed_with_ensure_newline_before_comments_1295():
    """Tests to ensure that the black profile can be used in conjunction with
    force_sort_within_sections.

    See: https://github.com/pycqa/isort/issues/1295
    """
    test_input = """
from openzwave.group import ZWaveGroup
from openzwave.network import ZWaveNetwork

# pylint: disable=import-error
from openzwave.option import ZWaveOption
"""
    assert isort.code(test_input, profile="black") == test_input
    assert isort.code(test_input, profile="black", force_sort_within_sections=True) == test_input


def test_trailing_comma_doesnt_introduce_broken_code_with_comment_and_wrap_issue_1302():
    """Tests to assert the combination of include_trailing_comma and a wrapped line doesnt break.
    See: https://github.com/pycqa/isort/issues/1302.
    """
    assert (
        isort.code(
            """
from somewhere import very_very_very_very_very_very_long_symbol # some comment
""",
            line_length=50,
            include_trailing_comma=True,
        )
        == """
from somewhere import \\
    very_very_very_very_very_very_long_symbol  # some comment
"""
    )


def test_ensure_sre_parse_is_identified_as_stdlib_issue_1304():
    """Ensure sre_parse is idenified as STDLIB.
    See: https://github.com/pycqa/isort/issues/1304.
    """
    assert isort.place_module("sre_parse") == isort.place_module("sre") == isort.settings.STDLIB


def test_add_imports_shouldnt_move_lower_comments_issue_1300():
    """Ensure add_imports doesn't move comments immediately below imports.
    See:: https://github.com/pycqa/isort/issues/1300.
    """
    test_input = """from __future__ import unicode_literals

from os import path

# A comment for a constant
ANSWER = 42
"""
    assert isort.code(test_input, add_imports=["from os import path"]) == test_input


def test_windows_newline_issue_1277():
    """Test to ensure windows new lines are correctly handled within indented scopes.
    See: https://github.com/pycqa/isort/issues/1277
    """
    assert (
        isort.code("\ndef main():\r\n    import time\r\n\n    import sys\r\n")
        == "\ndef main():\r\n    import sys\r\n    import time\r\n"
    )


def test_windows_newline_issue_1278():
    """Test to ensure windows new lines are correctly handled within indented scopes.
    See: https://github.com/pycqa/isort/issues/1278
    """
    assert isort.check_code(
        "\ntry:\r\n    import datadog_agent\r\n\r\n    "
        "from ..log import CheckLoggingAdapter, init_logging\r\n\r\n    init_logging()\r\n"
        "except ImportError:\r\n    pass\r\n"
    )


def test_check_never_passes_with_indented_headings_issue_1301():
    """Test to ensure that test can pass even when there are indented headings.
    See: https://github.com/pycqa/isort/issues/1301
    """
    assert isort.check_code(
        """
try:
    # stdlib
    import logging
    from os import abc, path
except ImportError:
    pass
""",
        import_heading_stdlib="stdlib",
    )


def test_isort_shouldnt_fail_on_long_from_with_dot_issue_1190():
    """Test to ensure that isort will correctly handle formatting a long from import that contains
    a dot.
    See: https://github.com/pycqa/isort/issues/1190
    """
    assert (
        isort.code(
            """
from this_is_a_very_long_import_statement.that_will_occur_across_two_lines\\
        .when_the_line_length.is_only_seventynine_chars import (
    function1,
    function2,
)
        """,
            line_length=79,
            multi_line_output=3,
        )
        == """
from this_is_a_very_long_import_statement.that_will_occur_across_two_lines"""
        """.when_the_line_length.is_only_seventynine_chars import (
    function1,
    function2
)
"""
    )


def test_isort_shouldnt_add_extra_new_line_when_fass_and_n_issue_1315():
    """Test to ensure isort doesnt add a second extra new line when combining --fss and -n options.
    See: https://github.com/pycqa/isort/issues/1315
    """
    assert isort.check_code(
        """import sys

# Comment canary
from . import foo
""",
        ensure_newline_before_comments=True,  # -n
        force_sort_within_sections=True,  # -fss
        show_diff=True,  # for better debugging in the case the test case fails.
    )

    assert (
        isort.code(
            """
from . import foo
# Comment canary
from .. import foo
""",
            ensure_newline_before_comments=True,
            force_sort_within_sections=True,
        )
        == """
from . import foo

# Comment canary
from .. import foo
"""
    )


def test_isort_doesnt_rewrite_import_with_dot_to_from_import_issue_1280():
    """Test to ensure isort doesn't rewrite imports in the from of import y.x into from y import x.
    This is because they are not technically fully equivalent to eachother and can introduce broken
    behaviour.
    See: https://github.com/pycqa/isort/issues/1280
    """
    assert isort.check_code(
        """
        import test.module
        import test.module as m
        from test import module
        from test import module as m
    """,
        show_diff=True,
    )


def test_isort_shouldnt_introduce_extra_lines_with_fass_issue_1322():
    """Tests to ensure isort doesn't introduce extra lines when used with fass option.
    See: https://github.com/pycqa/isort/issues/1322
    """
    assert (
        isort.code(
            """
        import logging

# Comment canary
from foo import bar
import quux
""",
            force_sort_within_sections=True,
            ensure_newline_before_comments=True,
        )
        == """
        import logging

# Comment canary
from foo import bar
import quux
"""
    )


def test_comments_should_cause_wrapping_on_long_lines_black_mode_issue_1219():
    """Tests to ensure if isort encounters a single import line which is made too long with a comment
    it is wrapped when using black profile.
    See: https://github.com/pycqa/isort/issues/1219
    """
    assert isort.check_code(
        """
from many_stop_words import (
    get_stop_words as get_base_stopwords,  # extended list of stop words, also for en
)
""",
        show_diff=True,
        profile="black",
    )


def test_comment_blocks_should_stay_associated_without_extra_lines_issue_1156():
    """Tests to ensure isort doesn't add an extra line when there are large import blocks
    or otherwise warp the intent.
    See: https://github.com/pycqa/isort/issues/1156
    """
    assert (
        isort.code(
            """from top_level_ignored import config  # isort:skip
####################################
# COMMENT BLOCK SEPARATING THESE   #
####################################
from ast import excepthandler
import logging
"""
        )
        == """from top_level_ignored import config  # isort:skip
import logging
####################################
# COMMENT BLOCK SEPARATING THESE   #
####################################
from ast import excepthandler
"""
    )


def test_comment_shouldnt_be_duplicated_with_fass_enabled_issue_1329():
    """Tests to ensure isort doesn't duplicate comments when imports occur with comment on top,
    immediately after large comment blocks.
    See: https://github.com/pycqa/isort/pull/1329/files.
    """
    assert isort.check_code(
        """'''
Multi-line docstring
'''
# Comment for A.
import a
# Comment for B - not A!
import b
""",
        force_sort_within_sections=True,
        show_diff=True,
    )


def test_wrap_mode_equal_to_line_length_with_indendet_imports_issue_1333():
    assert isort.check_code(
        """
import a
import b


def function():
    import a as b
    import c as d
""",
        line_length=17,
        wrap_length=17,
        show_diff=True,
    )


def test_isort_skipped_nested_imports_issue_1339():
    """Ensure `isort:skip are honored in nested imports.
    See: https://github.com/pycqa/isort/issues/1339.
    """
    assert isort.check_code(
        """
    def import_test():
        from os ( # isort:skip
            import path
        )
    """,
        show_diff=True,
    )


def test_windows_diff_too_large_misrepresentative_issue_1348(test_path):
    """Ensure isort handles windows files correctly when it come to producing a diff with --diff.
    See: https://github.com/pycqa/isort/issues/1348
    """
    diff_output = StringIO()
    isort.file(test_path / "example_crlf_file.py", show_diff=diff_output)
    diff_output.seek(0)
    assert diff_output.read().endswith(
        "-1,5 +1,5 @@\n+import a\r\n import b\r\n" "-import a\r\n \r\n \r\n def func():\r\n"
    )


def test_combine_as_does_not_lose_comments_issue_1321():
    """Test to ensure isort doesn't lose comments when --combine-as is used.
    See: https://github.com/pycqa/isort/issues/1321
    """
    test_input = """
from foo import *  # noqa
from foo import bar as quux  # other
from foo import x as a  # noqa

import operator as op  # op comment
import datetime as dtime  # dtime comment

from datetime import date as d  # dcomm
from datetime import datetime as dt  # dtcomm
"""

    expected_output = """
import datetime as dtime  # dtime comment
import operator as op  # op comment
from datetime import date as d, datetime as dt  # dcomm; dtcomm

from foo import *  # noqa
from foo import bar as quux, x as a  # other; noqa
"""

    assert isort.code(test_input, combine_as_imports=True) == expected_output


def test_combine_as_does_not_lose_comments_issue_1381():
    """Test to ensure isort doesn't lose comments when --combine-as is used.
    See: https://github.com/pycqa/isort/issues/1381
    """
    test_input = """
from smtplib import SMTPConnectError, SMTPNotSupportedError  # important comment
"""
    assert "# important comment" in isort.code(test_input, combine_as_imports=True)

    test_input = """
from appsettings import AppSettings, ObjectSetting, StringSetting  # type: ignore
"""
    assert "# type: ignore" in isort.code(test_input, combine_as_imports=True)


def test_incorrect_grouping_when_comments_issue_1396():
    """Test to ensure isort groups import correct independent of the comments present.
    See: https://github.com/pycqa/isort/issues/1396
    """
    assert (
        isort.code(
            """from django.shortcuts import render
from apps.profiler.models import Project
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    # ListView,
    # DetailView,
    TemplateView,
    # CreateView,
    # View
)
""",
            line_length=88,
            known_first_party=["apps"],
            known_django=["django"],
            sections=["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
        )
        == """from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import \\
    TemplateView  # ListView,; DetailView,; CreateView,; View

from apps.profiler.models import Project
"""
    )
    assert (
        isort.code(
            """from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.profiler.models import Project

from django.views.generic import ( # ListView,; DetailView,; CreateView,; View
    TemplateView,
)
""",
            line_length=88,
            known_first_party=["apps"],
            known_django=["django"],
            sections=["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
            include_trailing_comma=True,
            multi_line_output=3,
            force_grid_wrap=0,
            use_parentheses=True,
            ensure_newline_before_comments=True,
        )
        == """from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import (  # ListView,; DetailView,; CreateView,; View
    TemplateView,
)

from apps.profiler.models import Project
"""
    )


def test_reverse_relative_combined_with_force_sort_within_sections_issue_1395():
    """Test to ensure reverse relative combines well with other common isort settings.
    See: https://github.com/pycqa/isort/issues/1395.
    """
    assert isort.check_code(
        """from .fileA import a_var
from ..fileB import b_var
""",
        show_diff=True,
        reverse_relative=True,
        force_sort_within_sections=True,
        order_by_type=False,
        case_sensitive=False,
        multi_line_output=5,
        sections=["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "APPLICATION", "LOCALFOLDER"],
        lines_after_imports=2,
        no_lines_before="LOCALFOLDER",
    )


def test_isort_should_be_able_to_add_independent_of_doc_string_placement_issue_1420():
    """isort should be able to know when an import requested to be added is sucesfully added,
    independent of where the top doc string is located.
    See: https://github.com/PyCQA/isort/issues/1420
    """
    assert isort.check_code(
        '''"""module docstring"""

import os
''',
        show_diff=True,
        add_imports=["os"],
    )


def test_comments_should_never_be_moved_between_imports_issue_1427():
    """isort should never move comments to different import statement.
    See: https://github.com/PyCQA/isort/issues/1427
    """
    assert isort.check_code(
        """from package import CONSTANT
from package import *  # noqa
        """,
        force_single_line=True,
        show_diff=True,
    )


def test_isort_doesnt_misplace_comments_issue_1431():
    """Test to ensure isort wont misplace comments.
    See: https://github.com/PyCQA/isort/issues/1431
    """
    input_text = """from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent,  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component,  # DRY
)
"""
    assert isort.code(input_text, profile="black") == input_text


def test_isort_doesnt_misplace_add_import_issue_1445():
    """Test to ensure isort won't misplace an added import depending on docstring position
    See: https://github.com/PyCQA/isort/issues/1445
    """
    assert (
        isort.code(
            '''#!/usr/bin/env python

"""module docstring"""
''',
            add_imports=["import os"],
        )
        == '''#!/usr/bin/env python

"""module docstring"""

import os
'''
    )

    assert isort.check_code(
        '''#!/usr/bin/env python

"""module docstring"""

import os
    ''',
        add_imports=["import os"],
        show_diff=True,
    )


def test_isort_doesnt_mangle_code_when_adding_imports_issue_1444():
    """isort should NEVER mangle code. This particularly nasty and easy to reproduce bug,
    caused isort to produce invalid code just by adding a single import statement depending
    on comment placement.
    See: https://github.com/PyCQA/isort/issues/1444
    """
    assert (
        isort.code(
            '''

"""module docstring"""
''',
            add_imports=["import os"],
        )
        == '''

"""module docstring"""

import os
'''
    )


def test_isort_doesnt_float_to_top_correctly_when_imports_not_at_top_issue_1382():
    """isort should float existing imports to the top, if they are currently below the top.
    See: https://github.com/PyCQA/isort/issues/1382
    """
    assert (
        isort.code(
            """
def foo():
    pass

import a

def bar():
    pass
""",
            float_to_top=True,
        )
        == """import a


def foo():
    pass


def bar():
    pass
"""
    )

    assert (
        isort.code(
            """






def foo():
    pass

import a

def bar():
    pass
""",
            float_to_top=True,
        )
        == """import a


def foo():
    pass


def bar():
    pass
"""
    )

    assert (
        isort.code(
            '''"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''
"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''
"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''#!/bin/bash
"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''#!/bin/bash
"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''#!/bin/bash

"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''#!/bin/bash

"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )


def test_empty_float_to_top_shouldnt_error_issue_1453():
    """isort shouldn't error when float to top is set with a mostly empty file"""
    assert isort.check_code(
        """
""",
        show_diff=True,
        float_to_top=True,
    )
    assert isort.check_code(
        """
""",
        show_diff=True,
    )


def test_import_sorting_shouldnt_be_endless_with_headers_issue_1454():
    """isort should never enter an endless sorting loop.
    See: https://github.com/PyCQA/isort/issues/1454
    """
    assert isort.check_code(
        """

# standard library imports
import sys

try:
    # Comment about local lib
    # related third party imports
    from local_lib import stuff
except ImportError as e:
    pass
""",
        known_third_party=["local_lib"],
        import_heading_thirdparty="related third party imports",
        show_diff=True,
    )


def test_isort_should_leave_non_import_from_lines_alone():
    """isort should never mangle non-import from statements.
    See: https://github.com/PyCQA/isort/issues/1488
    """
    raise_from_should_be_ignored = """
    raise SomeException("Blah") \
        from exceptionsInfo.popitem()[1]
"""
    assert isort.check(raise_from_should_be_ignored, show_diff=True)

    yield_from_should_be_ignored = """
def generator_function():
    yield \
        from []
"""
    assert isort.check(raise_from_should_be_ignored, show_diff=True)
