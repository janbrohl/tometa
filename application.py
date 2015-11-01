#!/usr/bin/python2
# -*- coding: utf-8 -*-

from urlparse import parse_qsl
from xml.sax.saxutils import escape, quoteattr
from wsgiref.util import FileWrapper
import re

__version__ = "0.2"

url_re = re.compile("url(?::(.+))?")
metaurl_re = re.compile("metaurl:(.+)")
hash_re = re.compile("hash:(.+)")


def _first_qst(qst, key):
    for k, v in qst:
        if k == key:
            return v
    return None


def _getname(qst):
    return quoteattr(_first_qst(qst, "name"))


def _getsize(qst):
    size = _first_qst(qst, "size")
    if size:
        return "<size>%i</size>" % int(size)
    return ""


def _geturls(qst):
    outl = []
    for k, s in qst:
        m = url_re.match(k)
        if m is not None:
            if m.group(1):
                outl.append("<url location=%s>%s</url>" %
                            (quoteattr(m.group(1)), escape(s)))
            else:
                outl.append("<url>%s</url>" % escape(s))
    return "\n".join(outl)


def _getmetaurls(qst):
    outl = []
    for k, s in qst:
        m = metaurl_re.match(k)
        if m is not None:
            outl.append('<metaurl mediatype=%s>%s</metaurl>' %
                        (quoteattr(m.group(1)), escape(s)))
    return "\n".join(outl)


def _gethashes(qst):
    outl = []
    for k, s in qst:
        m = hash_re.match(k)
        if m is not None:
            outl.append('<hash type=%s>%s</hash>' %
                        (quoteattr(m.group(1)), escape(s)))
    return "\n".join(outl)


def makelink(qst):
    return """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
<generator>ToMeta/{version}</generator>
<file name={name}>
{size}
{urls}
{metaurls}
{hashes}
</file>
</metalink>""".format(version=__version__, name=_getname(qst),
                      size=_getsize(qst), urls=_geturls(qst),
                      metaurls=_getmetaurls(qst), hashes=_gethashes(qst))


def application(environ, start_response):
    qst = tuple(parse_qsl(environ["QUERY_STRING"]))
    if not qst:
        status = '200 OK'  # HTTP Status
        headers = [('Content-type', 'text/html; charset=utf-8')]
        out = FileWrapper(open("form.html"))
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
