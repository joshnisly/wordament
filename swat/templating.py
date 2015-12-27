
import os

import jinja2
import jinja2.ext
import jinja2.nodes

import swat

class TemplateEngine:
    def __init__(self, static_path, swat_static_path, templates_path, urls):
        loader = jinja2.FileSystemLoader(templates_path)
        self.env = jinja2.Environment(loader=loader, extensions=[
            'jinja2.ext.autoescape',
            StaticFileExtension,
            ReverseExtension
        ], autoescape=True)
        self.env.reverse_urls = urls
        self.env.static_path = static_path
        self.env.swat_static_path = swat_static_path

    def get_template_text(self, url_prefix, template_name, variables):
        template = self.env.get_template(template_name)
        self.env.url_prefix = url_prefix
        return template.render(**variables)

class StaticFileExtension(jinja2.ext.Extension):
    tags = set(['static', 'swat_static'])

    def __init__(self, environment):
        super(StaticFileExtension, self).__init__(environment)
        environment.extend(
            static_path=None
        )

    def parse(self, parser):
        token = parser.stream.next()

        arg = parser.parse_expression() # filename

        if str(token) == 'static':
            path = jinja2.nodes.EnvironmentAttribute('static_path')
        else:
            path = jinja2.nodes.EnvironmentAttribute('swat_static_path')

        return jinja2.nodes.Output([self.call_method('_get_url', [
            jinja2.nodes.Const(str(token)),
            jinja2.nodes.EnvironmentAttribute('url_prefix'),
            path,
            arg
        ])]).set_lineno(token.lineno)

    def _get_url(self, static_tag, url_prefix, static_path, rel_path):
        # Use the file's last modified time as the version
        path = os.path.join(static_path, rel_path)
        try:
            version = os.stat(path).st_mtime
        except OSError:
            # We try to get the modified time and handle failures
            # to avoid the overhead of first checking if the file exists.
            version = 0
        return '%s/%s/%i/%s' % (url_prefix, static_tag, version, rel_path)

class ReverseExtension(jinja2.ext.Extension):
    tags = set(['get_url'])

    def __init__(self, environment):
        super(ReverseExtension, self).__init__(environment)
        environment.extend(
            reverse_urls=None
        )

    def parse(self, parser):
        token = parser.stream.next()

        func_name = parser.parse_expression() # function name
        if not isinstance(func_name.value, basestring):
            parser.fail('The function name must be a string.')

        args = jinja2.nodes.Const([])
        kwargs = jinja2.nodes.Const({})
        if parser.stream.skip_if('comma'): # path_info args
            args = parser.parse_expression()

            if parser.stream.skip_if('comma'): # query string args
                kwargs = parser.parse_expression()

        return jinja2.nodes.Output([self.call_method('_get_url', [
            func_name,
            args,
            kwargs,
            jinja2.nodes.EnvironmentAttribute('url_prefix'),
        ])]).set_lineno(token.lineno)

    def _get_url(self, func_name, args, kwargs, url_prefix):
        url = swat.reverse(func_name, self.environment.reverse_urls,
                           args, kwargs)
        if not url:
            return '/completely_bogus_url/'

        return url_prefix + url
