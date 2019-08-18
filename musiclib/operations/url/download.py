import sqlite3
import logging
import os.path
import glob
from .._metadata_analyser import set_metadata
from .._types import Song
from ...exceptions import RequiresYtdlError

SELECT_ALL_DATA = """
    SELECT title, artist, album, download_url
    FROM library
    WHERE download_url IS NOT NULL;
    """

SELECT_COUNT = """
    SELECT COUNT(*)
    FROM library
    WHERE download_url IS NOT NULL;
    """

def change_extension(video_filename: str) -> str:
    """Workaround to get audio-only extension, since youtube-dl
        only outputs the filename before the post-processing.
    """
    name = os.path.splitext(video_filename)[0]
    globbed_filename = glob.escape(name) + '.*'
    return glob.glob(globbed_filename)[0]

def do_download(database: str):
    try:
        import youtube_dl
    except ModuleNotFoundError as mnf_err:
        raise RequiresYtdlError from mnf_err
    con = sqlite3.connect(database)
    total = con.execute(SELECT_COUNT).fetchone()[0]
    ytdl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }
    with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
        cur = con.execute(SELECT_ALL_DATA)
        res = cur.fetchone()
        count = 1
        while res:
            title, artist, album, download_url = res
            #logging.info("%d of %d: %s - %s", count, total, title, artist)
            print("%d of %d: %s - %s" % (count, total, title, artist))
            info = ytdl.extract_info(download_url, download=True)
            filename = change_extension(ytdl.prepare_filename(info))
            set_metadata(filename, Song(title=title, artist=artist, album=album))
            res = cur.fetchone()
            count += 1