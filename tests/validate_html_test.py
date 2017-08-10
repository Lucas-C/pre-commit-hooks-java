from __future__ import absolute_import
from __future__ import unicode_literals

from pre_commit_hooks.validate_html import main as validate_html


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

JINJA_TEMPLATE = '''
{% extends "base.html" %}
{% block title %}Search results{% endblock %}
{% set bullet = joiner(" &bullet; ") %}
{% for truc in machin %}
    {{bullet()}}
    {% if dummy %}
        {{ ' '.join(article.content.split(' ')[:75])|striptags|striptags }}
    {% endif %}
{% endfor %}
{% include "partial.html" %}
'''


def test_validate_pybar_ok(tmpdir, caplog):
    hbs_file = tmpdir.join('test.hbs')
    hbs_file.write(HTML_WITH_HANDLEBAR_TITLE)
    assert validate_html(['--remove-mustaches', hbs_file.strpath]) == 0
    assert 'All good.' in caplog.text

def test_validate_jinja2_ok(tmpdir, caplog):
    hbs_file = tmpdir.join('test.hbs')
    hbs_file.write(JINJA_TEMPLATE)
    assert validate_html(['--remove-mustaches', '--mustache-remover=jinja2', '--templates-include-dir=tests', hbs_file.strpath]) == 0
    assert 'All good.' in caplog.text


def test_validate_html_ko(tmpdir, caplog):
    html_file = tmpdir.join('test.hbs')
    html_file.write(HTML_WITH_HANDLEBAR_TITLE)
    assert validate_html([html_file.strpath]) == 1
    assert 'attribute "src" on element "img": Illegal character in path segment: "{" is not allowed.' in caplog.text
