A pre-commit hook to validate like http://validator.w3.org/nu/

Requires a `java` interpreter installed.

Support http://handlebarsjs.com only for the moment (tell me if you have other needs).

The `--remove-mustaches` feature is currently pending on a bug fix: https://github.com/svenkreiss/html5validator/issues/27

## Usage

```
-   repo: https://github.com/Lucas-C/pre-commit-hooks-html
    sha: v1.0.2
    hooks:
    -   id: validate-html
        args: [--remove-mustaches]
```
