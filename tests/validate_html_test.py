from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from pre_commit_hooks.validate_html import main as validate_html


HTML_WITH_HANDLEBAR_TITLE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
</head>
<body>
    <img alt="" src="http://root.website.com/{{#if img.src}}{{img.src}}{{/if}}"/>
</body>
</html>'''


def test_validate_html_ok(tmpdir, capsys):
    hbs_file = tmpdir.join('test.hbs')
    hbs_file.write(HTML_WITH_HANDLEBAR_TITLE)
    with pytest.raises(SystemExit):
        try:
            validate_html(['--remove-mustaches', hbs_file.strpath])
        except SystemExit as error:
            _, stderr = capsys.readouterr()
            assert stderr == ''
            assert error.code == 0
            raise


def test_validate_html_ko(tmpdir, capsys):
    html_file = tmpdir.join('test.hbs')
    html_file.write(HTML_WITH_HANDLEBAR_TITLE)
    with pytest.raises(SystemExit):
        try:
            validate_html([html_file.strpath])
        except SystemExit as error:
            _, stderr = capsys.readouterr()
            assert stderr.endswith('attribute "src" on element "img": Illegal character in path segment: "{" is not allowed.\n')
            assert error.code == 1
            raise
