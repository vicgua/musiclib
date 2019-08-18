import eyed3
from ._types import Song

def get_metadata(file: str) -> Song:
    meta = eyed3.load(file)
    return Song(title=meta.tag.title, artist=meta.tag.artist, album=meta.tag.album)

def set_metadata(file: str, metadata: Song):
    meta = eyed3.load(file)
    meta.tag.title = metadata.title
    meta.tag.artist = metadata.artist
    meta.tag.album = metadata.album
    meta.tag.save()