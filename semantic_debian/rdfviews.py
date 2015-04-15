
from rdflib import Graph, URIRef

from semantic_debian.store import graph
from semantic_debian.namespaces import namespace_manager
from semantic_debian.namespaces import DOAP

def get_view(uri):
    split_uri = uri.split('/')
    try:
        return views[split_uri[3]]
    except KeyError:
        return default_view

def project_view(uri):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = graph.resource(uri)
    for triple in graph.triples( (uri, None, None) ):
        g.add(triple)
    for k in [x.identifier for x in p[DOAP.release]]:
        for triple in graph.triples( (k, None, None) ):
            g.add(triple)
    for k in [x.identifier for x in p[DOAP.maintainer]]:
        for triple in graph.triples( (k, None, None) ):
            g.add(triple)
    for k in [x.identifier for x in p[DOAP.developer]]:
        for triple in graph.triples( (k, None, None) ):
            g.add(triple)
    for k in [x.identifier for x in p[DOAP.repository]]:
        for triple in graph.triples( (k, None, None) ):
            g.add(triple)
    return g

def default_view(uri):
    g = Graph()
    g.namespace_manager = namespace_manager
    for triple in graph.triples( (uri, None, None) ):
        g.add(triple)
    return g

views = {'project': project_view,}

