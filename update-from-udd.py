
import re

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from urllib import quote
from hashlib import sha1

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
from semantic_debian.core.namespaces import SCREENSHOTS
from semantic_debian.core.namespaces import DDPO

# Helpful things
rfc822_extract = re.compile('^(.*) <(.*)>$')

repotype = {
        'Svn': DOAP.SVNRepository,
        'Mtn': DOAP.Repository,
        'Hg':  DOAP.HgRepository,
        'Git': DOAP.GitRepository,
        'Arch': DOAP.ArchRepository,
        'Cvs': DOAP.CVSRepository,
        'Bzr': DOAP.BazaarBranch,
        'Darcs': DOAP.DarcsRepository,
        }

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

packages = udd.query("SELECT source, version, release, maintainer_name, maintainer_email, uploaders, vcs_type, vcs_url, vcs_browser FROM sources")

for package in packages:
    # Break out uploaders
    uploaders = []
    if package[5] != None:
        for u in package[5].split(', '):
            matches = rfc822_extract.match(u)
            if matches != None:
                uploaders.append(matches.group(1,2))
   
    g.add( (PROJECT[package[0]], RDF.type, ADMSSW.SoftwareProject) )
    g.add( (PROJECT[package[0]], DOAP.name, Literal("Debian " + package[0] + " packaging")) )
    g.add( (PROJECT[package[0]], DOAP.description, Literal("Maintenance of the " + package[0] + " source package in Debian")) )

    g.add( (PROJECT[package[0]], DOAP.homepage, TRACKER[package[0]]) )

    g.add( (PROJECT[package[0]], DOAP['download-page'], SRCPKG[package[0]]) )

    g.add( (PROJECT[package[0]], DOAP.release, PACKAGE[package[0] + "_" + package[1]]) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], ADMSSW.project, PROJECT[package[0]]) )

    vcs_type = package[6]
    vcs_url = package[7].split(" ")[0] if package[7] != None else None
    vcs_browser = package[8]

    if vcs_type != None and vcs_type != "Cvs":
        repository = URIRef('http://rdf.debian.net/repository/' + package[0])
        g.add( (repository, RDF.type, repotype[vcs_type]) )
        if vcs_url != None:
            if " " in vcs_url or "<" in vcs_url or ">" in vcs_url or "{" in vcs_url:
                print "W: VCS URL for %s (%s) contains a bad character, ignoring this URL" % (package[0], vcs_url,)
            else:
                g.add( (repository, DOAP['anon-root'], URIRef(vcs_url)) )
        if vcs_browser != None:
            if " " in vcs_browser or "<" in vcs_browser or ">" in vcs_browser or "{" in vcs_browser:
                print "W: VCS Browser URL for %s (%s) contains a bad character, ignoring this URL" % (package[0], vcs_browser,)
            else:
                g.add( (repository, DOAP.browse, URIRef(vcs_browser)) )
        g.add( (PROJECT[package[0]], DOAP.repository, repository ) )

    g.add( (RELEASE[package[2]], ADMSSW.includedAsset, PACKAGE[package[0] + "_" + package[1]]) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], DCTERMS.isPartOf, RELEASE[package[2]]) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], DOAP.revision, Literal(package[1])) )
    g.add( (PACKAGE[package[0] + "_" + package[1]], DOAP.platform, Literal('dpkg')) )
    g.add( (PROJECT[package[0]], DOAP.platform, Literal('dpkg')) )

    g.add( (PROJECT[package[0]], DOAP.screenshots, SCREENSHOTS[package[0]]) )

    g.add( (PROJECT[package[0]], DOAP.maintainer, MAINTAINER[quote(package[4])]) )
    g.add( (MAINTAINER[quote(package[4])], RDF.type, FOAF.Agent) )
    g.add( (MAINTAINER[quote(package[4])], FOAF.name, Literal(package[3])) )
    g.add( (MAINTAINER[quote(package[4])], FOAF.mbox, URIRef('mailto:' + package[4])) )
    g.add( (MAINTAINER[quote(package[4])], FOAF.mbox_sha1sum, Literal(sha1('mailto:' + package[4]).hexdigest())) )
    g.add( (MAINTAINER[quote(package[4])], FOAF.homepage, DDPO[quote(package[4])]) )

    for uploader in uploaders:
        g.add( (PROJECT[package[0]], DOAP.developer, MAINTAINER[quote(uploader[1])]) )
        g.add( (MAINTAINER[quote(uploader[1])], RDF.type, FOAF.Agent) )
        g.add( (MAINTAINER[quote(uploader[1])], FOAF.name, Literal(uploader[0])) )
        g.add( (MAINTAINER[quote(uploader[1])], FOAF.mbox, URIRef('mailto:' + uploader[1])) )
        g.add( (MAINTAINER[quote(uploader[1])], FOAF.mbox_sha1sum, Literal(sha1('mailto:' + uploader[1]).hexdigest())) )
        g.add( (MAINTAINER[quote(uploader[1])], FOAF.homepage, DDPO[quote(uploader[1])]) )

# Generate all release triples

# Generate all maintainer triples

# Generate all upstream triples

# Write out the RDFLib graph as a Turtle dump
g.serialize("semdeb.ttl", format='turtle')

# Make an xz compressed version of the dump

