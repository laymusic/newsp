#!/usr/bin/python
import mysql.connector
import dominate
from dominate.tags import *
from dominate.util import *
from datetime import *
import os

head = "http://localhost/~lconrad/newsp/"
filehead = "http://serpentpublications.org/~lconrad/"
html_head = "/home/lconrad/public_html/newsp/composerpages/"

def make_link(text, url):
    link = a(text, href=url)
    return link

def composer_link(id, last_name ):
    url = head + "composerpages/" + str(id) + ".html"
    link = make_link(last_name, url)
    return link

def piece_link(id, title):
    url = head + "piecepages/" + str(id) + ".html"
    link = make_link(title, url)
    return link

def book_link(id, title):
    if not id:
        return("")
    url = head + "bookpages/" + str(id) + ".html"
    link = make_link(title, url)
    return link

def full_composer_link(id, last_name, first_name, date_of_birth, date_of_death):
    url = head + "composerpages/"  + str(id) + ".html"
    full_name = "%s, %s (%s - %s)" % (last_name, first_name, date_of_birth, date_of_death)
    composer = make_link(full_name, url)
    return(composer)
 
def filename_link(text, directory, filename):
    # filenames are on serpentpublications.org
    url = filehead + directory + "/" + filename
    link = make_link(text, url)
    return link


def print_html(filename, html):
    f = open(filename, "w")
    f.write(str(html))
    f.close()
    return

def open_db():
    global cnx, cursor
    cnx = mysql.connector.connect(user='lconrad', password='jsb16851750', host='serpentpublications.org', database='musicpublish')
    cursor = cnx.cursor()
    query_string = "SET NAMES UTF8MB4;"
    cursor.execute(query_string)
    return(cursor)

def checkfile(filename):
    try:
        filestat = os.stat( filename )
    except:
        sys.stderr.write("db2htm.py: filename %s does not exist\n" % filename)
        return (0)
    t = filestat[ stat.ST_MTIME]
    s = filestat[ stat.ST_SIZE]
    return (s)

def long_line(id, cursor):
    query_string = ("select * from pcab_table where id=" + str(id)   + ";")
    result = cursor.execute(query_string)
    piece = cursor.fetchone()
    pieceprint = piece_link(piece[0],  piece[1])
    composer = full_composer_link(piece[2], piece[3], piece[4], piece[5], piece[6])
    pdf_link = filename_link("PDF", piece[8], piece[9])
    if piece[14]:
        parts = piece[14]
    else:
        parts = ""
    if piece[15]:
        lastmodified = piece[15].strftime("%x")
    else:
        lastmodified = ""
    if piece[16]:
        accesses = piece[16]
    else:
        accesses = ""
    if piece[17]:
        book = book_link(piece[17], piece[18])
    else:
        book = ""
    return (pieceprint, composer, pdf_link, parts, book, lastmodified, accesses)

def find_pieces(cid):
    query_string = "select * from pcab_table where composer_id = %d order by title;" % cid
    cursor.execute(query_string)
    value = cursor.fetchall()
    t = table()
    i = 1
    for piece in value:
        tuple = long_line(piece[0], cursor)
        with t:
            if i == 1:
                l = tr ()
                l += td(b('Title'))
                l += td(b('Composer'))
                l += td(b('PDF'))
                l += td(b('Parts'))
                l += td(b('Last Modified'))
                l += td(b('Accesses'))
                l += td(b('Book'))
            i += 1
            l = tr()
            for j in 0, 1, 2, 3, 5, 6, 4:
                l += td(tuple[j])
    return(t)

def write_composer_html(composer,  newonly): 
    cid = composer[0]
    composer_file = html_head + str(cid) + ".html"
    if newonly:
        filestat = checkfile(composer_file)
        if filestat:
            return()
    full_name = str(composer[1]) + " " + str(composer[2])
    chtml = dominate.document(title = full_name)
    with chtml.head:
        title = full_name
        raw('<meta charset="utf-8" />')
        link(rel='stylesheet', href='../newsp.css')
    composer_link = full_composer_link(composer[0], composer[2], composer[1], composer[3], composer[4])
    #book_list = find_books(composer[0])
    piece_table = find_pieces(composer[0])
    with chtml.body:
        h1(full_name)
        p("Composer: " , composer_link)
        if composer[7]:
            p("Comment: " , composer[7])
        if composer[6]:
            p(make_link("Website", composer[6]))
        #add book look up later
    chtml.body += piece_table
    print_html(composer_file, chtml)
    return()

    
def write_composers(cursor, newonly):
    query_string = "select * from composer;"
    composers = cursor.execute(query_string)
    value = cursor.fetchall()
    for composer in value:
        write_composer_html(composer, newonly)

newonly = 0
if len(sys.argv) > 1:
    if sys.argv[1] == '-n':
        newonly = 1
cursor = open_db()
write_composers( cursor, newonly)
    
