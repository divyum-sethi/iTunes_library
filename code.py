#code to parse iTunes' xml file and create a database
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect("trackdb.sqlite")
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Track;
CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);
CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);


CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    genre_id INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')
#to check if a specefic key is present under the tag
def lookup(parent, key):
    found = False
    for child in parent:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None


fname = "Library.xml"
stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')   #stores the list of all dicts under dict->dict
print('Dict count:', len(all))
for one in all:
    #to check if Track ID is in the tag
    if (lookup(one, 'Track ID') is None): continue

    name = lookup(one, 'Name')
    artist = lookup(one, 'Artist')
    album = lookup(one, 'Album')
    genre = lookup(one, 'Genre')
    count = lookup(one, 'Play Count')
    rating = lookup(one, 'Rating')
    length = lookup(one, 'Total Time')
    if name is None or artist is None or album is None  or genre is None:
        continue
    print(name, artist, album, count, rating, length)

    cur.execute('''INSERT OR IGNORE INTO Genre (name)
        VALUES  (?) ''', (genre,))
    cur.execute('''
        SELECT id FROM Genre WHERE name=?''', (genre,))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Artist (name)
    VALUES  (?) ''', (artist,))
    cur.execute('''
    SELECT id FROM Artist WHERE name=?''', (artist,))
    artist_id= cur.fetchone()[0]

    cur.execute('''
    INSERT OR IGNORE INTO Album (title, artist_id)
    VALUES (?,?)''' , (album,artist_id))

    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
        VALUES ( ?, ? )''', ( album, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, len, genre_id, rating, count) 
        VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( name, album_id, length, genre_id, rating, count ) )

conn.commit()
