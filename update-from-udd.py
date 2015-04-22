
import re

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from urllib import quote
from hashlib import sha1

from semantic_debian.udd import udd
from semantic_debian.namespaces import namespace_manager
from semantic_debian.namespaces import RDF
from semantic_debian.namespaces import RDFS
from semantic_debian.namespaces import OWL
from semantic_debian.namespaces import DCTERMS
from semantic_debian.namespaces import FOAF
from semantic_debian.namespaces import DOAP
from semantic_debian.namespaces import SCHEMA
from semantic_debian.namespaces import ADMS
from semantic_debian.namespaces import ADMSSW
from semantic_debian.namespaces import SPDX
from semantic_debian.namespaces import PROJECT
from semantic_debian.namespaces import PACKAGE
from semantic_debian.namespaces import RELEASE
from semantic_debian.namespaces import MAINTAINER
from semantic_debian.namespaces import TRACKER
from semantic_debian.namespaces import SRCPKG
from semantic_debian.namespaces import SCREENSHOTS
from semantic_debian.namespaces import DDPO

## Helpful things
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

## Setup an RDFLib graph

g = Graph()
g.namespace_manager = namespace_manager

## We need to store maintainer, uploader and translator details for later

maintainers = []

## Generate Debian triples

# TODO: There should be translations for the description here.

debian = URIRef('http://rdf.debian.net/debian')
g.add( (debian, RDF.type, ADMSSW.SoftwareProject) )
g.add( (debian, DOAP.name, Literal('The Debian Project')) )
g.add( (debian, DOAP.description, Literal('Debian is a free operating system ' +
   '(OS) for your computer. An operating system is the set of basic programs ' +
   'and utilities that make your computer run. Debian provides more than a ' +
   'pure OS: it comes with over 37500 packages, precompiled software bundled ' +
   'up in a nice format for easy installation on your machine.', lang="en")) )
g.add( (debian, DOAP.homepage, URIRef('http://www.debian.org/')) )

## Generate all release triples

releases = [x[0] for x in udd.query("SELECT DISTINCT release FROM sources")]

for release in releases:
    if "-" in release:
        parent = RELEASE[release.split("-")[0]]
        g.add( (parent, ADMSSW.includedAsset, RELEASE[release]) )
        g.add( (RELEASE[release], DCTERMS.isPartOf, parent) )
        g.add( (RELEASE[release], ADMSSW.project, debian) )
    else:
        g.add( (debian, DOAP.release, RELEASE[release]) )
        g.add( (RELEASE[release], ADMSSW.project, debian) )
    g.add( (RELEASE[release], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (RELEASE[release], DOAP.name, Literal("Debian " + release)) )

## Generate all project triples

projects = [{'source': x[0],
             'maintainer_name': x[1],
             'maintainer_email': x[2],
             'uploaders': x[3],}
             for x in udd.query("SELECT source, maintainer_name, " +
                                "maintainer_email, uploaders FROM sources " +
                                "ORDER BY version DESC")]


# Keep track of projects we've already seen so only the latest version's
# details are used
seen_projects = []

for p in projects:
    if p['source'] in seen_projects:
        continue
    seen_projects.append(p['source'])
    # Basic project triples
    g.add( (PROJECT[p['source']], RDF.type, ADMSSW.SoftwareProject) )
    g.add( (PROJECT[p['source']], DOAP.name, Literal("Debian " + p['source'] + " packaging")) )
    g.add( (PROJECT[p['source']], DOAP.shortdesc, Literal("Maintenance of the " + p['source'] + " source package in Debian", lang="en")) )
    g.add( (PROJECT[p['source']], DOAP.homepage, TRACKER[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP['download-page'], SRCPKG[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP.screenshots, SCREENSHOTS[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP.platform, Literal('dpkg')) )

    # Add maintainer
    g.add( (PROJECT[p['source']], DOAP.maintainer, 
        MAINTAINER[quote(p['maintainer_email'])]) )
    maintainers.append( (p['maintainer_name'], p['maintainer_email'],) )

    # Add uploaders
    if p['uploaders'] != None:
        for u in p['uploaders'].split(', '):
            matches = rfc822_extract.match(u)
            if matches != None:
                u = matches.group(1,2)
                g.add( (PROJECT[p['source']], DOAP.developer, MAINTAINER[quote(u[1])]) )
                maintainers.append(u)

## Generate all maintainer triples

for maintainer in maintainers:
    name = maintainer[0]
    email = maintainer[1]
    g.add( (MAINTAINER[quote(email)], RDF.type, FOAF.Agent) )
    g.add( (MAINTAINER[quote(email)], FOAF.name, Literal(name)) )
    g.add( (MAINTAINER[quote(email)], FOAF.mbox, URIRef('mailto:' + email)) )
    g.add( (MAINTAINER[quote(email)], FOAF.mbox_sha1sum, Literal(sha1('mailto:' + email).hexdigest())) )
    g.add( (MAINTAINER[quote(email)], FOAF.homepage, DDPO[quote(email)]) )

## Generate all repository triples

# TODO: This should really use the vcswatch table instead.
# TODO: Add git branch information

repositories = [{'source': x[0],
                 'vcs_type': x[1],
                 'vcs_url': x[2].strip() if x[2] != None else None,
                 'vcs_browser': x[3].strip() if x[3] != None else None,}
                for x in udd.query("SELECT source, vcs_type, vcs_url, " +
                    "vcs_browser FROM sources WHERE release='sid'")]

for r in repositories:
    # Git things might have branch information included
    r['vcs_url'] = r['vcs_url'].split(" ")[0] if r['vcs_url'] != None else None

    if r['vcs_type'] != None and r['vcs_type'] != "Cvs":
        repository = URIRef('http://rdf.debian.net/repository/' + r['source'])
        g.add( (repository, RDF.type, repotype[r['vcs_type']]) )
        if r['vcs_url'] != None:
            if " " in r['vcs_url'] or "<" in r['vcs_url'] or ">" in r['vcs_url'] or "{" in r['vcs_url']:
                print "W: VCS URL for %s (%s) contains a bad character, ignoring this URL" % (r['source'], r['vcs_url'],)
            else:
                g.add( (repository, DOAP['anon-root'], URIRef(r['vcs_url'])) )
        if r['vcs_browser'] != None:
            if " " in r['vcs_browser'] or "<" in r['vcs_browser'] or ">" in r['vcs_browser'] or "{" in r['vcs_browser']:
                print "W: VCS Browser URL for %s (%s) contains a bad character, ignoring this URL" % (r['source'], r['vcs_browser'],)
            else:
                g.add( (repository, DOAP.browse, URIRef(r['vcs_browser'])) )
        g.add( (PROJECT[r['source']], DOAP.repository, repository ) )

## Generate all package release triples

releases = [{'source': x[0],
             'version': quote(x[1]),
             'release': x[2],}
             for x in udd.query("SELECT source, version, release FROM sources " +
                                "ORDER BY version DESC")]

for r in releases:
    g.add( (RELEASE[r['release']], ADMSSW.includedAsset, PACKAGE[r['source'] + "_" + r['version']]) )
    g.add( (PACKAGE[r['source'] + "_" + r['version']], ADMSSW.project, PROJECT['source']) )
    g.add( (PROJECT[r['source'], DOAP.project, PACKAGE[r['source'] + "_" + r['version']]) )
    g.add( (PACKAGE[r['source'] + "_" + r['version']], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (PACKAGE[r['source'] + "_" + r['version']], DCTERMS.isPartOf, RELEASE[r['release']]) )
    g.add( (PACKAGE[r['source'] + "_" + r['version']], DOAP.revision, Literal(r['version'])) )
    g.add( (PACKAGE[r['source'] + "_" + r['version']], DOAP.platform, Literal('dpkg')) )

## Generate all upstream triples

## Write out the RDFLib graph as a Turtle dump
g.serialize("semdeb.ttl", format='turtle')

## Make an xz compressed version of the dump

