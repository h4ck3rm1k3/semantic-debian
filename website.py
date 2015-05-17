#!/usr/bin/env python3

from flask import Flask, request, redirect, url_for, Response, render_template
from werkzeug.routing import BaseConverter

from rdflib import URIRef
from rdflib.resource import Resource

from urllib.parse import quote

from semantic_debian.namespaces import DOAP
from semantic_debian.store import graph
from semantic_debian.conneg import negotiate, get_serializer, get_mime_type
from semantic_debian.html import html_response
from semantic_debian.rdf import rdf_response

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter

## Top Level Resource

@app.route('/debian.<regex("ttl|xml|n3"):ext>')
def top_level_resource_rdf(ext):
    return rdf_response('http://rdf.debian.net/debian',
            get_serializer(ext), get_mime_type(ext))

@app.route("/debian.html")
def top_level_resource_html():
    return html_response('http://rdf.debian.net/debian')

@app.route("/debian")
def top_level_resource():
    ext = negotiate(request.headers.get('Accept'))
    if ext == 'html':
        return redirect(url_for('top_level_resource_html'), code=303)
    return redirect(url_for('top_level_resource_rdf', ext=ext), code=303)

## Second Level Resources

@app.route('/<resource>/<name>.<regex("ttl|xml|n3"):ext>')
def resource_rdf(resource, name, ext):
    return rdf_response('http://rdf.debian.net/' + resource + '/' + quote(name),
            get_serializer(ext), get_mime_type(ext))

@app.route("/<resource>/<name>.html")
def resource_html(resource, name):
    uri = 'http://rdf.debian.net/' + resource + '/' + quote(name)
    return html_response(uri)

@app.route("/<resource>/<name>")
def resource(resource, name):
    ext = negotiate(request.headers.get('Accept'))
    if ext == 'html':
        return redirect(url_for('resource_html', resource=resource,
            name=name), code=303)
    return redirect(url_for('resource_rdf', resource=resource,
        name=name, ext=ext), code=303)

## Static Pages

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/usage")
def usage():
    return render_template("usage.html", title="Usage Documentation", breadcrumb=' / usage')

@app.route("/dataset")
def dataset():
    return render_template("dataset.html", title="Dataset Documentation", breadcrumb=' / dataset')

if __name__ == "__main__":
    app.run(debug=True)

