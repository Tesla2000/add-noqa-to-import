from __future__ import annotations

import argparse
import enum
import io
import os
import re
import sys
from typing import Generator
from typing import NamedTuple
from typing import Sequence


class Settings(NamedTuple):
    application_directories: tuple[str, ...] = ('.',)
    unclassifiable_application_modules: frozenset[str] = frozenset()
    maximal_line_length: int = 79


CodeType = enum.Enum('CodeType', 'PRE_IMPORT_CODE IMPORT NON_CODE CODE')

Tok = enum.Enum('Tok', 'IMPORT STRING NEWLINE ERROR')

# GENERATED VIA generate-tokenize
COMMENT = r'#[^\r\n]*'
NAME = r'\w+'
PREFIX = r'[RrUu]?'
DOUBLE_3 = r'"""[^"\\]*(?:(?:\\.|\\\n|"(?!""))[^"\\]*)*"""'
SINGLE_3 = r"'''[^'\\]*(?:(?:\\.|\\\n|'(?!''))[^'\\]*)*'''"
DOUBLE_1 = r'"[^"\\]*(?:\\.[^"\\]*)*"'
SINGLE_1 = r"'[^'\\]*(?:\\.[^'\\]*)*'"
# END GENERATED

WS = r'[ \f\t]+'
IMPORT = fr'(?:from|import)(?={WS})'
EMPTY = fr'[ \f\t]*(?=\n|{COMMENT})'
OP = '[,.*]'
ESCAPED_NL = r'\\\n'
NAMES = fr'\((?:\s+|,|{NAME}|{ESCAPED_NL}|{COMMENT})*\)'
STRING = fr'{PREFIX}(?:{DOUBLE_3}|{SINGLE_3}|{DOUBLE_1}|{SINGLE_1})'


def _pat(base: str, pats: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(
        fr'{base}'
        fr'(?:{"|".join(pats)})*'
        fr'(?P<comment>(?:{COMMENT})?)'
        fr'(?:\n|$)',
    )


TOKENIZE: tuple[tuple[Tok, re.Pattern[str]], ...] = (
    (Tok.IMPORT, _pat(IMPORT, (WS, NAME, OP, ESCAPED_NL, NAMES))),
    (Tok.NEWLINE, _pat(EMPTY, ())),
    (Tok.STRING, _pat(STRING, (WS, STRING, ESCAPED_NL))),
)


def _tokenize(s: str) -> Generator[tuple[Tok, str], None, None]:
    pos = 0
    while True:
        for tp, reg in TOKENIZE:
            match = reg.match(s, pos)
            if match is not None:
                if 'noreorder' in match['comment']:
                    yield (Tok.ERROR, s[pos:])
                    return
                else:
                    yield (tp, match[0])
                pos = match.end()
                break
        else:
            yield (Tok.ERROR, s[pos:])
            return


def partition_source(src: str) -> tuple[str, list[str], str, str]:
    sio = io.StringIO(src, newline=None)
    src = sio.read().rstrip() + '\n'

    if sio.newlines is None:
        nl = '\n'
    elif isinstance(sio.newlines, str):
        nl = sio.newlines
    else:
        nl = sio.newlines[0]

    chunks = []
    pre_import = True
    for token_type, s in _tokenize(src):
        if token_type is Tok.IMPORT:
            pre_import = False
            chunks.append((CodeType.IMPORT, s))
        elif token_type is Tok.NEWLINE:
            if s.isspace():
                tp = CodeType.NON_CODE
            elif pre_import:
                tp = CodeType.PRE_IMPORT_CODE
            else:
                tp = CodeType.CODE

            chunks.append((tp, s))
        elif pre_import and token_type is Tok.STRING:
            chunks.append((CodeType.PRE_IMPORT_CODE, s))
        else:
            chunks.append((CodeType.CODE, s))

    last_idx = 0
    for i, (tp, _) in enumerate(chunks):
        if tp in (CodeType.PRE_IMPORT_CODE, CodeType.IMPORT):
            last_idx = i

    pre = []
    imports = []
    code = []
    for i, (tp, src) in enumerate(chunks):
        if tp is CodeType.PRE_IMPORT_CODE:
            pre.append(src)
        elif tp is CodeType.IMPORT:
            imports.append(src)
        elif tp is CodeType.CODE or i > last_idx:
            code.append(src)

    return ''.join(pre), imports, ''.join(code), nl


def add_noqa_to_imports(
    imports: list[str], settings: Settings = Settings(),
) -> list[str]:
    def add_noqa_to_import(import_: str) -> str:
        import_lines = import_.splitlines()
        first_line = import_lines[0].rstrip()
        if len(first_line) <= settings.maximal_line_length or "#" in first_line:
            return import_
        if first_line.startswith("from ") and first_line.endswith("import ("):
            first_line += "  # noqa: E501"
        elif first_line.startswith("import "):
            first_line += "  # noqa: E501"
        import_lines[0] = first_line
        return "\n".join(import_lines) + "\n"

    return list(map(add_noqa_to_import, imports))


def fix_file_contents(
    contents: str,
    *,
    settings: Settings = Settings(),
) -> str:
    if not contents or contents.isspace():
        return ''

    # internally use `'\n` as the newline and normalize at the very end
    before, imports, after, nl = partition_source(contents)

    imports = add_noqa_to_imports(imports, settings=settings)

    return f'{before}{"".join(imports)}{after}'.replace('\n', nl)


def _fix_file(
    filename: str,
    args: argparse.Namespace,
    *,
    settings: Settings = Settings(),
) -> int:
    if filename == '-':
        contents_bytes = sys.stdin.buffer.read()
    else:
        with open(filename, 'rb') as f:
            contents_bytes = f.read()
    try:
        contents = contents_bytes.decode()
    except UnicodeDecodeError:
        print(
            f'{filename} is non-utf-8 (not supported)',
            file=sys.stderr,
        )
        return 1

    new_contents = fix_file_contents(
        contents,
        settings=settings,
    )
    if filename == '-':
        print(new_contents, end='')
    elif contents != new_contents:
        print(f'Reordering imports in {filename}', file=sys.stderr)
        with open(filename, 'wb') as f:
            f.write(new_contents.encode())

    if args.exit_zero_even_if_changed:
        return 0
    else:
        return contents != new_contents


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='If `-` is given, reads from stdin and writes to stdout.',
    )
    parser.add_argument('--exit-zero-even-if-changed', action='store_true')
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
    parser.add_argument(
        '--unclassifiable-application-module', action='append', default=[],
        dest='unclassifiable',
        help=(
            '(may be specified multiple times) module names that are '
            'considered application modules.  this setting is intended to be '
            'used for things like C modules which may not always appear on '
            'the filesystem'
        ),
    )

    args = parser.parse_args(argv)

    if os.environ.get('PYTHONPATH'):
        sys.stderr.write('$PYTHONPATH set, import order may be unexpected\n')
        sys.stderr.flush()

    settings = Settings(
        application_directories=tuple(args.application_directories.split(':')),
        unclassifiable_application_modules=frozenset(args.unclassifiable),
        maximal_line_length=int(args.maximal_line_length),
    )

    retv = 0
    for filename in args.filenames:
        retv |= _fix_file(
            filename,
            args,
            settings=settings,
        )
    return retv


if __name__ == '__main__':
    raise SystemExit(main())
