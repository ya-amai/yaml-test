import yaml
from jq import jq
from pprint import pprint as pp

EXAMPLES = []
DATA = []

# datas
DATA.append({"key": "value"})

# simple include

EXAMPLES << {"data": 100}
"""
object:
    _include: {"from": ".[0]"}
""",
"out":{"object": {"key": "value"}}}

# simple duplicate(loop)
EXAMPLES.append("""
$object_item: 100
_dup: {"with": [1,2]}
""")
RESULT.append({"object_1": 100, "object_2": 100})

# simple exists(if)
EXAMPLES.append("""
object: 100
_exsists: {"when": False}
""")
RESULT.append({})


def process(data, context, out={}):
    print("***: Input = %s" % data)
    print("***: Context = %s" % context)

    if isinstance(data, dict):
        for k, v in data.items():
            if "_include" in v:
                ret = jq(v["_include"]["from"]).transform(context)
                out[k] = ret
                continue
            if isinstance(v, dict):
                process(data[k], context, out)
    return out 
            

    pass

"""
    pp("DDDD: Input = %s" % data)
    if isinstance(data, dict):
        for k, v in data.items():
            if k.startswith("_include"):
                out[k] = v["from"]
                continue
            if isinstance(v, dict):
                process(v, context, out)
    return out

            #process(data[k], context)
"""



def main():
    context = DATA
    for ex in EXAMPLES:
        ret = process(yaml.load(ex), context)
        pp(ret)

if __name__ == '__main__':
    main()
