
from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS, FOAF, DOAP

if 'namespace_manager' not in vars():
    base_url    = "http://rdf.debian.net/"

    SCHEMA = Namespace("http://schema.org/")
    SPDX   = Namespace("http://www.spdx.org/rdf/terms#")
    ADMS   = Namespace("http://www.w3.org/ns/adms#")
    ADMSSW = Namespace("http://purl.org/adms/sw/")

    PROJECT    = Namespace(base_url + "project/")
    PACKAGE    = Namespace(base_url + "package/")
    RELEASE    = Namespace(base_url + "release/")
    MAINTAINER = Namespace(base_url + "maintainer/")
    TRACKER    = Namespace("http://tracker.debian.org/pkg/")
    SRCPKG     = Namespace("http://packages.debian.org/src:")
    SCREENSHOTS= Namespace("http://screenshots.debian.net/package/")
    DDPO       = Namespace("https://qa.debian.org/developer.php?login=")
    namespace_manager = NamespaceManager(Graph())

    namespace_manager.bind('adms', ADMS, override=False)
    namespace_manager.bind('admssw', ADMSSW, override=False)
    namespace_manager.bind('dcterms', DCTERMS, override=False)
    namespace_manager.bind('doap', DOAP, override=False)
    namespace_manager.bind('foaf', FOAF, override=False)
    namespace_manager.bind('owl', OWL, override=False)
    namespace_manager.bind('rdf', RDF, override=False)
    namespace_manager.bind('rdfs', RDFS, override=False)
    namespace_manager.bind('schema', SCHEMA, override=False)
    namespace_manager.bind('spdx', SPDX, override=False)

