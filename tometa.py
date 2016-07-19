# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

try:
    from urlparse import parse_qsl
except ImportError:  # python3
    from urllib.parse import parse_qsl

from xml.sax.saxutils import escape, quoteattr
import re

__version__ = "0.4"


def wrap_file(environ, filelike, block_size=8192):
    # copied from
    # http://legacy.python.org/dev/peps/pep-3333/#optional-platform-specific-file-handling
    if 'wsgi.file_wrapper' in environ:
        return environ['wsgi.file_wrapper'](filelike, block_size)
    else:
        return iter(lambda: filelike.read(block_size), '')


class App(object):
    url_re = re.compile("url(?::(.+))?")
    metaurl_re = re.compile("metaurl:(.+)")
    hash_re = re.compile("hash:(.+)")

    def __init__(self, form_path="form.html", error_path="error.html"):
        self.form_path = form_path
        self.error_path = error_path

    def __call__(self, environ, start_response):
        qsl = parse_qsl(environ["QUERY_STRING"])
        if not qsl:
            status = '200 OK'  # HTTP Status
            headers = [('Content-type', 'text/html; charset=utf-8')]
            out = wrap_file(environ, open(self.form_path, "rb"))
        else:
            try:
                out = [self.makelink(qsl).encode("utf8")]
                status = '200 OK'  # HTTP Status
                # HTTP Headers
                headers = [('Content-type', 'application/metalink4+xml')]
            except Exception:
                out = wrap_file(environ, open(self.error_path, "rb"))
                status = "400 Bad Request"
                headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return out

    @staticmethod
    def first_qs(qsl, key):
        """
        return the first parameter value for key
        """
        for k, v in qsl:
            if k == key:
                return v
        return None

    @classmethod
    def getname(cls, qsl):
        """
        return the quoted name
        """
        name = cls.first_qs(qsl, "name")
        if name is None:
            raise ValueError("'name' not found in qst")
        return quoteattr(name)

    @classmethod
    def getsize(cls, qsl):
        """
        return a size element string
        """
        size = cls.first_qs(qsl, "size")
        if size:
            return "<size>%i</size>" % int(size)
        return ""

    @classmethod
    def geturls(cls, qsl):
        """
        return url element strings
        """
        outl = []
        for k, s in qsl:
            m = cls.url_re.match(k)
            if m is not None:
                if m.group(1):
                    outl.append("<url location=%s>%s</url>" %
                                (quoteattr(m.group(1)), escape(s)))
                else:
                    outl.append("<url>%s</url>" % escape(s))
        return "\n".join(outl)

    @classmethod
    def getmetaurls(cls, qsl):
        """
        return metaurl elements string
        """
        outl = []
        for k, s in qsl:
            m = cls.metaurl_re.match(k)
            if m is not None:
                outl.append('<metaurl mediatype=%s>%s</metaurl>' %
                            (quoteattr(m.group(1)), escape(s)))
        return "\n".join(outl)

    @classmethod
    def gethashes(cls, qsl):
        """
        return hash elements string
        """
        outl = []
        for k, s in qsl:
            m = cls.hash_re.match(k)
            if m is not None:
                outl.append('<hash type=%s>%s</hash>' %
                            (quoteattr(m.group(1)), escape(s)))
        return "\n".join(outl)

    @classmethod
    def makelink(cls, qsl):
        """
        return an actual metalink4 xml string
        """
        return """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
<generator>ToMeta/{version}</generator>
<file name={name}>
{size}
{urls}
{metaurls}
{hashes}
</file>
</metalink>""".format(version=__version__, name=cls.getname(qsl),
                      size=cls.getsize(qsl), urls=cls.geturls(qsl),
                      metaurls=cls.getmetaurls(qsl), hashes=cls.gethashes(qsl))

if __name__ == "__main__":
    import sys
    app = App()
    qsli = [s.lstrip("-").split("=", 1) for s in sys.argv[1:]]
    sys.stdout.write(app.makelink(qsli))
