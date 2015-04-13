
from rdflib import Graph, URIRef

from semantic_debian.core.store import graph
from semantic_debian.core.namespaces import namespace_manager
from semantic_debian.core.namespaces import DOAP, SCHEMA

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

def maintainer_view(uri):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = graph.resource(uri)
    for triple in graph.triples( (uri, None, None) ):
        g.add(triple)
    for s, p, o in graph.triples( (None, SCHEMA.contributor, p.identifier) ):
        g.add( (s, p, o) )
    return g

def package_view(uri):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = graph.resource(uri)
    return g

def release_view(uri):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = graph.resource(uri)
    return g

