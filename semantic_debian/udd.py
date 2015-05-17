
import psycopg2

class UltimateDebianDatabase:

    def __init__(self):
        username = "public-udd-mirror"
        password = "public-udd-mirror"
        host = "public-udd-mirror.xvm.mit.edu"
        port = 5432
        db = "udd"
        try:
            self.conn = psycopg2.connect("dbname=" + db + \
                        " user=" + username + \
                        " host=" + host + \
                        " password=" + password)
            print("I: Connected to Ultimate Debian Database")
        except:
            print("E: Error connecting to Ultimate Debian Database")
            raise
        self.conn.set_client_encoding('utf8')

    def query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_sources(self):
        query = "SELECT DISTINCT source " + \
            "FROM sources WHERE release='sid' AND " + \
            "( maintainer_email='debian-hams@lists.debian.org' OR " + \
            " section='hamradio' ) " + \
            "ORDER BY source"
        result = self.query(query)
        return [x[0] for x in result]

if 'udd' not in vars():
    udd = UltimateDebianDatabase()

