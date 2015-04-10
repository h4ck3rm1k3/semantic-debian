
from semantic_debian.core.store import graph
from semantic_debian.core.namespaces import DOAP
from semantic_debian.core.namespaces import SCHEMA

class Project:
    def __init__(self, project):
        self.uri = project
        self.triples = graph.triples( (project, None, None) )

    def getContributors(self):
        result = graph.triples( (self.uri, SCHEMA.contributor, None) )
        return [x[2] for x in result]

    def getPackages(self):
        result = graph.triples( (self.uri, DOAP.release, None) )
        return [x[2] for x in result]

