#!/usr/bin/python
import mysql.connector
import dominate
from dominate.tags import *
from dominate.util import *
from datetime import *
import os

head = "http://localhost/~lconrad/newsp/"
filehead = "http://serpentpublications.org/~lconrad/"
html_head = "/home/lconrad/public_html/newsp/bookpages/"

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

def long_line(id):
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

def find_pieces(bid):
    query_string = "select * from Book_Pieces_Table where book_id = %d order by Ordinal;" % bid
    cursor.execute(query_string)
    value = cursor.fetchall()
    t = table()
    i = 1
    for piece in value:
        ordinal = piece[2]
        tuple = long_line(piece[1])
        with t:
            if i == 1:
                l = tr ()
                l += td(b('Ordinal'))
                l += td(b('Title'))
                l += td(b('Composer'))
                l += td(b('PDF'))
                l += td(b('Parts'))
                l += td(b('Last Modified'))
                l += td(b('Accesses'))
            i = i + 1
            l = tr()
            l += td(str(ordinal))
            l += td(tuple[0])
            l += td(tuple[1])
            l += td(tuple[2])
            l += td(tuple[3])
            l += td(tuple[5])
            l += td(tuple[6])
        i += 1
    return(t)

def write_book_html(book): 
    bid = book[0]
    book_file = html_head + str(bid) + ".html"
    book_title = book[1]
    bhtml = dominate.document(title = book_title)
    with bhtml.head:
        title = book_title
        raw('<meta charset="utf-8" />')
        link(rel='stylesheet', href='../newsp.css')
    book_link = make_link(book_title, book_file)
    query_string = "select * from composer where composer_id = %d" % book[2]
    value = cursor.execute(query_string)
    composer = cursor.fetchone()
    composer_link = full_composer_link(composer[0], composer[2], composer[1], composer[3], composer[4])
    piece_table = find_pieces(book[0])
    with bhtml.body:
        h1(book_title)
        p(book_link)
        p("Composer: " , composer_link)
        if book[9]:
            p("Comment: " , book[9])
        if book[6]:
            pdf_link = filename_link("PDF", book[5], book[6])
        if book[7]:
            midi_link = filename_link("MIDI", book[5], book[7])
        if book[8]:
            source_link = filename_link("Source", book[5], book[8])
        if book[10]:
            make_link("More information", book[10])
        if book[11]:
            p(make_link("Buy this book", book[11]), " at ",  make_link("Lulu.com", "http://lulu.com/spotlight/laymusic"))
    bhtml.body += piece_table
    print_html(book_file, bhtml)
    return()

    
def write_books(cursor):
    query_string = "select * from book;"
    composers = cursor.execute(query_string)
    value = cursor.fetchall()
    for book in value:
        write_book_html(book)

cursor = open_db()
write_books( cursor)
    
