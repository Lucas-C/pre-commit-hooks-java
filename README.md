A pre-commit hook to validate HTML5 pages or templates.
It uses the v.Nu validator behind http://validator.w3.org/nu/.

This hook requires a `java` interpreter in the `$PATH`.

This hook can automagically replace mustaches by a default value in order to validate templates.
Currently, only http://handlebarsjs.com templates are supported for the moment (create an issue if you have other needs !).

## Usage

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
