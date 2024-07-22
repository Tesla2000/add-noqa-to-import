from __future__ import annotations

import argparse
from typing import NamedTuple, Union
from typing import Sequence

import libcst as cst
from libcst import Module, Comment, FlattenSentinel, RemovalSentinel, \
    ImportFrom, TrailingWhitespace, Import, SimpleWhitespace


class Settings(NamedTuple):
    application_directories: tuple[str, ...] = ('.',)
    unclassifiable_application_modules: frozenset[str] = frozenset()
    maximal_line_length: int = 79


def fix_imports(
    code: str,
    *,
    settings: Settings = Settings(),
) -> str:
    module = cst.parse_module(code)
    transformer = AddImportTransformer(module, settings)
    new_module = module.visit(transformer)
    return new_module.code


class AddImportTransformer(cst.CSTTransformer):

    def __init__(self, module: Module, settings: Settings ):
        super().__init__()
        self.settings = settings
        self.module = module

    def leave_ImportFrom(self, original_node: cst.ImportFrom,
                         updated_node: cst.ImportFrom) -> cst.ImportFrom:
        str_code = self.module.code_for_node(original_node)
        if len(str_code.splitlines()[0]) <= self.settings.maximal_line_length:
            return updated_node
        comment_path = ["lpar", "whitespace_after", "first_line", "comment"]
        if self._get_path_attrs(original_node, comment_path):
            return updated_node
        if self._get_path_attrs(original_node, comment_path[:-1]):
            return self._set_path_attrs(original_node, comment_path[:-1],
                                        comment=Comment("# noqa: E501"), whitespace=SimpleWhitespace("  "))
        return updated_node

    def leave_SimpleStatementLine(
        self, original_node: "SimpleStatementLine",
        updated_node: "SimpleStatementLine"
    ) -> Union[
        "BaseStatement", FlattenSentinel["BaseStatement"], RemovalSentinel]:
        str_code = self.module.code_for_node(original_node)
        if len(str_code.splitlines()[0]) <= self.settings.maximal_line_length:
            return updated_node
        if (len(original_node.children) != 2 or
            not isinstance(original_node.children[0], ImportFrom | Import) or
            len(original_node.children[0].names) != 1 or
            not isinstance(original_node.children[1], TrailingWhitespace) or
            self._get_path_attrs(original_node, ["trailing_whitespace", "comment"]) or
            self._get_path_attrs(original_node.children[0], ["lpar"])
        ):
            return updated_node
        return self._set_path_attrs(updated_node, ["trailing_whitespace"], comment=Comment(
            value='# noqa: E501'), whitespace=SimpleWhitespace("  "))

    def leave_Import(self, original_node: cst.ImportFrom,
                     updated_node: cst.ImportFrom) -> cst.ImportFrom:
        str_code = self.module.code_for_node(original_node)
        if len(str_code.splitlines()[0]) <= self.settings.maximal_line_length:
            return updated_node
        return updated_node
        comment_path = ["lpar", "whitespace_after", "first_line", "comment"]
        if self._get_path_attrs(original_node, comment_path):
            return updated_node
        if self._get_path_attrs(original_node, comment_path[:-1]):
            return self._set_path_attrs(original_node, comment_path[:-1],
                                        comment=Comment("#  noqa: E501"))
        if len(original_node.names) > 1:
            return updated_node
        return updated_node.lpar.with_changes(children=new_children)

    def _get_path_attrs(self, elem, attrs: Sequence[str]):
        current_elem = elem
        for attr in attrs:
            if not hasattr(current_elem, attr):
                return
            current_elem = getattr(current_elem, attr)
        return current_elem

    def _set_path_attrs(self, elem, attrs: Sequence[str], **kwargs):
        inner_element = self._get_path_attrs(elem, attrs)
        inner_element = inner_element.with_changes(**kwargs)
        for i in range(1, len(attrs) + 1):
            outer_element = self._get_path_attrs(elem, attrs[:-i])
            inner_element = outer_element.with_changes(
                **{attrs[-i]: inner_element})
        return inner_element


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
        retv |= fix_imports(
            filename,
            settings=settings,
        )
    return retv


if __name__ == '__main__':
    fix_imports(
        code="""def hello_world():
    print("Hello, world!")""")
    # raise SystemExit(main())
