import json
from jinja2 import Markup

def tojson(value, **kwargs):
    j = json.dumps(value, **kwargs)
    return Markup(j
        .replace('&', '\\u0026')
        .replace("'", '\\u0027')
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
    )

