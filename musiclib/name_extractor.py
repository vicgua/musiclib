"""Try to get the name and artist from a filename"""

import sqlite3
import pickle
from .exceptions import RequiresYdlError
from typing import Optional, Dict, Tuple, BinaryIO

GET_URLS = """
    SELECT title, artist, download_url
    FROM library
    WHERE download_url IS NOT NULL;
    """

INSERT_FILENAME = """
    INSERT OR REPLACE
    INTO downloads(download_id, filename, title, artist)
    VALUES (:download_id, :filename, :title, :artist);
    """

def get_filename_mappings(database: str, output_template: Optional[str] = None):
    try:
        import youtube_dl
    except ModuleNotFoundError as err:
        raise RequiresYdlError from err
    ytdl_opts = {
        'simulate': True
    }
    if output_template is not None:
        ytdl_opts['outtmpl'] = output_template
    mapping = {}
    with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
        con = sqlite3.connect(database)
        cur = con.execute(GET_URLS)
        res = cur.fetchone()
        while res:
            title, artist, download_url = res
            result = ytdl.extract_info(download_url, download=False)
            filename = ytdl.prepare_filename(result)
            mapping[filename] = (title, artist)
            res = cur.fetchone()
    return mapping

def serialize_mapping(mapping, dest: BinaryIO) -> None:
    pickle.dump(mapping, dest, protocol=3)

def deserialize_mapping(orig: BinaryIO):
    return pickle.load(orig)