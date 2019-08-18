import sqlite3
from ._types import Song, SongList, SongDict
from ._metadata_analyser import get_metadata
from typing import Iterable, Generator
import logging

DIRECT_DELETE = """
    DELETE FROM library
    WHERE title = :title AND artist = :artist
    """

CREATE_TEMP_TABLE = """
    CREATE TEMP TABLE to_be_deleted (
        title TEXT NOT NULL,
        artist TEXT NOT NULL
    );
    """

INSERT_INTO_TEMP = """
    INSERT INTO to_be_deleted (title, artist)
    VALUES (:title, :artist);
    """

CHECK_MISSING = """
    SELECT title, artist FROM to_be_deleted
    WHERE (title, artist) NOT IN (
        SELECT title, artist FROM library
    );
    """

DELETE_SONGS = """
    DELETE FROM library WHERE (title, artist) IN (
        SELECT title, artist FROM to_be_deleted
    );
    """

def remove(database: str, *music_files: str, verbose: int = 0, warn_missing: bool = False) -> None:
    music_files = set(music_files)
    gen = (get_metadata(f).as_dict() for f in music_files)
    con = sqlite3.connect(database)
    with con:
        if warn_missing:
            con.execute(CREATE_TEMP_TABLE)
            con.executemany(INSERT_INTO_TEMP, gen)
            cur = con.execute(CHECK_MISSING)
            for (title, artist) in cur.fetchall():
                logging.warning('duplicated: "%s" from "%s"', title, artist)
            con.execute(DELETE_SONGS)
        else:
            con.executemany(DIRECT_DELETE, gen)
    con.close()