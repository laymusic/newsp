#!/usr/bin/python
import mysql.connector
import dominate
import sys
from dominate.tags import *
from dominate.util import *
from datetime import *
import os

head = "http://localhost/~lconrad/newsp/"
filehead = "http://serpentpublications.org/~lconrad/"
html_head = "/home/lconrad/public_html/newsp/piecepages/"

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

def write_piece_html(piece,  newonly): 
    pid = piece[0]
    piece_file = html_head + str(pid) + ".html"
    if newonly:
        filestat = checkfile(piece_file)
        if filestat:
            return()
    phtml = dominate.document(title = piece[1])
    with phtml.head:
        title = piece[1]
        raw('<meta charset="utf-8" />')
    ptitle = piece_link(piece[0], piece[1])
    composer = full_composer_link(piece[2], piece[3], piece[4], piece[5], piece[6])
    if piece[17]:
        book = book_link(piece[17], piece[18])
    else:
        book = ""
    files = filename_link("PDF",piece[8], piece[9])
    if piece[10]:
        files += filename_link(" ABC", piece[8], piece[10])
    if piece[11]:
        files += filename_link(" MIDI", piece[8], piece[11])
    if piece[12]:
        files += filename_link(" Lilypond", piece[8], piece[12])
    query = "select * from accesses where piece = %d;" % piece[0]
    result = cursor.execute(query)
    value = cursor.fetchall()
    t = table()
    i = 1
    for file in value:
        with t:
            if i == 1:
                l =  tr()
                l += td(b("Filename"))
                l += td(b("Last Modified"))
                l += td(b("Number of Downloads"))
                i += 1
            l += tr()
            l += td(make_link(file[0], filehead + file[0]))
            if file[4]:
                l += td(file[4].strftime("%c"))
            l += td(file[1])
    with phtml.body:
        h1(piece[1])
        p("Title: ", ptitle)
        p("Composer: " , composer)
        if piece[17]:
            p("Book: ", book)
        p(files)
        if piece[14]:
            p("Parts: ",  piece[14])
        if piece[13]:
            p("Comment: " , piece[13])
        query = "select filename from previews where id = %d;" % piece[0]
        result = cursor.execute(query)
        value = cursor.fetchall()
        for image in value:
            filename =  filehead + piece[8] +  "/previews/" + str(image[0])
            himg = '<img src="%s", alt="part preview]">' % filename
            raw("<br/>" + himg)
    phtml.body += t
    print_html(piece_file, phtml)
    return()

    
def write_pieces(cursor, newonly):
    query_string = "select * from pcab_table;"
    pieces = cursor.execute(query_string)
    value = cursor.fetchall()
    for piece in value:
        write_piece_html(piece, newonly)

newonly = 0
if len(sys.argv) > 1:
    if sys.argv[1] == '-n':
        newonly = 1
cursor = open_db()
write_pieces( cursor, newonly)
    
