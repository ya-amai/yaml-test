import yaml
from jq import jq
from pprint import pprint as pp


# datas
DATA = [
   {"key": "value"},
   100
]

EXAMPLES = [
    # simple include to root
    {"data": """
_include: {"from": "$.[0]"}
     """,
     "result": {"key": "value"}
    },
    # simple include to object
    {"data": """
object:
  _include: {"from": "$.[0]"}
     """,
     "result": {"object": {"key": "value"}}
    },

    # simple duplicate(loop)
    {"data": """
$object_item: 100
_dup: {"with": [1,2]}
    """,
    "result": {"object_1": 100, "object_2": 100}
    },

    # simple exists(if)
    {"data": """
object: 100
_exsists: {"when": False}
    """,
    "result": {}
    },
]

def _process_include(data, context):
    # check data has include key
    if "_include" not in data:
        return

    # process jq value
    value = include["from"]
    if value.startswith("$"):
        ret = jq(value[1:]).transform(context)
    else:
        ret = value

    return ret

def process(data, context, out={}):
    print("***: Input = %s" % data)
    print("***: Context = %s" % context)

    if isinstance(data, dict):
        _process_include(data, context)

        for k, v in data.items():
            print("+++:", k, v)
            if "_dup" in v:
                # process jq value
                value = v["_dup"]["with"]
                if value.startswith("$"):
                    ret = jq(value[1:]).transform(context)
                else:
                    ret = value

                # loop
                for elm in enumerate(ret) if isinstance(ret, list) else ret.items():
                    print(elm)
                
            if isinstance(v, dict):
                process(data[k], context, out)
    return out 
            
def main():
    context = DATA
    for ex in EXAMPLES:
        ret = process(yaml.load(ex["data"]), context)
        print("***: Result = %s" % ret)
        print("-->: Expect %s" % (ret == ex["result"]))
        break

if __name__ == '__main__':
    main()
