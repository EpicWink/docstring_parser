"""NumPy-style docstring parsing."""

import collections
import typing as T
import functools as ft

from numpydoc import docscrape

from .common import (
    Docstring,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    ParseError,
)


class Section(collections.namedtuple("Section", ("title", "build_meta"))):
    """A docstring section."""


def _blank_after(lines: T.List[str], text: str) -> bool:
    long_pos = text.index(lines[-1])
    after_pos = long_pos + len(lines[-1])
    after = text[after_pos:after_pos + 2]
    return after == "\n\n"


def _build_param_meta(
        arg_name: str,
        type_name: str,
        desc: T.List[str],
) -> DocstringParam:
    args = ["param"] + ([type_name] if type_name else []) + [arg_name]
    type_name = type_name or None
    desc = "\n".join(desc)
    return DocstringParam(args, desc, arg_name, type_name, None, None)


def _build_raises_meta(
        _,
        type_name: str,
        desc: T.List[str],
) -> DocstringRaises:
    args = ["raises", type_name]
    desc = "\n".join(desc)
    return DocstringRaises(args, desc, type_name)


def _build_returns_meta(
        arg_name: str,
        type_name: str,
        desc: T.List[str],
        yields: bool = False,
) -> DocstringReturns:
    key = "yields" if yields else "returns"
    type_name = type_name or arg_name
    args = [key, type_name]
    desc = "\n".join(desc)
    return DocstringReturns(args, desc, type_name, yields)


def _build_other_meta(
        arg_name: str,
        type_name: str,
        desc: T.Union[T.List[str], str],
        key: str = "other",
) -> DocstringMeta:
    arg_name = [arg_name] if arg_name else []
    type_name = [type_name] if type_name else []
    args = [key] + arg_name + type_name
    if not isinstance(desc, str):
        desc = "\n".join(desc)
    return DocstringMeta(args, desc)


def _build_see_also_meta(
        funcs: T.List[T.Tuple[str, str]],
        rest: T.List[str],
) -> DocstringMeta:
    funcs = ", ".join(f"{role}`{func}`" for func, role in funcs)
    desc = funcs + " " + "\n".join(rest)
    return _build_other_meta("", "", desc, key="seealso")


_sections = [
    Section("Parameters", _build_param_meta),
    Section("Other Parameters", _build_param_meta),
    Section("Raises", _build_raises_meta),
    Section("Attributes", ft.partial(_build_other_meta, key="attribute")),
    Section("Examples", ft.partial(_build_other_meta, key="examples")),
    Section("Returns", _build_returns_meta),
    Section("Yields", ft.partial(_build_returns_meta, yields=True)),
    Section("Signature", ft.partial(_build_other_meta, key="signature")),
    Section("Receives", ft.partial(_build_other_meta, key="recieves")),
    Section("Warns", ft.partial(_build_other_meta, key="warns")),
    Section("Warnings", ft.partial(_build_other_meta, key="warns")),
    Section("Methods", ft.partial(_build_other_meta, key="method")),
    Section("See Also", _build_see_also_meta),
    Section("References", ft.partial(_build_other_meta, key="reference")),
    Section("index", ft.partial(_build_other_meta, key="index")),
]


def parse(text: str) -> Docstring:
    """
    Parse the NumPy-style docstring into its components.

    :returns: parsed docstring
    """
    ret = Docstring()
    if not text:
        return ret

    try:
        doc = docscrape.NumpyDocString(text)
    except (docscrape.ParseError, ValueError) as e:
        raise ParseError(
            f'Failed to parse NumPy docstring "{text}"'
        ) from e

    if any(doc["Summary"]):
        ret.short_description = "\n".join(doc["Summary"])
        ret.blank_after_short_description = _blank_after(doc["Summary"], text)

    if doc["Extended Summary"] or doc["Notes"]:
        long_desc = doc["Extended Summary"] + doc["Notes"]
        ret.long_description = "\n".join(long_desc)
        ret.blank_after_long_description = _blank_after(long_desc, text)

    for section in _sections:
        parsed = doc[section.title]
        parsed = parsed if isinstance(parsed, list) else [parsed]
        for args in parsed:
            if not args:
                continue
            if isinstance(args, tuple):
                meta = section.build_meta(*args)
            else:
                meta = section.build_meta("", "", args)
            ret.meta.append(meta)

    return ret
