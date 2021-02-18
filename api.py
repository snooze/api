import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute ('SELECT * FROM books;').fetchall()
    return jsonify(all_books)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1>"

@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


@app.route('/api/v1/resources/computers', methods=['GET'])
def computer_search():
    """
    Example API using MSSQL connection
    """
    query_parameters = request.args
    ServerName = ''
    DatabaseName = ''
    MSSQLengine = sqlalchemy.create_engine('mssql://' + ServerName + "/" + DatabaseName + '?driver=SQL+Server+Native+Client+11.0' + '?trusted_connection=yes')
 
    computerName = query_parameters.get(‘ComputerName’)
    ipAddress = query_parameters.get(‘IPAddress’)
    
    query = 'SELECT * FROM TABLENAME WHERE'
    to_filter = []
 
    if computerName:
        query += ' ComputerName=? AND'
        to_filter.append(computerName)
    if ipAddress:
        query += ' IPAddress=? AND'
        to_filter.append(ipAddress)
    if not (computerName or ipAddress):
        return page_not_found(404)
    
    # Remove trailing space and "AND" from query, add terminating ;
    query = query[:-4] + ';'
 
    with MSSQLengine.connect() as con:
        resultproxy = con.execute(query, to_filter)
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
 
    return(jsonify(a))


app.run()