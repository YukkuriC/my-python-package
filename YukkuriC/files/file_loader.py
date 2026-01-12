import json
from functools import partial

opentext = partial(open, encoding='utf-8')


def loadjson(file):
    with opentext(file) as f:
        return json.load(f)


def loadtext(file):
    with opentext(file) as f:
        return f.read()


__all__ = ['opentext', 'loadtext', 'loadjson']
