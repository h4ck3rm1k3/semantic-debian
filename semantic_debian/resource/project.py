
from semantic_debian.core.store import graph
from semantic_debian.core.namespaces import PROJECT

class Project:
    def __init__(self, name):
        self.triples = graph.triples( (PROJECT[name], None, None) )

