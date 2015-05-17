from debian import deb822
import re

from semantic_debian.udd import udd

print "I: Mapping binary packages to source packages"

res = udd.query("SELECT package, source FROM packages")

sources = {}
for r in res:
    sources[r[0]] = r[1]

def lookup_source(pkg):
    if pkg in sources.keys():
        return sources[pkg]
    else:
        return None

print "I: Mapping Perl modules to CPAN distributions"

with open("/tmp/02packages.details.txt") as f:
    pkg_det = f.readlines()

spaces = re.compile(" +")

cpan_modules = {}

for line in pkg_det[9:]:
    row = spaces.split(line.strip())
    cpan_modules[row[0]] = row[2].split("/")[-1].rsplit("-", 1)[0]

print "I: Mapping source packages to Perl modules"

mapping = {}

def add_mapping(source, module):
    if source not in mapping.keys():
        mapping[source] = set()
    mapping[source].add(module)

with open('/tmp/PerlPackages') as debpkgs:
    for pkg in deb822.Packages.iter_paragraphs(debpkgs):
        if 'Perl-Modules' in pkg:
            source = lookup_source(pkg['Package'])
            if source == None:
                print "W: No source package was found for %s" % (pkg['Package'],)
                continue
            modules = [x.strip() for x in pkg['Perl-Modules'].strip().split('\n')]
            for module in [x.split(" ")[0].strip() for x in modules]:
                if module in cpan_modules.keys():
                    add_mapping(source, cpan_modules[module])
                    print "D: %s is in CPAN distribution %s" % (source, cpan_modules[module],)
                else:
                    print "D: %s not in CPAN" % (module,)

with open("perl.map", "w") as out:
    for source in mapping.keys():
        out.write(source + ": " + str(len(mapping[source])) + "   " + str(mapping[source]) + "\n")

