# -*- coding: utf-8 -*-

from urlparse import parse_qsl
from xml.sax.saxutils import escape, quoteattr
from wsgiref.util import FileWrapper
import re

__version__ = "0.3"


class App(object):
    url_re = re.compile("url(?::(.+))?")
    metaurl_re = re.compile("metaurl:(.+)")
    hash_re = re.compile("hash:(.+)")

    def __init__(self, form_path="form.html", error_path="error.html"):
        self.form_path = form_path
        self.error_path = error_path

    def __call__(self, environ, start_response):
        qst = tuple(parse_qsl(environ["QUERY_STRING"]))
        if not qst:
            status = '200 OK'  # HTTP Status
            headers = [('Content-type', 'text/html; charset=utf-8')]
            out = FileWrapper(open(self.form_path))
        else:
            try:
                out = [makelink(qst)]
                status = '200 OK'  # HTTP Status
                # HTTP Headers
                headers = [('Content-type', 'application/metalink4+xml')]
            except Exception, e:
                out = FileWrapper(open("error.html"))
                status = "400 Bad Request"
                headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return out

    @staticmethod
    def first_qst(qst, key):
        for k, v in qst:
            if k == key:
                return v
        return None

    @classmethod
    def getname(cls, qst):
        name = cls.first_qst(qst, "name")
        if name is None:
            raise ValueError("'name' dot found in qst")
        return quoteattr(name)

    @classmethod
    def getsize(cls, qst):
        size = cls.first_qst(qst, "size")
        if size:
            return "<size>%i</size>" % int(size)
        return ""

    @classmethod
    def geturls(cls, qst):
        outl = []
        for k, s in qst:
            m = cls.url_re.match(k)
            if m is not None:
                if m.group(1):
                    outl.append("<url location=%s>%s</url>" %
                                (quoteattr(m.group(1)), escape(s)))
                else:
                    outl.append("<url>%s</url>" % escape(s))
        return "\n".join(outl)

    @classmethod
    def getmetaurls(cls, qst):
        outl = []
        for k, s in qst:
            m = cls.metaurl_re.match(k)
            if m is not None:
                outl.append('<metaurl mediatype=%s>%s</metaurl>' %
                            (quoteattr(m.group(1)), escape(s)))
        return "\n".join(outl)

    @classmethod
    def gethashes(cls, qst):
        outl = []
        for k, s in qst:
            m = cls.hash_re.match(k)
            if m is not None:
                outl.append('<hash type=%s>%s</hash>' %
                            (quoteattr(m.group(1)), escape(s)))
        return "\n".join(outl)

    @classmethod
    def makelink(cls, qst):
        return """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
<generator>ToMeta/{version}</generator>
<file name={name}>
{size}
{urls}
{metaurls}
{hashes}
</file>
</metalink>""".format(version=__version__, name=cls.getname(qst),
                      size=cls.getsize(qst), urls=cls.geturls(qst),
                      metaurls=cls.getmetaurls(qst), hashes=cls.gethashes(qst))
