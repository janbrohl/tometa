#!/usr/bin/python2
from urlparse import parse_qsl
from xml.sax.saxutils import escape,quoteattr

def _first_qst(qst,key):
    for k,v in qst:
        if k==key:
            return v
    return None
    
def _getsize(qst):
    size=_first_qst(qst,"size")
    if size:
        return "<size>%i</size>"%int(size)
    return ""
    
def makelink(qst):
    return """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
<generator>ToMeta/0.1</generator>
<file name=%s>%s%s%s%s
</file>
</metalink>"""%(quoteattr(_first_qst(qst,"name")),
                _getsize(qst),
                "".join((("<url>%s</url>"%escape(s)) if ":"not in k else ("<url location=%s>%s</url>"%(quoteattr(k.split(":")[1]),escape(s)))) for k,s in qst if k.startswith("url")),
                "".join(('<metaurl mediatype=%s>%s</metaurl>'%(quoteattr(k.split(":")[1]),escape(s))) for k,s in qst if k.startswith("metaurl:")),
                "".join(('<hash type=%s>%s</hash>'% (quoteattr(k.split(":")[1]),escape(s))) for k,s in qst if k.startswith("hash:"))
                )

def application(environ,start_response):
    qst=tuple(parse_qsl(environ["QUERY_STRING"]))
    if not qst:
        status = '200 OK' # HTTP Status
        headers = [('Content-type', 'text/html')]
        out="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>ToMeta</title>
</head>
<body>
<h1>ToMeta <a href="http://en.wikipedia.org/wiki/Metalink">metalink4</a> generator</h1>
Simple form - you should better use self generated URLs for this.<br>
See <a href="./?badquery=badquery">Error Page</a> for help.<br>
<u><b>No input verification/validation! No waranty of any form! Use at your own risk.</b></u>
 <form action="./" method="get">
Filename:<input type="text" name="name"><br>
Filesize:<input type="text" name="size"><br>
URL:<input type="text" name="url"><br>
URL:<input type="text" name="url"><br>
URL:<input type="text" name="url"><br>
URL:<input type="text" name="url"><br>
Torrent:<input type="text" name="metaurl:torrent"><br>
MD5:<input type="text" name="hash:md5"><br>
SHA-256:<input type="text" name="hash:sha-256"><br>
<input type="submit" >
<input type="reset" >
</form>
</body>
</html>"""
    else:
        try:
            out=makelink(qst)
            status = '200 OK' # HTTP Status
            headers = [('Content-type', 'application/metalink4+xml')] # HTTP Headers
        except Exception,e:
            out="Bad query string!\nRequired: name\nOptional: size\nAny count: url, url:[location], hash:[type], metaurl:[mediatype]"
            status="400 Bad Request"
            headers = [('Content-type', 'text/plain')]
    start_response(status,headers)
    return [out]


