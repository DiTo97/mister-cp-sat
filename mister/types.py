import typing as t


JSON = t.Union[str, int, float, bool, None,
               t.Dict[str, 'JSON'],
               t.List['JSON']]
