from __future__ import absolute_import
from __future__ import unicode_literals

from pre_commit_hooks.validate_html import Jinja2MustacheRemover, Placeholder, PybarMustacheRemover, main as validate_html


HTML_WITH_HANDLEBAR_TITLE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
</head>
<body>
    <img alt="" src="http://root.website.com/{{#if img.title}}{{img.src}}{{/if}}"/>
</body>
</html>'''


def test_Jinja2MustacheRemover():
    assert Jinja2MustacheRemover('tests').clean_template('tests/jinja-template.html', Placeholder('DUMMY')) == '''base.html content
Jinja test

DUMMY
DUMMY
hardcoded
DUMMY
CONDITIONAL

DUMMY-iterstep-DUMMY-iterstep-
main template stuff
partial.html content
'''

def test_Jinja2MustacheRemover_providedEnv(tmpdir):
    html_file = tmpdir.join('test.html')
    html_file.write('{{x}}')
    assert Jinja2MustacheRemover('tests').clean_template(html_file.strpath, Placeholder('DUMMY', (('x', '"42"'),))) == '42'

def test_PybarMustacheRemover_providedEnv(tmpdir):
    hbs_file = tmpdir.join('test.hbs')
    hbs_file.write('{{x}}')
    assert PybarMustacheRemover().clean_template(hbs_file.strpath, Placeholder('DUMMY', (('x', '42'),))) == '42'

def test_validate_pybar_ok(tmpdir, caplog):
    hbs_file = tmpdir.join('test.hbs')
    hbs_file.write(HTML_WITH_HANDLEBAR_TITLE)
    assert validate_html(['--remove-mustaches', hbs_file.strpath]) == 0
    assert 'All good.' in caplog.text

def test_validate_jinja2_errors(caplog):
    assert validate_html(['--remove-mustaches',
                          '--mustache-remover=jinja2',
                          '--templates-include-dir=tests',
                          'tests/jinja-template.html']) == 2
    errors = caplog.text.splitlines()
    assert 'Expected "<!DOCTYPE html>"' in errors[0]
    assert 'Element "head" is missing a required instance of child element "title"' in errors[1]


def test_validate_handlebar_ko(tmpdir, caplog):
    html_file = tmpdir.join('test.hbs')
    html_file.write(HTML_WITH_HANDLEBAR_TITLE)
    assert validate_html([html_file.strpath]) == 1
    assert 'attribute "src" on element "img": Illegal character in path segment: "{" is not allowed.' in caplog.text
