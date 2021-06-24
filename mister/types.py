import typing as t


JSON = t.Union[str, int, float, bool, None,
               t.Dict[str, 'JSON'],
               t.List['JSON']]

def str2bool(s):
    return str(s).lower() \
           in ("true", "1")
