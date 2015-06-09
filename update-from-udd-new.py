from rdflib import Graph, Literal, Namespace, URIRef, BNode
from urllib.parse import quote
from hashlib import sha1

from semantic_debian.udd2 import get_all_projects, get_all_sources, get_all_repositories, get_all_releases, get_all_maintainers, get_all_packages

from semantic_debian.namespaces import namespace_manager
from semantic_debian.namespaces import RDF
from semantic_debian.namespaces import RDFS
from semantic_debian.namespaces import OWL
from semantic_debian.namespaces import DCTERMS
from semantic_debian.namespaces import FOAF
from semantic_debian.namespaces import DEPS
from semantic_debian.namespaces import DOAP
from semantic_debian.namespaces import SCHEMA
from semantic_debian.namespaces import ADMS
from semantic_debian.namespaces import ADMSSW
from semantic_debian.namespaces import SPDX
from semantic_debian.namespaces import PROJECT
from semantic_debian.namespaces import SOURCE
from semantic_debian.namespaces import PACKAGE
from semantic_debian.namespaces import RELEASE
from semantic_debian.namespaces import MAINTAINER
from semantic_debian.namespaces import REPOSITORY
from semantic_debian.namespaces import TRACKER
from semantic_debian.namespaces import SRCPKG
from semantic_debian.namespaces import SCREENSHOTS
from semantic_debian.namespaces import DDPO

########## TRIPLE GENERATION FUNCTIONS #########################################

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

relationships = {
        'depends': DEPS['runtime-requirement'],
        'recommends': DEPS['runtime-recommendation'],
        'suggests': DEPS['runtime-suggestion'],
}

def add_release_triples(g, d):
    if "-" in d:
        parent = RELEASE[d.split("-")[0]]
        g.add( (parent, ADMSSW.includedAsset, RELEASE[d]) )
        g.add( (RELEASE[d], DCTERMS.isPartOf, parent) )
        g.add( (RELEASE[d], ADMSSW.project, debian) )
    else:
        g.add( (debian, DOAP.release, RELEASE[d]) )
        g.add( (RELEASE[d], ADMSSW.project, debian) )
    g.add( (RELEASE[d], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (RELEASE[d], DOAP.name, Literal("Debian " + d)) )

def add_project_triples(g, p):
    g.add( (PROJECT[p['source']], RDF.type, ADMSSW.SoftwareProject) )
    g.add( (PROJECT[p['source']], DOAP.name, Literal("Debian " + p['source'] + " packaging")) )
    g.add( (PROJECT[p['source']], DOAP.shortdesc, Literal("Maintenance of " + p['source'] + " packaging in Debian", lang="en")) )
    g.add( (PROJECT[p['source']], DOAP.homepage, TRACKER[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP['download-page'], SRCPKG[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP.screenshots, SCREENSHOTS[p['source']]) )
    g.add( (PROJECT[p['source']], DOAP.platform, Literal('dpkg')) )

    # Add maintainer
    g.add( (PROJECT[p['source']], DOAP.maintainer,
        MAINTAINER[quote(p['maintainer_email'])]) )

    # Add uploaders
    if p['uploaders'] != None:
        for u in p['uploaders']:
            g.add( (PROJECT[p['source']], DOAP.developer, MAINTAINER[quote(u[1])]) )

def add_source_triples(g, s):
    identifier = s['source'] + "_" + s['version']
    g.add( (SOURCE[identifier], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (SOURCE[identifier], RDFS.label, Literal(s['source'] + "-" + s['version'] + " (source package)")))
    g.add( (SOURCE[identifier], ADMSSW.project, PROJECT[s['source']]) )
    g.add( (SOURCE[identifier], DCTERMS.isPartOf, RELEASE[s['release']]) )
    g.add( (SOURCE[identifier], DOAP.revision, Literal(s['version'])) )
    g.add( (SOURCE[identifier], DOAP.platform, Literal('dpkg')) )
    g.add( (RELEASE[s['release']], ADMSSW.includedAsset, SOURCE[identifier]) )
    g.add( (PROJECT[s['source']], DOAP.release, SOURCE[identifier]) )

def add_repository_triples(g, r):
    ## TODO: Add branch information somehow
    repository = REPOSITORY[r['source']]
    g.add( ( repository, RDF.type, repotype[r['vcs']]) )
    if r['url'] != None:
        if " " in r['url'] or "<" in r['url'] or ">" in r['url'] or "{" in r['url']:
            print("W: VCS URL for {} ({}) contains a bad character, ignoring this URL".format(r['source'], r['url'],))
        else:
            g.add( (repository, DOAP['anon-root'], URIRef(r['url'])) )
    if r['browser'] != None:
        if " " in r['browser'] or "<" in r['browser'] or ">" in r['browser'] or "{" in r['browser']:
            print("W: VCS Browser URL for {} ({}) contains a bad character, ignoring this URL".format(r['source'], r['browser'],))
        else:
            g.add( (repository, DOAP.browse, URIRef(r['browser'])) )
    g.add( (PROJECT[r['source']], DOAP.repository, repository ) )

def add_maintainer_triples(g, m):
    g.add( (MAINTAINER[quote(m['email'])], RDF.type, FOAF.Agent) )
    g.add( (MAINTAINER[quote(m['email'])], FOAF.name, Literal(m['name'])) )
    g.add( (MAINTAINER[quote(m['email'])], FOAF.mbox, URIRef('mailto:' + m['email'])) )
    g.add( (MAINTAINER[quote(m['email'])], FOAF.mbox_sha1sum, Literal(sha1(('mailto:' + m['email']).encode()).hexdigest())) )
    g.add( (MAINTAINER[quote(m['email'])], FOAF.homepage, DDPO[quote(m['email'])]) )

def add_package_triples(g, p):
    identifier = p['package'] + "_" + p['version'] + "_" + p['architecture']
    g.add( (PACKAGE[identifier], RDF.type, ADMSSW.SoftwareRelease) )
    g.add( (PACKAGE[identifier], RDFS.label, Literal(identifier + " (binary package)")) )
    g.add( (PACKAGE[identifier], DCTERMS.isPartOf, RELEASE[p['release']]) )
    g.add( (PACKAGE[identifier], DOAP.revision, Literal(p['version'])) )
    g.add( (PACKAGE[identifier], DEPS['source'], SOURCE[p['source']]) )
    g.add( (SOURCE[p['source']], DEPS['binary'], PACKAGE[identifier]))
    g.add( (RELEASE[p['release']], ADMSSW.includedAsset, PACKAGE[identifier]) )
    g.add( (PROJECT[p['source']], DOAP.release, PACKAGE[identifier]) )
    for i in relationships.keys():
        if p[i] != None:
            for j in p[i]:
                g.add( (PACKAGE[identifier], relationships[i], Literal(j, datatype=DEPS.DebianId)) )

########## PERFORM THE ACTUAL THINGS AND STUFF #################################

g = Graph()

print ("I: Importing triples from CPAN thingy")

g.load("perl.ttl", format="turtle")

print ("I: Importing triples from PyPI thingy")

g.load("pypi.ttl", format="turtle")

### Reset namespaces
g.namespace_manager = namespace_manager

print ("I: Generating the hardcoded Debian Project triples")

debian = URIRef('http://rdf.debian.net/debian')
g.add( (debian, RDF.type, ADMSSW.SoftwareProject) )
g.add( (debian, DOAP.name, Literal('The Debian Project')) )
g.add( (debian, DOAP.description, Literal('Debian is a free operating system ' +
   '(OS) for your computer. An operating system is the set of basic programs ' +
   'and utilities that make your computer run. Debian provides more than a ' +
   'pure OS: it comes with over 37500 packages, precompiled software bundled ' +
   'up in a nice format for easy installation on your machine.', lang="en")) )
g.add( (debian, DOAP.homepage, URIRef('http://www.debian.org/')) )

print ("I: Generating triples from UDD for Debian releases")

for d in get_all_releases():
    add_release_triples(g, d)

print ("I: Generating triples from UDD for packaging projects")

for p in get_all_projects():
    add_project_triples(g, p)

print ("I: Generating triples from UDD for source packages")

for s in get_all_sources():
    add_source_triples(g, s)

print ("I: Generating triples from UDD for VCS repositories")

for r in get_all_repositories():
    add_repository_triples(g, r)

print ("I: Generating triples from UDD for maintainers")

for m in get_all_maintainers():
    add_maintainer_triples(g, m)

print ("I: Generating triples from UDD for packages")

for p in get_all_packages():
    add_package_triples(g, p)

g.serialize('semdeb.ttl', format="n3")
