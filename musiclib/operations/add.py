from typing import Optional, Iterable, Generator, Dict
import sqlite3
import logging
from ._types import Song, SongDict
from ._metadata_analyser import get_metadata

# [SQL statements]

INSERT_SONG_DIRECT = """
    INSERT OR IGNORE INTO library (title, artist, album)
    VALUES (:title, :artist, :album);
    """

CREATE_TEMP_TABLE = """
    CREATE TEMP TABLE to_be_added (
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        album TEXT
    );
    """

INSERT_SONG_TEMP = """
    INSERT INTO to_be_added (title, artist, album)
    VALUES (:title, :artist, :album);
    """

CHECK_DUPLICATES = """
    SELECT title, artist FROM to_be_added
    WHERE (title, artist) IN (
        SELECT title, artist FROM library
    );
    """

COPY_SONG = """
    INSERT OR IGNORE INTO library (title, artist, album)
    SELECT title, artist, album FROM to_be_added;
    """

# [/SQL statements]


def get_generator(music_files: Iterable[str], verbose: int) -> Generator[SongDict, None, None]:
    def gen() -> Generator[SongDict, None, None]:
        for f in music_files:
            data = get_metadata(f)
            if data.album:
                s = '%(file)s -> "%(title)s" from "%(artist)s" on "%(album)s"'
            else:
                s = '%(file)s -> "%(title)s from "%(artist)s"'
            logging.info(
                f"processing: {s}",
                file=f,
                title=data.title,
                artist=data.artist,
                album=data.album,
            )
            yield data.as_dict()

    if verbose >= 0:
        return gen()
    else:
        return (get_metadata(f).as_dict() for f in music_files)


def add(
    database: str, *music_files: str, verbose: int = 0, warn_duplicates: bool = True
) -> None:
    """Add `music_files` to the database (`database`).

    With `warn_duplicates`, duplicates will be checked.
    Else, duplicates will be silently ignored (this may improve performance).
    Regardless of `warn_duplicates`, duplicates on `music_files` will be ignored
    and reported, as it is likely to be a programming error.
    """

    music_files_clean = set(music_files)
    if len(music_files_clean) != len(music_files_clean):
        logging.warning("found and ignored duplicates in files list")
    gen = get_generator(music_files_clean, verbose)
    con = sqlite3.connect(database)
    with con:
        if warn_duplicates:
            con.execute(CREATE_TEMP_TABLE)
            con.executemany(INSERT_SONG_TEMP, gen)
            cur = con.execute(CHECK_DUPLICATES)
            for (title, artist) in cur.fetchall():
                logging.warning('duplicated: "%s" from "%s"', title, artist)
            con.execute(COPY_SONG)
        else:
            con.executemany(INSERT_SONG_DIRECT, gen)
    con.close()
