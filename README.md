[![](https://travis-ci.org/Lucas-C/pre-commit-hooks-java.svg?branch=master)](https://travis-ci.org/Lucas-C/pre-commit-hooks-java)

[Pre-commit](https://pre-commit.com) hooks requiring a `java` interpreter in the `$PATH`.

The `validate-html` hook uses the v.Nu validator: http://validator.w3.org/nu/.
It can automagically replace mustaches by a default value in order to validate templates.
Currently, only [handlebars](http://handlebarsjs.com) templates are supported. Please create an issue if you need support for other template engines: the ones where a Python implementation exist should be easy to add.

## Usage
```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-java
    sha: 1.3.9
    hooks:
    -   id: validate-html
```

Advanced usage:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-java
    sha: 1.3.9
    hooks:
    -   id: validate-html
        args: [--remove-mustaches, "--ignore=Expected \"<!DOCTYPE html>\""]
        files: ^src/main/html/
```

With Jinja templates:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-java
    sha: 1.3.9
    hooks:
    -   id: validate-html
        args: [--remove-mustaches, --mustache-remover=jinja2]
```

## [FR] Accessibilité RGAA

Comme ce hook de pre-commit git utilise v.Nu, il permet de valider le critère RGAA3 **1.1 [A] "Chaque image a-t-elle une alternative textuelle ?"** [en employant le validateur HTML5 recommandé par la norme](http://disic.github.io/rgaa_methodologie/).

Si vous souhaitez effectuer d'autres validations automatiques de critères d'accessibilité, jetez un oeil à [WCAG-Zoo](https://wcag-zoo.readthedocs.io)

## Alternatives

- [HTML Tidy](http://www.html-tidy.org) : implemented in C
