#!/usr/bin/env python3
import json, re, sys
from urllib import parse, request
import psycopg2

from semantic_debian.namespaces import DOAP, PROJECT, namespace_manager
from rdflib import Graph

REGEX_EXT = re.compile("\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))$", re.I)
DOAP_URL = "https://pypi.python.org/pypi?:action=doap&name=%s&version=%s"
doap_urls = {}

g = Graph()
g.namespace_manager = namespace_manager

try:
    conn = psycopg2.connect(host="public-udd-mirror.xvm.mit.edu", database="udd", 
    user="public-udd-mirror", password="public-udd-mirror")
    cursor = conn.cursor()
    cursor.execute("SELECT source, upstream_url FROM upstream WHERE upstream_url IS NOT NULL")
except Exception as e:
    sys.stderr.write("failed to get data from database;\n%s\n" % e)
    sys.exit(1)
for name, url in cursor.fetchall():
    parsed = parse.urlparse(url)
    if parsed.hostname == "pypi.debian.net":
        package_name = parsed.path[1:].split("/", 1)[0]
        version = parsed.path.rsplit("-", 1)[1]
        version = re.sub(REGEX_EXT, "", version)
        if "_" in version:
            version = version.split("_", 1)[0]
        package_doap_url = DOAP_URL % (package_name, version)
        doap_urls[name] = package_doap_url
        g.add( (PROJECT[name], DOAP.relation, package_doap_url) )

g.serialize("pypi.ttl", format="turtle")

doap_json = json.dumps(doap_urls, sort_keys=True, indent=4)
with open("pypi.json", "w") as out:
    out.write(doap_json)
