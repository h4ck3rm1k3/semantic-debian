import re

from sqlalchemy import create_engine, MetaData, distinct
from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy import Table

engine = create_engine('postgresql+psycopg2://public-udd-mirror:public-udd-mirror@public-udd-mirror.xvm.mit.edu/udd',
        client_encoding='utf8')
conn = engine.connect()
metadata = MetaData()

sources_table = Table('sources', metadata,
    autoload=True, autoload_with=engine
)

vcswatch_table = Table('vcswatch', metadata,
    autoload=True, autoload_with=engine
)

uploaders_table = Table('uploaders', metadata,
    autoload=True, autoload_with=engine
)

packages_table = Table('packages', metadata,
    autoload=True, autoload_with=engine
)

rfc822_extract = re.compile('^(.*) <(.*)>$')

def get_all_releases():
    columns = [distinct(sources_table.c.release)]
    query = select(columns)
    result = conn.execute(query)
    ret = [x[0] for x in result]
    return ret

def get_all_projects():
    columns = [sources_table.c.source,
               sources_table.c.maintainer_name,
               sources_table.c.maintainer_email,
               sources_table.c.uploaders]
    query = select(columns).order_by(desc(sources_table.c.version))
    result = conn.execute(query)
    ret = []
    seen = set()
    for row in result:
        if row[0] in seen:
            continue
        seen.add(row[0])
        p = dict(zip([c.name for c in columns], row))
        if p['uploaders'] != None:
            uploaders = []
            for uploader in [u.strip() for u in p['uploaders'].split(',')]:
                uploader_matches = rfc822_extract.match(uploader)
                if uploader_matches != None:
                    uploaders.append(uploader_matches.group(1,2))
            p['uploaders'] = uploaders
        ret.append(p)
    return ret

def get_all_sources():
    columns = [sources_table.c.source,
               sources_table.c.version,
               sources_table.c.release]
    query = select(columns)
    result = conn.execute(query)
    ret = []
    for row in result:
        s = dict(zip([c.name for c in columns], row))
        ret.append(s)
    return ret

def get_all_repositories():
    columns = [vcswatch_table.c.source,
               vcswatch_table.c.vcs,
               vcswatch_table.c.url,
               vcswatch_table.c.branch,
               vcswatch_table.c.browser]
    query = select(columns).order_by(desc(vcswatch_table.c.version))
    result = conn.execute(query)
    ret = []
    seen = set()
    for row in result:
        if row[0] in seen:
            continue
        seen.add(row[0])
        r = dict(zip([c.name for c in columns], row))
        if r['vcs'] != None and r['vcs'] != "Cvs":
            ret.append(r)
    return ret

def get_all_maintainers():
    seen = set()
    ret = []
    ### Listed as uploader, from the uploaders table
    columns = [uploaders_table.c.name,
               uploaders_table.c.email]
    query = select(columns)
    result = conn.execute(query)
    for row in result:
        if row[1] not in seen:
            seen.add(row[1])
            m = dict(zip([c.name for c in columns], row))
            ret.append(m)
    ### Listed as maintainer, from the sources table
    columns = [sources_table.c.maintainer_name,
               sources_table.c.maintainer_email]
    query = select(columns)
    result = conn.execute(query)
    for row in result:
        if row[1] not in seen:
            seen.add(row[1])
            m = dict(zip(["name", "email"], row))
            ret.append(m)
    return ret

def get_all_packages():
    columns = [packages_table.c.package,
               packages_table.c.version,
               packages_table.c.architecture,
               packages_table.c.release,
               packages_table.c.source,
               packages_table.c.description,
               packages_table.c.depends,
               packages_table.c.suggests,
               packages_table.c.recommends,
               packages_table.c.pre_depends]
    query = select(columns)
    result = conn.execute(query)
    ret = []
    for row in result:
        p = dict(zip([c.name for c in columns], row))
        for i in ['depends', 'recommends', 'suggests']:
            if p[i] != None:
                p[i] = [x.strip() for x in p[i].split(",")]
        ret.append(p)
    return ret
