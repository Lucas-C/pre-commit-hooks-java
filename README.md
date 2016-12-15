Pre-commit hooks to validate HTML5 pages or templates:

- one hook uses a regex-based NodeJS linter: https://github.com/yaniswang/HTMLHint

- another one used a [htmlparser2](https://github.com/fb55/htmlparser2)-based NodeJS linter: [htmllint](https://github.com/htmllint/htmllint/wiki/Options)

- the last one uses the v.Nu validator: http://validator.w3.org/nu/
It requires a `java` interpreter in the `$PATH`.

This hook can automagically replace mustaches by a default value in order to validate templates.
Currently, only http://handlebarsjs.com templates are supported for the moment (create an issue if you have other needs !).

## Usage

For `htmlhint` & `htmllint`:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.0.4
    hooks:
    -   id: htmlhint
        # optional custom config:
        args: [--config, .htmlhintrc]
    -   id: htmllint
```

For the W3C v.Nu validator:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.0.4
    hooks:
    -   id: validate-html
```

Advanced usage:

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.0.4
    hooks:
    -   id: validate-html
        args: [--remove-mustaches, "--ignore=Expected \"<!DOCTYPE html>\""]
        files: ^src/main/html/
```

## [FR] Accessibilité RGAA

Comme ce hook de pre-commit git utilise v.Nu, il permet de valider le critère RGAA3 **1.1 [A] "Chaque image a-t-elle une alternative textuelle ?"** [en employant le validateur HTML5 recommandé par la norme](http://disic.github.io/rgaa_methodologie/).


## Alternatives

- [HTML Tidy](http://www.html-tidy.org) : C
