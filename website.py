
from flask import Flask, request, redirect, url_for, Response, render_template

from rdflib import Graph
from rdflib.resource import Resource

from urllib import quote

from semantic_debian.core.namespaces import namespace_manager
from semantic_debian.core.namespaces import PROJECT, MAINTAINER
from semantic_debian.core.namespaces import RELEASE, PACKAGE
from semantic_debian.core.namespaces import DOAP
from semantic_debian.core.store import graph
from semantic_debian.views import project_view, maintainer_view
from semantic_debian.views import release_view, package_view

app = Flask(__name__)

def negotiate(accept):
    if "text/plain" in accept:
        return "ttl"
    if "application/rdf+xml" in accept:
        return "xml"
    return "html"

def resource_template(uri):
    r = graph.resource(uri)
    name = uri
    description = "No description available"
    for x in r[DOAP.description]:
        description = x
        break
    for x in r[DOAP.name]:
        name = x
        break
    p_o = []
    for p, o in r.predicate_objects():
        if isinstance(o, Resource):
            o_type = "resource"
            try:
                o_qname = o.qname() if not o.qname().startswith('ns') else o.identifier
            except:
                o_qname = o.identifier
            o_value = o.identifier
        else:
            o_type = "literal"
            o_qname = None
            o_value = str(o)
        p_o.append( (str(p.identifier), p.qname(), o_type, o_qname, o_value) )
    p_o.sort(key = lambda t: t[1])
    return {'uri': uri,
            'name': name,
            'description': description,
            'p_o': p_o}

########### PROJECT PAGES ################

@app.route("/project/<name>.ttl")
def project_turtle(name):
    v = project_view(PROJECT[name])
    return Response(v.serialize(format='turtle'), mimetype="text/plain")

@app.route("/project/<name>.xml")
def project_rdfxml(name):
    v = project_view(PROJECT[name])
    return Response(v.serialize(format='xml'), mimetype="application/rdf+xml")

@app.route("/project/<name>.html")
def project_html(name):
    resource = resource_template(PROJECT[name])
    return render_template('rdf.html', resource=resource, title="%s (packaging project)" % (name,), breadcrumb=" / browse / project / %s" % (name,))

@app.route("/project/<name>")
def project(name):
    f = negotiate(request.headers.get('Accept'))
    if f == 'xml':
        return redirect(url_for('project_rdfxml', name=name), code=303)
    if f == 'ttl':
        return redirect(url_for('project_turtle', name=name), code=303)
    if f == 'html':
        return redirect(url_for('project_html', name=name), code=303)

########### MAINTAINER PAGES ################

@app.route("/maintainer/<email>.ttl")
def maintainer_turtle(email):
    v = maintainer_view(MAINTAINER[quote(email)])
    return Response(v.serialize(format='turtle'), mimetype="text/plain")

@app.route("/maintainer/<email>.xml")
def maintainer_rdfxml(email):
    v = maintainer_view(MAINTAINER[quote(email)])
    return Response(v.serialize(format='xml'), mimetype="application/rdf+xml")

@app.route("/maintainer/<email>.html")
def maintainer_html(email):
    resource = resource_template(MAINTAINER[quote(email)])
    return render_template('rdf.html', resource=resource, title="%s (Debian contributor)" % (email,), breadcrumb=" / browse / project / %s" % (email,))

@app.route("/maintainer/<email>")
def maintainer(email):
    f = negotiate(request.headers.get('Accept'))
    if f == 'xml':
        return redirect(url_for('maintainer_rdfxml', email=email), code=303)
    if f == 'ttl':
        return redirect(url_for('maintainer_turtle', email=email), code=303)
    if f == 'html':
        return redirect(url_for('maintainer_html', email=email), code=303)

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/urls")
def urls():
    return render_template("urls.html", title="URLs", breadcrumb=' / urls')

########### PACKAGE PAGES ################

@app.route("/package/<name>.ttl")
def package_turtle(name):
    v = package_view(PACKAGE[name])
    return Response(v.serialize(format='turtle'), mimetype="text/plain")

@app.route("/package/<name>.xml")
def package_rdfxml(name):
    v = package_view(PACKAGE[name])
    return Response(v.serialize(format='xml'), mimetype="application/rdf+xml")

@app.route("/package/<name>.html")
def package_html(name):
    resource = resource_template(PACKAGE[name])
    return render_template('rdf.html', resource=resource, title="%s (package release)" % (name,), breadcrumb=" / browse / package / %s" % (name,))

@app.route("/package/<name>")
def package(name):
    f = negotiate(request.headers.get('Accept'))
    if f == 'xml':
        return redirect(url_for('package_rdfxml', name=name), code=303)
    if f == 'ttl':
        return redirect(url_for('package_turtle', name=name), code=303)
    if f == 'html':
        return redirect(url_for('package_html', name=name), code=303)

########### RELEASE PAGES ################

@app.route("/release/<name>.ttl")
def release_turtle(name):
    v = release_view(RELEASE[name])
    return Response(v.serialize(format='turtle'), mimetype="text/plain")

@app.route("/release/<name>.xml")
def release_rdfxml(name):
    v = release_view(RELEASE[name])
    return Response(v.serialize(format='xml'), mimetype="application/rdf+xml")

@app.route("/release/<name>.html")
def release_html(name):
    resource = resource_template(RELEASE[name])
    return render_template('rdf.html', resource=resource, title="%s (Debian release)" % (name,), breadcrumb=" / browse / release / %s" % (name,))

@app.route("/release/<name>")
def release(name):
    f = negotiate(request.headers.get('Accept'))
    if f == 'xml':
        return redirect(url_for('release_rdfxml', name=name), code=303)
    if f == 'ttl':
        return redirect(url_for('release_turtle', name=name), code=303)
    if f == 'html':
        return redirect(url_for('release_html', name=name), code=303)

if __name__ == "__main__":
    app.run(debug=True)

