
from rdflib.resource import Resource

from semantic_debian.store import graph
from semantic_debian.namespaces import DOAP, FOAF

from flask import render_template

def preprocess_resource(uri):
    r = graph.resource(uri)
    name = uri
    description = "No description available"
    for x in r[DOAP.description]:
        description = x
        break
    for x in r[DOAP.name]:
        name = x
        break
    for x in r[FOAF.name]:
        name = x
        break
    p_o = []
    for p, o in r.predicate_objects():
        if isinstance(o, Resource):
            o_type = "resource"
            o_qname = o.identifier
            o_value = o.identifier
        else:
            o_type = "literal"
            o_qname = None
            o_value = str(o)
        p_o.append( (str(p.identifier), p.qname(), o_type, o_qname, o_value) )
    p_o.sort(key = lambda t: t[1])
    return {'uri': uri,
            'name': name,
            'path': uri.split('/')[3:],
            'description': description,
            'p_o': p_o}

def html_response(uri):
    preprocessed_resource = preprocess_resource(uri)
    return render_template('rdf.html', resource=preprocessed_resource, title=preprocessed_resource['name'], breadcrumb=' / browse / ' + ' / '.join(preprocessed_resource['path']))

