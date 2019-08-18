import sqlite3
import shlex
from typing import TextIO, BinaryIO, Generator, Dict, Optional

from . import download
__all__ = ['download']

class MalformedFile(Exception):
    pass

GET_RAW = """
    SELECT download_url
    FROM library
    WHERE download_url IS NOT NULL;
    """

GET_ALL_URLS = """
    SELECT title, artist, album, download_url
    FROM library
    ORDER BY title ASC, artist ASC;
    """

MAKE_TEMPLATE = """
    SELECT title, artist, IFNULL(download_url, '')
    FROM library
    ORDER BY title ASC, artist ASC;
    """

SET_URL = """
    UPDATE library
    SET download_url = :url
    WHERE title = :title AND artist = :artist;
    """

def get_ytdl(database: str, file: TextIO) -> None:
    con = sqlite3.connect(database)
    cur = con.execute(GET_ALL_URLS)
    r = cur.fetchone()
    while r:
        title, artist, album, download_url = r
        if album:
            file.write(f'# "{title}" from "{album}" by "{artist}"\n')
        else:
            file.write(f'# "{title}" by "{artist}"\n')
        if download_url:
            file.write(f'{download_url}\n')
        else:
            file.write('; (No download URL)\n')
        r = cur.fetchone()

def get_raw(database: str, file: TextIO) -> None:
    con = sqlite3.connect(database)
    cur = con.execute(GET_RAW)
    r = cur.fetchone()
    while r:
        file.write(f'{r[0]}\n')
        r = cur.fetchone()

def template(database: str, file: TextIO) -> None:
    con = sqlite3.connect(database)
    cur = con.execute(MAKE_TEMPLATE)
    #quoted_res = list(map(lambda r: list(map(shlex.quote, r[0:3])), cur.fetchall()))
    TITLE_PLACEHOLDER = "<title>"
    ARTIST_PLACEHOLDER = "<artist>"
    URL_PLACEHOLDER = "<download url>"
    title_len = len(TITLE_PLACEHOLDER)
    artist_len = len(ARTIST_PLACEHOLDER)
    res = []
    r = cur.fetchone()
    while r:
        title = shlex.quote(r[0])
        artist = shlex.quote(r[1])
        url = shlex.quote(r[2])
        title_len = max(title_len, len(title))
        artist_len = max(artist_len, len(artist))
        res.append((title, artist, url))
        r = cur.fetchone()
    file.write("# {t:{t_l}} {a:{a_l}} {u}\n".format(
        t=TITLE_PLACEHOLDER, t_l=title_len - 2, a=ARTIST_PLACEHOLDER, a_l=artist_len, u=URL_PLACEHOLDER))
    for r in res:
        file.write("{r[0]:{t_l}} {r[1]:{a_l}} {r[2]}\n".format(
            r=r, t_l=title_len, a_l=artist_len
        ))
    con.close()

def get_lines(file: TextIO) -> Generator[Dict[str, Optional[str]], None, None]:
    for line in file:
        try:
            parsed_line = shlex.split(line, comments=True)
            if not parsed_line:
                continue
            title, artist, url = parsed_line
            yield {'title': title, 'artist': artist, 'url': url if url else None}
        except ValueError:
            raise MalformedFile(f"line `{line}` is incomplete")

def set_from_file(database: str, file: TextIO) -> None:
    con = sqlite3.connect(database)
    with con:
        con.executemany(SET_URL, get_lines(file))