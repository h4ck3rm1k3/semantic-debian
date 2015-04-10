
import re

from rdflib import Graph, Literal, Namespace, URIRef
from urllib import quote

from semantic_debian.core.udd import udd
from semantic_debian.core.namespaces import namespace_manager
from semantic_debian.core.namespaces import RDF
from semantic_debian.core.namespaces import RDFS
from semantic_debian.core.namespaces import OWL
from semantic_debian.core.namespaces import DCTERMS
from semantic_debian.core.namespaces import FOAF
from semantic_debian.core.namespaces import DOAP
from semantic_debian.core.namespaces import SCHEMA
from semantic_debian.core.namespaces import ADMS
from semantic_debian.core.namespaces import ADMSSW
from semantic_debian.core.namespaces import SPDX
from semantic_debian.core.namespaces import PROJECT
from semantic_debian.core.namespaces import PACKAGE
from semantic_debian.core.namespaces import RELEASE
from semantic_debian.core.namespaces import MAINTAINER
from semantic_debian.core.namespaces import TRACKER
from semantic_debian.core.namespaces import SRCPKG

# Helpful things
rfc822_extract = re.compile('^(.*) <(.*)>$')

# Setup an RDFLib graph

g = Graph()
g.namespace_manager = namespace_manager

# Generate Debian triples

debian = URIRef('http://rdf.debian.net/debian')
g.add( (debian, RDF.type, ADMSSW.SoftwareProject) )
g.add( (debian, DOAP.name, Literal('The Debian Project')) )
g.add( (debian, DOAP.homepage, URIRef('http://www.debian.org/')) )

# Generate all release triples

releases = [x[0] for x in udd.query("SELECT DISTINCT release FROM sources")]

for release in releases:
    g.add( (RELEASE[release], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (RELEASE[release], DOAP.name, Literal("Debian " + release)) )

# Generate all project triples

packages = udd.query("SELECT source, version, release, maintainer_name, maintainer_email, uploaders FROM sources")

for package in packages:
    # Break out maintainers
    contributors = [package[4]]
    if package[5] != None:
        uploaders = package[5].split(', ')
        for uploader in uploaders:
            matches = rfc822_extract.match(uploader)
            if matches != None:
                contributors.append(matches.group(2))
   
    g.add( (PROJECT[package[0]], RDF.type, ADMSSW.SoftwareProject) )
    g.add( (PROJECT[package[0]], DOAP.name, Literal("Debian " + package[0] + " packaging")) )
    g.add( (PROJECT[package[0]], DOAP.description, Literal("Maintenance of the " + package[0] + " source package in Debian")) )
    g.add( (PROJECT[package[0]], DOAP.homepage, TRACKER[package[0]]) )
    g.add( (PROJECT[package[0]], DOAP.homepage, SRCPKG[package[0]]) )

    g.add( (PROJECT[package[0]], DOAP.release, PACKAGE[package[0] + "_" + package[1]]) )

    g.add( (RELEASE[package[2]], ADMSSW.includedAsset, PACKAGE[package[0] + "_" + package[1]]) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], DCTERMS.isPartOf, RELEASE[package[2]]) )

    for contributor in [MAINTAINER[quote(x)] for x in contributors]:
        g.add( (PROJECT[package[0]], SCHEMA.contributor, contributor) )
        g.add( (contributor, RDF.type, FOAF.Agent) )

# Generate all release triples

# Generate all maintainer triples

# Generate all upstream triples

# Write out the RDFLib graph as a Turtle dump
g.serialize("semdeb.ttl", format='turtle')

# Make an xz compressed version of the dump

