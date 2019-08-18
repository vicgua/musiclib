import sqlite3
from typing import List, NamedTuple, Optional
import json
from ._types import Song, SongList

# [SQL statements]

SELECT_ALL = """
    SELECT title, artist, album, download_url FROM library
    ORDER BY title ASC, artist ASC;
    """

SELECT_FORMAT = """
    SELECT
        MAX(LENGTH(title)),
        MAX(LENGTH(artist)),
        MAX(IFNULL(LENGTH(album), 0)),
        MAX(IFNULL(LENGTH(download_url), 0))
    FROM library;
    """

# [/SQL statements]


def do_list(database: str, fetch_format_info: bool = True) -> SongList:
    con = sqlite3.connect(database)
    cur = con.execute(SELECT_ALL)
    song_list = SongList()
    s = cur.fetchone()
    while s:
        song_list.songs.append(
            Song(title=s[0], artist=s[1], album=s[2], download_url=s[3])
        )
        s = cur.fetchone()
    if fetch_format_info:
        if song_list:
            cur = con.execute(SELECT_FORMAT)
            fi = cur.fetchone()
        else:
            fi = (0, 0, 0, 0)
        (
            song_list.max_title,
            song_list.max_artist,
            song_list.max_album,
            song_list.max_dlurl,
        ) = fi
    con.close()
    return song_list


def format_list(song_list: SongList) -> None:
    if not song_list.has_format_info():
        raise ValueError("song list must have format info to be formatted")
    TITLE = "TITLE"
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    title_len = max(song_list.max_title, len(TITLE))
    artist_len = max(song_list.max_artist, len(ARTIST))
    album_len = max(song_list.max_album, len(ALBUM))
    print(
        "{t:^{t_l}} | {ar:^{ar_l}} | {al:^{al_l}}".format(
            t=TITLE, t_l=title_len, ar=ARTIST, ar_l=artist_len, al=ALBUM, al_l=album_len
        )
    )
    print(
        "{0:-<{t_l}}-|-{0:-<{ar_l}}-|-{0:-<{al_l}}".format(
            "", t_l=title_len, ar_l=artist_len, al_l=album_len
        )
    )
    for song in song_list.songs:
        print(
            "{s.title:{t_l}} | {s.artist:{ar_l}} | {s.album:{al_l}}".format(
                s=song, t_l=title_len, ar_l=artist_len, al_l=album_len
            )
        )


def to_json(song_list: SongList, compact: bool = False) -> str:
    doc = [
        {
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "download_url": song.download_url,
        }
        for song in song_list.songs
    ]
    if compact:
        return json.dumps(doc, indent=None, separators=(",", ":"))
    else:
        return json.dumps(doc, indent=2, sort_keys=True)
