import argparse
import pkg_resources
import logging

from .operations import init as op_init
from .operations import add as op_add
from .operations import list as op_list
from .operations import remove as op_remove
from .operations import url as op_url

from .exceptions import CommandError, UnexpectedValueError, RequiresYtdlError


def not_implemented(parser, args):
    parser.error("not yet implemented\n")


def init(parser, args):
    op_init.init(args.database, args.force)


def add(parser, args):
    op_add.add(args.database, *args.music_files, warn_duplicates=args.warn_duplicates)


def do_list(parser, args):
    song_list = op_list.do_list(args.database, not args.json)
    if args.json:
        print(op_list.to_json(song_list, args.compact))
    else:
        op_list.format_list(song_list)


def remove(parser, args):
    op_remove.remove(args.database, *args.music_files, warn_missing=args.warn_missing)


def url(parser, args):
    if 'url_mode' not in args:
        parser.print_usage()
        parser.exit(1)
    elif args.url_mode == 'get':
        if args.format == 'youtube-dl':
            op_url.get_ytdl(args.database, args.dest)
        elif args.format == 'raw':
            op_url.get_raw(args.database, args.dest)
        else:
            raise UnexpectedValueError('format', args.format, args)
    elif args.url_mode == 'set':
        try:
            op_url.set_from_file(args.database, args.url_file)
        except op_url.MalformedFile as err:
            parser.error(f'failed to parse file: {err}')
    elif args.url_mode == 'template':
        op_url.template(args.database, args.template_file)
    elif args.url_mode == 'download':
        op_url.download.do_download(args.database)
    else:
        raise UnexpectedValueError('url_mode', args.url_mode, args)


def main():
    version = pkg_resources.require("musiclib")[0].version
    parser = argparse.ArgumentParser(description="Music library organizer")
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {version}"
    )
    parser.add_argument(
        "-d",
        "--database",
        default="library.db",
        type=str,
        help="specify database file. Default: library.db",
    )
    subparsers = parser.add_subparsers(title="commands")

    init_parser = subparsers.add_parser("init", help="initialize library database")
    init_parser.set_defaults(func=init, parser=init_parser)
    init_parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="erase the database if it exists",
    )

    add_parser = subparsers.add_parser(
        "add", aliases=["+"], help="add a song to the library database"
    )
    add_parser.set_defaults(func=add, parser=add_parser)
    add_parser.add_argument(
        "-Wd",
        "--no-warn-duplicates",
        dest="warn_duplicates",
        default=True,
        action="store_false",
        help="do not check duplicates (they will be silently ignored)",
    )
    add_parser.add_argument(
        "music_files", metavar="MUSIC-FILE", nargs="+", help="music file to be added"
    )

    list_parser = subparsers.add_parser(
        "list", aliases=["ls"], help="list all songs from the database"
    )
    list_parser.set_defaults(func=do_list, parser=list_parser)
    list_parser.add_argument(
        "--json", default=False, action="store_true", help="output as JSON"
    )
    list_parser.add_argument(
        "--compact",
        default=False,
        action="store_true",
        help="output a compact representation. Only significant with JSON output",
    )

    remove_parser = subparsers.add_parser(
        "remove", aliases=["rm", "del"], help="remove a song from the database"
    )
    remove_parser.set_defaults(func=remove, parser=remove_parser)
    remove_parser.add_argument(
        "-Wm",
        "--no-warn-missing",
        dest="warn_missing",
        default=True,
        action="store_false",
        help="do not warn about files not in the database"
    )
    remove_parser.add_argument(
        "music_files", metavar="MUSIC-FILE", nargs="+", help="music file to be removed (the disk file will not be deleted)"
    )

    purge_parser = subparsers.add_parser(
        "purge", help="remove all missing songs from the database"
    )
    purge_parser.set_defaults(func=not_implemented, parser=purge_parser)

    url_parser = subparsers.add_parser("url", help="manage URLs")
    url_parser.set_defaults(func=url, parser=url_parser, do_mapping=True)
    url_subparsers = url_parser.add_subparsers()

    url_get_parser = url_subparsers.add_parser('get', help="print the URL list")
    url_get_parser.set_defaults(url_mode='get')
    url_get_parser.add_argument('dest', nargs='?', type=argparse.FileType('w'), default='-',
        help="write the URL list to this file. Standard output by default")
    url_get_parser.add_argument('--format', '-f', choices=("youtube-dl", "raw"), default="youtube-dl",
        help="youtube-dl (the default) will print a human-readable, youtube-dl"
        " compatible format; raw will dump the URLs directly, one per line")

    url_set_parser = url_subparsers.add_parser('set', help="set URLs from a list produced by `template`")
    url_set_parser.set_defaults(url_mode='set')
    url_set_parser.add_argument('url_file', nargs='?', type=argparse.FileType('r'), default='-',
        help='read URLs from this file. Standard input by default')

    url_template_parser = url_subparsers.add_parser('template', aliases=['tpl'],
        help="write a template of URLs to be filled and passed to `set`")
    url_template_parser.set_defaults(url_mode='template')
    url_template_parser.add_argument('template_file', nargs='?', type=argparse.FileType('w'), default='-')

    url_download_parser = url_subparsers.add_parser('download', aliases=['dl'],
        help="download all URLs and apply the metadata")
    url_download_parser.set_defaults(url_mode='download')

    args = parser.parse_args()
    try:
        p = args.parser
    except AttributeError:
        p = parser
    if "func" not in args:
        p.print_usage()
        parser.exit(1)
    try:
        args.func(p, args)
    except CommandError as ce:
        p.error(ce)
    except RequiresYtdlError:
        p.error("this feature requires youtube-dl. Please install musiclib[download]")
