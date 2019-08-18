import sqlite3
from ..exceptions import CommandError

CHECK_EXISTANCE = """
    SELECT 1 FROM sqlite_master
    WHERE type = 'table' AND name = 'library'
    LIMIT 1;
    """

DROP_IF_EXISTS = """
    DROP TABLE IF EXISTS library;
    """

CREATE_TABLE = """
    CREATE TABLE library (
        title TEXT,
        artist TEXT,
        album TEXT,
        download_url TEXT DEFAULT NULL,
        PRIMARY KEY (title, artist)
    );
    """


def init(database: str, force: bool = False) -> None:
    con = sqlite3.connect(database)
    with con:
        if force:
            con.execute(DROP_IF_EXISTS)
        else:
            cur = con.execute(CHECK_EXISTANCE)
            if cur.fetchone():
                raise CommandError(
                    "already initialized. Use --force to recreate anyway"
                )
        con.execute(CREATE_TABLE)
    con.close()
