from __future__ import print_function
import argparse, contextlib, logging, os, shutil, sys
from jinja2 import Environment, FileSystemLoader
from jinja2.defaults import DEFAULT_NAMESPACE
from jinja2.runtime import Context
from jinja2.utils import concat
from six import raise_from, text_type
from pybars import Compiler as PybarCompiler, PybarsError
from html5validator.validator import Validator


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='filenames to check')
    parser.add_argument('--show-warnings', dest='error_only',
                        action='store_false', default=True)
    parser.add_argument('--ignore', action='append',
                        help='ignore messages containing the given strings')
    parser.add_argument('--ignore-re', action='append',
                        help='regular expression of messages to ignore')
    parser.add_argument('-l', action='store_const', dest='stack_size', const=2048,
                        help='run on larger files: sets Java stack size to 2048k')
    parser.add_argument('-ll', action='store_const', dest='stack_size', const=8192,
                        help='run on larger files: sets Java stack size to 8192k')
    parser.add_argument('-lll', action='store_const', dest='stack_size', const=32768,
                        help='run on larger files: sets Java stack size to 32768k')
    parser.add_argument('--remove-mustaches', action='store_true', default=False)
    parser.add_argument('--mustache-remover', choices=('pybar', 'jinja2'), default='pybar')
    parser.add_argument('--mustache-remover-env', action='append', nargs=2, help='Predefined KEY VALUE pair to substitute in the template')
    parser.add_argument('--mustache-remover-copy-ext', default='~~')
    parser.add_argument('--mustache-remover-default-value', default='DUMMY')
    parser.add_argument('--templates-include-dir', help='Required for Jinja2 templates that use the `include` directive'
                        ' - set it if you get a TemplateNotFound error')
    parser.add_argument('--log', default='WARNING',
                        help=('log level: DEBUG, INFO or WARNING '
                              '(default: WARNING)'))
    args = parser.parse_args(argv)

    if not args.filenames:
        return 0

    logging.basicConfig(level=getattr(logging, args.log))

    placeholder = Placeholder(args.mustache_remover_default_value, args.mustache_remover_env)
    validator = CustomHTMLValidator(mustache_remover_name=args.mustache_remover,
                                    mustache_remover_copy_ext=args.mustache_remover_copy_ext,
                                    mustache_remover_placeholder=placeholder,
                                    templates_include_dir=args.templates_include_dir,
                                    directory=None, match=None, ignore=args.ignore, ignore_re=args.ignore_re)
    return validator.validate(
        args.filenames,
        errors_only=args.error_only,
        stack_size=args.stack_size,
        remove_mustaches=args.remove_mustaches,
    )


class Placeholder:
    def __init__(self, default_value, env=None):
        self.default_value = default_value
        self.env = {k: eval(v) for k, v in env or ()}



class CustomHTMLValidator(Validator):

    def __init__(self, mustache_remover_name, mustache_remover_copy_ext, mustache_remover_placeholder, templates_include_dir, *args, **kwargs):
        Validator.__init__(self, *args, **kwargs)
        self.mustache_remover_copy_ext = mustache_remover_copy_ext
        self.mustache_remover_placeholder = mustache_remover_placeholder
        self.mustache_remover = Jinja2MustacheRemover(templates_include_dir) if mustache_remover_name == 'jinja2' else PybarMustacheRemover()

    def validate(self, files=None, remove_mustaches=False, **kwargs):
        if not files:
            files = self.all_files()
        if remove_mustaches:
            with generate_mustachefree_tmpfiles(files,
                                                self.mustache_remover,
                                                copy_ext=self.mustache_remover_copy_ext,
                                                placeholder=self.mustache_remover_placeholder) as tmpfiles:
                return Validator.validate(self, tmpfiles, **kwargs)
        else:
            return Validator.validate(self, files, **kwargs)

@contextlib.contextmanager
def generate_mustachefree_tmpfiles(filepaths, mustache_remover, copy_ext, placeholder):
    mustachefree_tmpfiles = []

    for filepath in filepaths:
        tmpfile = filepath + copy_ext
        shutil.copyfile(filepath, tmpfile)
        code_without_mustaches = mustache_remover.clean_template(filepath, placeholder)
        with open(tmpfile, 'w+') as new_tmpfile:
            new_tmpfile.write(code_without_mustaches)
        mustachefree_tmpfiles.append(tmpfile)

    try:
        yield mustachefree_tmpfiles
    finally:
        for tmpfile in mustachefree_tmpfiles:
            os.remove(tmpfile)


class PybarMustacheRemover:
    def __init__(self):
        self.tmplt_compiler = PybarCompiler()
    def clean_template(self, filepath, placeholder):
        with open(filepath, 'r') as src_file:
            template_content = text_type(src_file.read())
        try:
            compiled_template = self.tmplt_compiler.compile(template_content)
            return compiled_template(PybarPlaceholderContext(placeholder))
        except PybarsError as error:
            raise_from(MustacheSubstitutionFail('For HTML template file {}: {}'.format(filepath, error)), error)

class PybarPlaceholderContext:
    def __init__(self, placeholder):
        self.placeholder = placeholder
    def get(self, segment):
        if segment in self.placeholder.env:
            return self.placeholder.env[segment]
        return RecursiveDefaultPlaceholder(self.placeholder.default_value)


class Jinja2MustacheRemover:
    def __init__(self, templates_include_dir):
        self.template_loader_extra_paths = [templates_include_dir] if templates_include_dir else []
    def clean_template(self, filepath, placeholder):
        env = Jinja2PlaceholderEnvironment(placeholder, loader=FileSystemLoader([os.path.dirname(filepath)] + self.template_loader_extra_paths))
        template = env.get_template(os.path.basename(filepath))
        context = Jinja2PlaceholderContext(placeholder, env, DEFAULT_NAMESPACE.copy(), template.name, template.blocks)
        return concat(template.root_render_func(context))

class Jinja2PlaceholderEnvironment(Environment):
    def __init__(self, placeholder, *args, **kwargs):
        Environment.__init__(self, *args, **kwargs)
        self.placeholder = placeholder
    def getattr(self, *_, **__):
        return RecursiveDefaultPlaceholder(self.placeholder.default_value)

class Jinja2PlaceholderContext(Context):
    def __init__(self, placeholder, *args, **kwargs):
        Context.__init__(self, *args, **kwargs)
        self.placeholder = placeholder
    def call(self, *_, **__):
        return RecursiveDefaultPlaceholder(self.placeholder.default_value)
    def resolve_or_missing(self, key, missing=None):
        if key in self.placeholder.env:
            return self.placeholder.env[key]
        return RecursiveDefaultPlaceholder(self.placeholder.default_value)


class RecursiveDefaultPlaceholder:
    def __init__(self, default):
        self.default = default
    def __str__(self):
        return str(self.default)
    def __getattribute__(self, name):
        if name == 'default' or name.startswith('__'):
            return object.__getattribute__(self, name)
        return self
    def __iter__(self):
        return iter([self, self])
    def __getitem__(self, _):
        return self


class MustacheSubstitutionFail(Exception):
    pass


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
