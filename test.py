import yaml
from copy import deepcopy
from jq import jq
from pprint import pprint as pp


# datas
DATA = { "a": {"key": "value"},
         "b": 100
}

EXAMPLES = [
    # simple include to root
    {"data": """
_include: {"from": "$.a"}
     """,
     "result": {"key": "value"}
    },
    {"data": """
_include: {"from": "$.a"}
other: 100
     """,
     "result": {"key": "value", "other": 100}
    },

    # simple include to object
    {"data": """
object:
  _include: {"from": "$.a"}
     """,
     "result": {"object": {"key": "value"}}
    },
    {"data": """
object:
  other: "bbb"
  _include: {"from": "$.a"}
     """,
     "result": {"object": {"key": "value", "other": "bbb"}}
    },

    # simple duplicate(loop)
    {"data": """
$"object_\\(.item[1])": 100
_dup: {"with": [1,2]}
    """,
    "result": {"object_1": 100, "object_2": 100}
    },
    {"data": """
other: ["a"]
$"object_\\(.item[1])": 100
_dup: {"with": [1,2]}
    """,
    "result": {"other": ["a"], "object_1": 100, "object_2": 100}
    },

    # simple exists(if)
    {"data": """
object: 100
_exsists: {"when": False}
    """,
    "result": {}
    },
]

def _jq(s, c):
    print("+++:", s, c)
    if isinstance(s, str) and s.startswith("$"):
        print("+++: jqin", s[1:])
        ret = jq(s[1:]).transform(c)
    else:
        ret = s
    return ret

def _process_include(data, context, out):
    # check data has include key
    if "_include" not in data:
        return out

    # process jq value
    value = data["_include"]["from"]
    if value.startswith("$"):
        ret = jq(value[1:]).transform(context)
    else:
        ret = value

    # store result
    # import pdb; pdb.set_trace()
    out.update(ret)
    data.pop("_include")

    return out

def _process_dup(data, context, out):
    # check data has include key
    if "_dup" not in data:
        return out

    # process jq value
    # import pdb; pdb.set_trace()
    value = data["_dup"]["with"]
    if isinstance(value, str) and value.startswith("$"):
        ret = jq(value[1:]).transform(context)
    else:
        ret = value
    
    # make deepcopy for duplicate object
    obj = deepcopy(data)

    # loop
    for elm in enumerate(ret) if isinstance(ret, list) else ret.items():
        ctx = context
        ctx.update({"item": elm})
        print("+++: ", elm, ctx)
        for k, v in obj.items():
            out[_jq(k, ctx)] = _jq(v, ctx)

    # pop unnecessary keys
    # import pdb; pdb.set_trace()
    out.pop("_dup", None)
    for k in obj.keys():
        print("+++: Delete duplicated object %s" % k)
        data.pop(k, None)

    return out

def process(data, context, out={}):
    print("***: Input = %s" % data)
    print("***: Context = %s" % context)
    print("***: Output = %s" % out)

    if isinstance(data, dict):
        _process_include(data, context, out)
        _process_dup(data, context, out)
        for k, v in data.items():
            print(out)
            print("+++: Iter", k, v)
            if isinstance(v, dict):
                out[k] = {}
                process(data[k], context, out[k])
                continue
            out[k] = v

    return out 
            
def main():
    context = DATA
    for i, ex in enumerate(EXAMPLES):
        if i not in (0,1,2,3,4,5,6):
        # if i not in (3,4,):
            continue
        print("%03d: ##############################" % i)
        ret = process(yaml.load(ex["data"]), context, {})
        print("***: Result = %s" % ret)
        print("-->: Expect = %s" % (ex["result"]))
        print("-->: %s" % (ret == ex["result"]))
        print("")

if __name__ == '__main__':
    main()
