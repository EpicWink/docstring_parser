# docstring_parser

Parse Python docstrings. Currently supports ReST-style and Google-style
docstrings.

## Installation

```bash
pip install docstring-parser
```

## Usage

ReST-style:
```python
>>> from docstring_parser import parse
>>>
>>>
>>> docstring = parse(
...     '''
...     Short description
...
...     Long description spanning multiple lines
...     - First line
...     - Second line
...     - Third line
...
...     :param name: description 1
...     :param int priority: description 2
...     :param str sender: description 3
...     :raises ValueError: if name is invalid
...     ''')
>>>
>>> docstring.long_description
'Long description spanning multiple lines\n- First line\n- Second line\n- Third line'
>>> docstring.params[1].arg_name
'priority'
>>> docstring.raises[0].type_name
'ValueError'
```

Google-style:
```python
>>> from docstring_parser import parse
>>>
>>>
>>> docstring = parse(
...     '''
...     Short description
...
...     Long description spanning multiple lines
...     - First line
...     - Second line
...     - Third line
...
...     Arguments:
...         name: description 1
...         priority (int): description 2
...         sender (str): description 3
...
...     Raises:
...         ValueError: if name is invalid
...     ''')
>>>
>>> docstring.long_description
'Long description spanning multiple lines\n- First line\n- Second line\n- Third line'
>>> docstring.params[1].arg_name
'priority'
>>> docstring.raises[0].type_name
'ValueError'
```

## Contributing
MIT-licensed, see [LICENSE.md](LICENSE.md).

Run tests with [pytest](https://pytest.org/en/latest/)
```bash
pip install pytest
pytest -vvra
```

Process imports with [isort](https://timothycrosley.github.io/isort/)
```bash
pip install isort
isort -rc docstring_parser
```

Style code with [Black](https://black.readthedocs.io/en/stable/)
```bash
pip install black
black docstring_parser
```
