import attr
from typing import NamedTuple, Dict, List, Optional, NewType

SongDict = NewType("SongDict", Dict[str, Optional[str]])


class Song(NamedTuple):
    title: str
    artist: str
    album: Optional[str] = None
    download_url: Optional[str] = None

    def as_dict(self, prefix: Optional[str] = None) -> SongDict:
        if prefix:
            return SongDict(
                {f"{prefix}_{field}": getattr(self, field) for field in self._fields}
            )
        else:
            return SongDict({field: getattr(self, field) for field in self._fields})


@attr.s(auto_attribs=True, slots=True)
class SongList:
    songs: List[Song] = attr.Factory(list)
    max_title: Optional[int] = None
    max_artist: Optional[int] = None
    max_album: Optional[int] = None
    max_dlurl: Optional[int] = None

    def has_format_info(self) -> bool:
        return (
            self.max_title is not None
            and self.max_artist is not None
            and self.max_album is not None
            and self.max_dlurl is not None
        )
    
    def __bool__(self) -> bool:
        return bool(self.songs)
    
    def __len__(self) -> int:
        return len(self.songs)
