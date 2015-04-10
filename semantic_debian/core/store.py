
from rdflib import Graph
from semantic_debian.core.namespaces import namespace_manager

if 'graph' not in vars():
    graph = Graph()
    graph.namespace_manager = namespace_manager
    graph.load('semdeb.ttl', format='turtle')

