
from semantic_debian.core.store import graph

class Package:
    def __init__(self, package):
        self.uri = package
        self.triples = graph.triples( (package, None, None) )

