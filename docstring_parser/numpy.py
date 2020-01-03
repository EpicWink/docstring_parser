"""NumPy-style docstring parsing."""

from numpydoc import docscrape

from .common import (
    Docstring,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    ParseError,
)


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
        short = "\n".join(doc["Summary"])
        ret.short_description = short
        short_pos = text.index(doc["Summary"][-1])
        after_short_pos = short_pos + len(doc["Summary"][-1])
        after_short = text[after_short_pos:after_short_pos + 2]
        ret.blank_after_short_description = after_short == "\n\n"

    if doc["Extended Summary"] or doc["Notes"]:
        long_desc = doc["Extended Summary"] + doc["Notes"]
        ret.long_description = "\n".join(long_desc)
        long_pos = text.index(long_desc[-1])
        after_long_pos = long_pos + len(long_desc[-1])
        after_long = text[after_long_pos:after_long_pos + 2]
        ret.blank_after_long_description = after_long == "\n\n"

    for arg_name, type_name, desc in doc["Parameters"]:
        if type_name:
            args = ["param", type_name, arg_name]
        else:
            args = ["param", arg_name]
            type_name = None
        desc = "\n".join(desc)
        meta = DocstringParam(args, desc, arg_name, type_name, None)
        ret.meta.append(meta)

    for _, type_name, desc in doc["Raises"]:
        args = ["raises", type_name]
        desc = "\n".join(desc)
        meta = DocstringRaises(args, desc, type_name)
        ret.meta.append(meta)

    if doc["Returns"]:
        arg_name, type_name, desc = doc["Returns"][0]
        if type_name:
            args = ["returns", type_name]
        else:
            args = ["returns", arg_name]
            type_name = arg_name
        desc = "\n".join(desc)
        meta = DocstringReturns(args, desc, type_name, False)
        ret.meta.append(meta)
    elif doc["Yields"]:
        type_name, arg_name, desc = doc["Yields"][0]
        if type_name:
            args = ["yields", type_name]
        else:
            args = ["yields", arg_name]
            type_name = arg_name
        desc = "\n".join(desc)
        meta = DocstringReturns(args, desc, type_name, True)
        ret.meta.append(meta)

    return ret
