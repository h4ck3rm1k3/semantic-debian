
from semantic_debian.core.store import graph

class Maintainer:
    def __init__(self, maintainer):
        self.uri = maintainer
        self.triples = graph.triples( (maintainer, None, None) )

