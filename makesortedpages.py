#!/usr/bin/python
import mysql.connector
import dominate
from dominate.tags import *
from dominate.util import *
from datetime import *
head = "http://localhost/~lconrad/newsp/"
filehead = "http://serpentpublications.org/~lconrad/"
html_head = "/home/lconrad/public_html/newsp/sorts/"

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

def long_line(id, cursor):
    query_string = ("select * from pcab_table where id=" + str(id)   + ";")
    result = cursor.execute(query_string)
    piece = cursor.fetchone()
    composer_id = piece[2]
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
    return (pieceprint, composer, pdf_link, parts, book, lastmodified, accesses, composer_id)

    
    
    
def short_line(id, cursor):
    query_string = ("select id, title, composer_id, last_name from pcab_table where id=" + str(id)   + ";")
    result = cursor.execute(query_string)
    piece = cursor.fetchone()
    composer = composer_link(piece[2], piece[3])
    pieceprint = piece_link(piece[0], piece[1])
    return (composer, pieceprint)

def print_html(filename, html):
    f = open(filename, "w")
    f.write(str(html))
    f.close()
    return

def find_max(cursor):
    # don't include the 10 most recent pieces in the short recently modified list
    query_string = "select max(id) from piece;"
    result = cursor.execute(query_string)
    biggest = cursor.fetchone()
    lookat = biggest[0] - 10
    return(lookat)

def write_head(html, ptitle):
    with html:
        title = ptitle
        raw('<meta charset="utf-8" />')
        link(rel='stylesheet', href='../newsp.css')
        link(rel="shortcut icon", type="image/ico", href="images/favicon.ico")


def bynewest_short(cursor):
    ptitle = "Newest"
    bynewest_short = dominate.document(title = ptitle)
    query_string = ("select id from pcab_table order by id DESC  limit 10;")
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    write_head(bynewest_short.head, ptitle)
    i = 1
    t = table()
    for (id) in piece:
        newline = short_line(id[0], cursor)
        with t:
            if i == 1:
                l = tr()
                l+= td(b('Composer'))
                l+= td(b('Piece'))
            l = tr()
            l += td(newline[0])
            l += td(newline[1])
        i = i + 1
    bynewest_short.body += h1(ptitle)
    bynewest_short.body += t
    bynewest_short.body += br()
    with bynewest_short.body:
         make_link("More", "./bynewest-full.html")
    print_html(html_head + "bynewest-short.html", bynewest_short)
    return()

def bypopularity_short(cursor):
    ptitle = "By Popularity"
    bypopularity_short = dominate.document(title = "Popular")
    query_string = ("select id from pcab_table order by accesses DESC  limit 10;")
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    write_head(bypopularity_short.head, ptitle)
    i = 1
    t = table()
    for (id) in piece:
        newline = short_line(id[0], cursor)
        with t:
            if i == 1:
                l = tr()
                l+= td(b('Composer'))
                l+= td(b('Piece'))
            l = tr()
            l += td(newline[0])
            l += td(newline[1])
        i = i + 1
    bypopularity_short.body += h1(ptitle)
    bypopularity_short.body += t
    bypopularity_short.body += br()
    with bypopularity_short.body:
         make_link("More", "./bypopularity-full.html")
    print_html(html_head + "bypopularity-short.html", bypopularity_short)
    return()

def lastmodified_short(cursor):
    ptitle = "Recently Modified"
    lastmodified_short = dominate.document(title = ptitle)
    max_id = find_max(cursor)
    query_string = ("select id from pcab_table where id < %d order by lastmodified DESC  limit 10;" % max_id  )
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    write_head(lastmodified_short.head, ptitle)
    i = 1
    t = table()
    for (id) in piece:
        newline = short_line(id[0], cursor)
        with t:
            if i == 1:
                l = tr()
                l+= td(b('Composer'))
                l+= td(b('Piece'))
            l = tr()
            l += td(newline[0])
            l += td(newline[1])
        i = i + 1
    lastmodified_short.body += h1(ptitle)
    lastmodified_short.body += t
    lastmodified_short.body += br()
    with lastmodified_short.body:
         make_link("More", "./lastmodified-full.html")
    print_html(html_head + "lastmodified-short.html", lastmodified_short)
    return()


def lastmodified_full(cursor):
    # print all lines to lastmodified-full.html
    lastmodified_full = dominate.document(title = "Last modified")
    ptitle = "Sorted by last modification date"
    write_head(lastmodified_full.head, ptitle)
    with lastmodified_full.body:
        h1(ptitle)
    query_string = "select id from pcab_table order by lastmodified DESC;"
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    with lastmodified_full.add(body()).add(div(id='content')):
        t = table()
        with t:
            l = tr ()
            l += td(b('Title'))
            l += td(b('Composer'))
            l += td(b('PDF'))
            l += td(b('Parts'))
            l += td(b('Last Modified'))
            l += td(b('Accesses'))
            l += td(b('Book'))
            for id in piece:
                newline = long_line(id[0], cursor)
                l = tr()
                for j in 0, 1, 2, 3, 5, 6, 4:
                    l += td(newline[j])
    print_html(html_head + "lastmodified-full.html", lastmodified_full)
    return()

def bypopularity_full(cursor):
    # print all lines to lastmodified-full.html
    bypopularity_full = dominate.document(title = "By Popularity")
    ptitle = "Sorted by Number of accesses"
    write_head(bypopularity_full.head, ptitle)
    with bypopularity_full.body:
        h1(ptitle)
    query_string = "select id from pcab_table order by accesses DESC;"
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    with bypopularity_full.add(body()).add(div(id='content')):
        t = table()
        with t:
            l = tr ()
            l += td(b('Title'))
            l += td(b('Composer'))
            l += td(b('PDF'))
            l += td(b('Parts'))
            l += td(b('Last Modified'))
            l += td(b('Accesses'))
            l += td(b('Book'))
            for id in piece:
                newline = long_line(id[0], cursor)
                l = tr()
                for j in 0, 1, 2, 3, 5, 6, 4:
                    l += td(newline[j])
    print_html(html_head + "bypopularity-full.html", bypopularity_full)
    return()

def byparts(cursor):
    # print all lines to byparts.html
    bypartsp = dominate.document(title = "Parts")
    ptitle = "Sorted by number of parts"
    write_head( bypartsp.head, ptitle)
    with bypartsp.body:
        h1(ptitle)
    query_string = "select id from pcab_table order by parts, last_name, first_name, title;"
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    with bypartsp.add(body()).add(div(id='content')):
        t = table()
        with t:
            l = tr ()
            l += td(b('Title'))
            l += td(b('Composer'))
            l += td(b('PDF'))
            l += td(b('Parts'))
            l += td(b('Last Modified'))
            l += td(b('Accesses'))
            l += td(b('Book'))
            current = ""
            for id in piece:
                newline = long_line(id[0], cursor)
                if newline[3] != current:
                    current = newline[3]
                    l = tr(ID = str(current))
                else:
                    l = tr()
                for j in 0, 1, 2, 3,  5, 6, 4:
                    l += td(newline[j])
    print_html(html_head + "byparts.html", bypartsp)
    return()

def bynewest_full(cursor):
    bynewest = dominate.document(title = "Date Added")
    ptitle = "Sorted by date added"
    write_head( bynewest.head, ptitle)
    with bynewest.body:
        h1(ptitle)
    query_string = "select id from pcab_table order by id  DESC;"
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    with bynewest.add(body()).add(div(id='content')):
        t = table()
        with t:
            l = tr ()
            l += td(b('Title'))
            l += td(b('Composer'))
            l += td(b('PDF'))
            l += td(b('Parts'))
            l += td(b('Last Modified'))
            l += td(b('Accesses'))
            l += td(b('Book'))
            for id in piece:
                newline = long_line(id[0], cursor)
                l = tr()
                for j in 0, 1, 2, 3,  5, 6, 4:
                    l += td(newline[j])
    print_html(html_head + "bynewest-full.html", bynewest)
    return()

def bycomposer(cursor):
    bycomposer = dominate.document(title = "Composer")
    ptitle = "Sorted by Composer"
    write_head( bycomposer.head, ptitle)
    with bycomposer.body:
        h1(ptitle)
    query_string = "select id from pcab_table order by last_name, first_name, title;"
    result = cursor.execute(query_string)
    piece = cursor.fetchall()
    composer_id = 0
    with bycomposer.add(body()).add(div(id='content')):
        t = table()
        with t:
            l = tr ()
            l += td(b('Title'))
            l += td(b('Composer'))
            l += td(b('PDF'))
            l += td(b('Parts'))
            l += td(b('Last Modified'))
            l += td(b('Accesses'))
            l += td(b('Book'))
            for id in piece:
                newline = long_line(id[0], cursor)
                if newline[7] != composer_id:
                    composer_id = newline[7]
                    l = tr(ID = str(composer_id))
                else:
                    l = tr()
                for j in 0, 1, 2, 3,  5, 6, 4:
                    l += td(newline[j])
    print_html(html_head + "bycomposer.html", bycomposer)
    return()


cnx = mysql.connector.connect(user='lconrad', password='jsb16851750', host='serpentpublications.org', database='musicpublish')
cursor = cnx.cursor()
query_string = "SET NAMES UTF8MB4;"
cursor.execute(query_string)
lastmodified_short(cursor)
lastmodified_full(cursor)
byparts(cursor)
bycomposer(cursor)
bynewest_short(cursor)
bynewest_full(cursor)
bypopularity_short(cursor)
bypopularity_full(cursor)
cursor.close()
cnx.close()
exit
