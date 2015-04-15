
from flask import Response

from rdflib import URIRef

from semantic_debian.rdfviews import get_view

def rdf_response(uri, format, mimetype):
    view = get_view(uri)
    v = view(URIRef(uri))
    return Response(v.serialize(format=format), mimetype=mimetype)

