import typing as T

import pytest

from docstring_parser import ParseError
from docstring_parser.numpy import parse


@pytest.mark.parametrize("source, expected", [
    ("", None),
    ("\n", None),
    ("Short description", "Short description"),
    ("\nShort description\n", "Short description"),
    ("\n   Short description\n", "Short description"),
])
def test_short_description(source: str, expected: str) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected
    assert docstring.long_description is None
    assert docstring.meta == []


@pytest.mark.parametrize(
    "source, expected_short_desc, expected_long_desc, expected_blank",
    [
        (
            "Short description\n\nLong description",
            "Short description",
            "Long description",
            True
        ),

        (
            """
            Short description

            Long description
            """,
            "Short description",
            "Long description",
            True
        ),

        (
            """
            Short description

            Long description
            Second line
            """,
            "Short description",
            "Long description\nSecond line",
            True
        ),

        (
            """
            Short description
            """,
            "Short description",
            None,
            False
        ),
    ]
)
def test_long_description(
        source: str,
        expected_short_desc: str,
        expected_long_desc: str,
        expected_blank: bool
) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected_short_desc
    assert docstring.long_description == expected_long_desc
    assert docstring.blank_after_short_description == expected_blank
    assert docstring.meta == []


@pytest.mark.parametrize(
    "source, expected_short_desc, expected_long_desc, "
    "expected_blank_short_desc, expected_blank_long_desc",
    [
        (
            """
            Short description
    
            Parameters
            ----------
            asd
            """,
            "Short description", None, False, False
        ),

        (
            """
            Short description

            Long description

            Parameters
            ----------
            asd
            """,
            "Short description", "Long description", True, True
        ),

        (
            """
            Short description

            First line
                Second line

            Parameters
            ----------
            asd
            """,
            "Short description", "First line\n    Second line", True, True
        ),

        (
            """
            Parameters
            ----------
            asd
            """,
            None, None, False, False
        )
    ]
)
def test_meta_newlines(
        source: str,
        expected_short_desc: T.Optional[str],
        expected_long_desc: T.Optional[str],
        expected_blank_short_desc: bool,
        expected_blank_long_desc: bool
) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected_short_desc
    assert docstring.long_description == expected_long_desc
    assert docstring.blank_after_short_description == expected_blank_short_desc
    assert docstring.blank_after_long_description == expected_blank_long_desc
    assert len(docstring.meta) == 1


def test_meta_with_multiline_description() -> None:
    docstring = parse(
        """
        Short description

        Parameters
        ----------
        spam
            asd
            1
                2
            3
        """)
    assert docstring.short_description == "Short description"
    assert len(docstring.meta) == 1
    assert docstring.meta[0].args == ["param", "spam"]
    assert docstring.meta[0].description == "asd\n1\n    2\n3"


def test_multiple_meta() -> None:
    docstring = parse(
        """
        Short description

        Parameters
        ----------
        spam
            asd
            1
                2
            3
    
            Raises
        ------
        bla
            herp
        yay
            derp
        """)
    assert docstring.short_description == "Short description"
    assert len(docstring.meta) == 3
    assert docstring.meta[0].args == ["param", "spam"]
    assert docstring.meta[0].description == "asd\n1\n    2\n3"
    assert docstring.meta[1].args == ["raises", "bla"]
    assert docstring.meta[1].description == "herp"
    assert docstring.meta[2].args == ["raises", "yay"]
    assert docstring.meta[2].description == "derp"


def test_params() -> None:
    docstring = parse("Short description")
    assert len(docstring.params) == 0

    docstring = parse(
        """
        Short description

        Parameters
        ----------
        name
            description 1
        priority : int
            description 2
        sender : str
            description 3
        ratio : Optional[float], optional
            description 4
        """)
    assert len(docstring.params) == 4
    assert docstring.params[0].arg_name == "name"
    assert docstring.params[0].type_name is None
    assert docstring.params[0].description == "description 1"
    assert docstring.params[0].default is None
    assert not docstring.params[0].is_optional
    assert docstring.params[1].arg_name == "priority"
    assert docstring.params[1].type_name == "int"
    assert docstring.params[1].description == "description 2"
    assert docstring.params[1].default is None
    assert not docstring.params[1].is_optional
    assert docstring.params[2].arg_name == "sender"
    assert docstring.params[2].type_name == "str"
    assert docstring.params[2].description == "description 3"
    assert docstring.params[2].default is None
    assert not docstring.params[2].is_optional
    assert docstring.params[3].arg_name == "ratio"
    assert docstring.params[3].type_name == "Optional[float]"
    assert docstring.params[3].description == "description 4"
    assert docstring.params[3].is_optional


def test_attributes() -> None:
    docstring = parse("Short description")
    assert len(docstring.params) == 0

    docstring = parse(
        """
        Short description

        Attributes
        ----------
        name
            description 1
        priority : int
            description 2
        sender : str
            description 3
        ratio : Optional[float], optional
            description 4
        """
    )
    assert len(docstring.params) == 4
    assert docstring.params[0].arg_name == "name"
    assert docstring.params[0].type_name is None
    assert docstring.params[0].description == "description 1"
    assert not docstring.params[0].is_optional
    assert docstring.params[1].arg_name == "priority"
    assert docstring.params[1].type_name == "int"
    assert docstring.params[1].description == "description 2"
    assert not docstring.params[1].is_optional
    assert docstring.params[2].arg_name == "sender"
    assert docstring.params[2].type_name == "str"
    assert docstring.params[2].description == "description 3"
    assert not docstring.params[2].is_optional
    assert docstring.params[3].arg_name == "ratio"
    assert docstring.params[3].type_name == "Optional[float]"
    assert docstring.params[3].description == "description 4"
    assert docstring.params[3].is_optional

    docstring = parse(
        """
        Short description

        Attributes
        ----------
        name
            description 1
            with multi-line text
        priority : int
            description 2
        """
    )
    assert len(docstring.params) == 2
    assert docstring.params[0].arg_name == "name"
    assert docstring.params[0].type_name is None
    assert docstring.params[0].description == (
        "description 1\n" "with multi-line text"
    )
    assert docstring.params[1].arg_name == "priority"
    assert docstring.params[1].type_name == "int"
    assert docstring.params[1].description == "description 2"


def test_returns() -> None:
    docstring = parse(
        """
        Short description
        """)
    assert docstring.returns is None

    docstring = parse(
        """
        Short description

        Returns
        -------
        int
            description
        """)
    assert docstring.returns is not None
    assert docstring.returns.type_name == "int"
    assert docstring.returns.description == "description"

    docstring = parse(
        """
        Short description

        Returns
        -------
        out : int
            description
        """)
    assert docstring.returns is not None
    assert docstring.returns.type_name == "int"
    assert docstring.returns.description == "description"

    docstring = parse(
        """
        Short description

        Yields
        ------
        int
            description
        """)
    assert docstring.returns is not None
    assert docstring.returns.type_name == "int"
    assert docstring.returns.description == "description"


def test_raises() -> None:
    docstring = parse(
        """
        Short description
        """)
    assert len(docstring.raises) == 0

    docstring = parse(
        """
        Short description

        Raises
        ------
        ValueError
            description
        """)
    assert len(docstring.raises) == 1
    assert docstring.raises[0].type_name == "ValueError"
    assert docstring.raises[0].description == "description"


def test_broken_meta() -> None:
    with pytest.raises(ParseError):
        parse(
            """
            Short description

            Returns
            -------
            out : int
                description

            Yields
            ------
            int
                description
            """)

    # these should not raise any errors
    parse(":sthstrange: desc")
    parse(":param with too many args: desc")
