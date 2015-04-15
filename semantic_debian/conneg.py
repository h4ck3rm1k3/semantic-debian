
formats = [('ttl', 'turtle', 'text/turtle'),
           ('xml', 'xml', 'application/rdf+xml'),
           ('n3', 'n3', 'text/n3'),
          ]

def negotiate(accept):
    for f in formats:
        if f[2] in accept:
            return f[0]
    return "html"

def get_serializer(ext):
    for f in formats:
        if ext == f[0]:
            return f[1]

def get_mime_type(ext):
    for f in formats:
        if ext == f[0]:
            return f[2]

