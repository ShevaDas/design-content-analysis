import MySQLdb as mdb
import sys
from HTMLParser import HTMLParser

# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def character_count(text):
    return len(text)

def word_count(text):
    return len(text.split())

# http://stackoverflow.com/questions/1518522/python-most-common-element-in-a-list
def mode(data):
    return max(set(data), key=data.count)

# http://stackoverflow.com/questions/15389768/standard-deviation-of-a-list
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        print "No data"
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        #raise ValueError('variance requires at least two data points')
        pass # don't do anything for now
    ss = _ss(data)
    pvar = ss/n # the population variance
    num = pvar**0.5
    return ("%.2f" % num)

def table_statistics(table_data): # table_data is a list of the data from some table
    data = {}
    character_data = {}
    word_data = {}

    character_lengths = [character_count(item) for item in table_data]

    character_data["Longest"] = max(character_lengths)
    character_data["Shortest"] = min(character_lengths)
    character_data["Mean"] = mean(character_lengths)
    character_data["Mode"] = mode(character_lengths)
    character_data["Std. Dev"] = pstdev(character_lengths)

    word_lengths = [word_count(item) for item in table_data]

    word_data["Longest"] = max(word_lengths)
    word_data["Shortest"] = min(word_lengths)
    word_data["Mean"] = mean(word_lengths)
    word_data["Mode"] = mode(word_lengths)
    word_data["Std. Dev"] = pstdev(word_lengths)

    data["Characters"] = character_data
    data["Words"] = word_data

    headers = ["Longest", "Shortest", "Mean", "Mode", "Std. Dev"]

    # print a formatted table of results
    row_format ="{:>10}" * (len(headers) + 1)
    print row_format.format("", *headers)

    for key, value in data.iteritems():
        sorted_values = [data[key][headers[i]] for i, val in enumerate(data[key].values())]
        print row_format.format(key, *sorted_values)

def search(dict, term):
    results_list = []
    for key in dict:
        if term in key:
            results_list.append(key)
    if not results_list:
        return None
    return results_list


host = raw_input("Enter host: ")
user = raw_input("Enter user: ")
password = raw_input("Enter password for user %s: " % user)
database = raw_input("Enter db name (only Drupal databases for now): ")

con = mdb.connect(host, user, password, database);

field_content = {}

with con:
    cur = con.cursor()
    cur.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'field_data%';")
    tables = [x[2] for x in cur]
    for table in tables:
        field_name = table.split("field_data_")[1] + "_value" # column name is the name of the table, minus the field_data_ prefix, plus _value
        query = "SELECT " + field_name + " FROM " + table
        try:
            cur.execute(query)
            value_list = [strip_tags(row[0]) for row in cur] # get rid of any HTML tags present
            if value_list: # not an empty list!
                field_content[table] = value_list
        except:
            pass

commands_list = "Commands: \"search [keyword]\", \"display [table name]\", \"all tables\", \"stats [table name]\", \"help\", \"quit\""
protip = "Tip: display and stats both accept table names without the field_data_field_ prefix (e.g., job_location instead of field_data_field_job_location)."

print commands_list + "\n" + protip
command = "input"

while command not in "quit":
    command = raw_input("> ")
    keyword = command.split()[0]
    keyword = keyword.lower().strip()
    if keyword in "search":
        search_term = command.split()[1]
        results = search(field_content, search_term)
        print str(results)
        analyze = raw_input("Analyze these tables? (y/n) ")
        if analyze.lower() in "y":
            for table in results:
                print table
                table_statistics(field_content[table])
    elif keyword in "all":
        print field_content.keys()
    elif keyword in "stats":
        table = command.split()[1]
        if "field_data_field_" not in table: # they provided an abbreviated version
            table = "field_data_field_" + table
        try:
            table_statistics(field_content[table])
        except KeyError:
            print "No data found for " + table
    elif keyword in "display":
        table = command.split()[1]
        if "field_data_field_" not in table: # they provided an abbreviated version
            table = "field_data_field_" + table
        try:
            print field_content[table]
        except KeyError:
            print "No data found for " + table
    elif keyword in "help":
        print commands_list + "\n" + protip
