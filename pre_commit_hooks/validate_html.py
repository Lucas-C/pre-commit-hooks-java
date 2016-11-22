from __future__ import print_function
import argparse, contextlib, os, shutil, sys
from pybars import Compiler as PybarCompiler, PybarsError
from html5validator.validator import Validator


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='filenames to check')
    parser.add_argument('--show-warnings', dest='error_only',
                        action='store_false', default=True)
    parser.add_argument('--ignore', nargs='*', default=None,
                        type=lambda s: (s.decode('utf-8')
                                        if isinstance(s, bytes) else s),
                        help='ignore messages containing the given strings')
    parser.add_argument('--ignore-re', nargs='*', default=None,
                        type=lambda s: (s.decode('utf-8')
                                        if isinstance(s, bytes) else s),
                        dest='ignore_re',
                        help='regular expression of messages to ignore')
    parser.add_argument('-l', action='store_const', const=2048,
                        dest='stack_size',
                        help=('run on larger files: sets Java '
                              'stack size to 2048k')
                        )
    parser.add_argument('-ll', action='store_const', const=8192,
                        dest='stack_size',
                        help=('run on larger files: sets Java '
                              'stack size to 8192k')
                        )
    parser.add_argument('-lll', action='store_const', const=32768,
                        dest='stack_size',
                        help=('run on larger files: sets Java '
                              'stack size to 32768k')
                        )
    parser.add_argument('--remove-mustaches', action='store_true', default=False)
    parser.add_argument('--mustache-remover-copy-ext', default='~~')
    parser.add_argument('--mustache-remover-default-value', default='DUMMY')
    args = parser.parse_args(argv)

    if not args.filenames:
        return 0

    validator = CustomHTMLValidator(mustache_remover_copy_ext=args.mustache_remover_copy_ext, mustache_remover_default_value=args.mustache_remover_default_value,
                                    directory=None, match=None, ignore=args.ignore, ignore_re=args.ignore_re)
    return validator.validate(
        args.filenames,
        errors_only=args.error_only,
        stack_size=args.stack_size,
        remove_mustaches=args.remove_mustaches,
    )


class CustomHTMLValidator(Validator):

    def __init__(self, mustache_remover_copy_ext, mustache_remover_default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mustache_remover_copy_ext = mustache_remover_copy_ext
        self.mustache_remover_default_value = mustache_remover_default_value

    def validate(self, files=None, remove_mustaches=False, **kwargs):
        if not files:
            files = self.all_files()
        if remove_mustaches:
            with generate_mustachefree_tmpfiles(files, copy_ext=self.mustache_remover_copy_ext, default_value=self.mustache_remover_default_value) as files:
                return super().validate(files, **kwargs)
        else:
            return super().validate(files, **kwargs)

@contextlib.contextmanager
def generate_mustachefree_tmpfiles(filepaths, copy_ext, default_value):
    tmplt_compiler = PybarCompiler()
    mustachefree_tmpfiles = []

    for filepath in filepaths:
        tmpfile = filepath + copy_ext
        shutil.copyfile(filepath, tmpfile)
        with open(filepath, 'r') as src_file:
            template_content = src_file.read()
            try:
                compiled_template = tmplt_compiler.compile(template_content)
                code_without_mustaches = compiled_template(PybarConstantContext(default_value))
            except PybarsError as error:
                raise MustacheSubstitutionFail('For HTML template file {}'.format(filepath)) from error
            with open(tmpfile, 'w+') as new_tmpfile:
                new_tmpfile.write(code_without_mustaches)
        mustachefree_tmpfiles.append(tmpfile)

    try:
        yield mustachefree_tmpfiles
    finally:
        for tmpfile in mustachefree_tmpfiles:
            os.remove(tmpfile)

class PybarConstantContext:
    def __init__(self, default):
        self.default = default
    def __getattribute__(self, name):
        if name == 'default' or name.startswith('__'):
            return object.__getattribute__(self, name)
        return self
    def __str__(self):
        return str(self.default)

class MustacheSubstitutionFail(Exception):
    pass


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
