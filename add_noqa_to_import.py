from __future__ import annotations

import argparse
import enum
import io
import re
import sys
from typing import Generator
from typing import NamedTuple
from typing import Sequence


class Settings(NamedTuple):
    application_directories: tuple[str, ...] = ('.',)
    unclassifiable_application_modules: frozenset[str] = frozenset()
    maximal_line_length: int = 79


def fix_file(
    filename: str,
    *,
    settings: Settings = Settings(),
) -> int:
    pass


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='If `-` is given, reads from stdin and writes to stdout.',
    )
    parser.add_argument(
        '--application-directories', default='.',
        help=(
            'Colon separated directories that are considered top-level '
            'application directories.  Defaults to `%(default)s`'
        ),
    )
    parser.add_argument(
        '--maximal-line-length', default=79,
        help=(
            'Maximal line length specified by flake'
        ),
    )

    args = parser.parse_args(argv)

    settings = Settings(
        application_directories=tuple(args.application_directories.split(':')),
        unclassifiable_application_modules=frozenset(args.unclassifiable),
        maximal_line_length=int(args.maximal_line_length),
    )

    retv = 0
    for filename in args.filenames:
        retv |= fix_file(
            filename,
            settings=settings,
        )
    return retv


if __name__ == '__main__':
    raise SystemExit(main())
