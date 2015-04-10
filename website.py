
from flask import Flask, request, redirect, url_for, Response

from rdflib import Graph

from semantic_debian.resource.project import Project
from semantic_debian.resource.package import Package
from semantic_debian.resource.maintainer import Maintainer
from semantic_debian.core.namespaces import namespace_manager
from semantic_debian.core.namespaces import PROJECT

app = Flask(__name__)

def negotiate(accept):
    if "text/turtle" in accept:
        return "ttl"
    if "application/rdf+xml" in accept:
        return "xml"
    return "ttl"

@app.route("/project/<name>.ttl")
def project_turtle(name):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = Project(PROJECT[name])
    for triple in p.triples:
        g.add(triple)
    for package in p.getPackages():
        pa = Package(package)
        for triple in pa.triples:
            g.add(triple)
    for maintainer in p.getContributors():
        c = Maintainer(maintainer)
        for triple in c.triples:
            g.add(triple)
    return Response(g.serialize(format='turtle'), mimetype="text/turtle")

@app.route("/project/<name>.xml")
def project_rdfxml(name):
    g = Graph()
    g.namespace_manager = namespace_manager
    p = Project(PROJECT[name])
    for triple in p.triples:
        g.add(triple)
    for package in p.getPackages():
        pa = Package(package)
        for triple in pa.triples:
            g.add(triple)
    for maintainer in p.getContributors():
        c = Maintainer(maintainer)
        for triple in c.triples:
            g.add(triple)
    return Response(g.serialize(format='xml'), mimetype="application/rdf+xml")

@app.route("/project/<name>")
def project(name):
    f = negotiate(request.headers.get('Accept'))
    print "Decided to " + f
    if f == 'xml':
        return redirect(url_for('project_rdfxml', name=name), code=303)
    if f == 'ttl':
        return redirect(url_for('project_turtle', name=name), code=303)

if __name__ == "__main__":
    app.run(debug=True)

