[![](https://travis-ci.org/Lucas-C/pre-commit-hooks-html.svg?branch=master)](https://travis-ci.org/Lucas-C/pre-commit-hooks-html)

Pre-commit hooks to validate HTML5 pages or templates:

- one hook uses a regex-based NodeJS linter: https://github.com/yaniswang/HTMLHint

- another one used a [htmlparser2](https://github.com/fb55/htmlparser2)-based NodeJS linter: [htmllint](https://github.com/htmllint/htmllint/wiki/Options)

- the last one uses the v.Nu validator: http://validator.w3.org/nu/.
It requires a `java` interpreter in the `$PATH`.

This last hook can automagically replace mustaches by a default value in order to validate templates.
Currently, only [handlebars](http://handlebarsjs.com) templates are supported. Please create an issue if you need support for other template engines: the ones where a Python implementation exist should be easy to add.

## Usage

For `htmlhint` & `htmllint` (this one require you to have a config file like [this default `.htmllintrc`](https://github.com/htmllint/htmllint-cli/blob/master/lib/default_cfg.json)) :

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.2.0
    hooks:
    -   id: htmlhint
        # optional custom config:
        args: [--config, .htmlhintrc]
    -   id: htmllint
```

For the W3C v.Nu validator:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.2.0
    hooks:
    -   id: validate-html
```

Advanced usage:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.2.0
    hooks:
    -   id: validate-html
        args: [--remove-mustaches, "--ignore=Expected \"<!DOCTYPE html>\""]
        files: ^src/main/html/
```

## [FR] Accessibilité RGAA

Comme ce hook de pre-commit git utilise v.Nu, il permet de valider le critère RGAA3 **1.1 [A] "Chaque image a-t-elle une alternative textuelle ?"** [en employant le validateur HTML5 recommandé par la norme](http://disic.github.io/rgaa_methodologie/).


## Alternatives

- [HTML Tidy](http://www.html-tidy.org) : implemented in C
