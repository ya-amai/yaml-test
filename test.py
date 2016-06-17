import yaml
from copy import deepcopy
from logging import getLogger, StreamHandler, DEBUG, WARNING
from pprint import pprint as pp
from jq import jq

# initialize logging
logger = getLogger(__name__)
_handler = StreamHandler()
_handler.setLevel(DEBUG)
logger.addHandler(_handler)
logger.setLevel(WARNING)
_debug = logger.debug



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

    # simple if
    {"data": """
object: 100
_if: {"when": False}
    """,
    "result": {}
    },

    # complex duplicate
    {"data": """
other: ["a"]
$"object_\\(.item[1])": 100
comp:
  data:
    test: $100+.item[1]
    _dup: {"with": [1,2]}
_dup: {"with": [1,2]}
    """,
    "result": {"other": ["a"], "object_1": 100, "object_2": 100, "comp": {"data": {"test": 102}}}
    },

]

def _jq(s, c):
    _debug("    +++: jq in %s, %s", s, c)
    if isinstance(s, str) and s.startswith("$"):
        ret = jq(s[1:]).transform(c)
    else:
        ret = s
    _debug("    +++: jq out %s", ret)
    return ret

def _process_include(data, context, out):
    # check data has include key
    if "_include" not in data:
        return

    # process jq value
    # store result
    value = data["_include"]["from"]
    out.update(_jq(value, context))

    # import pdb; pdb.set_trace()
    data.pop("_include")

def _process_dup(data, context, out):
    # check data has include key
    if "_dup" not in data:
        return

    # process jq value
    # import pdb; pdb.set_trace()
    value = data["_dup"]["with"]
    ret = _jq(value, context)
    
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

def _process_if(data, context, out):
    # check data has include key
    if "_if" not in data:
        return out

    # make deepcopy for duplicate object
    obj = deepcopy(data)

    # process jq value
    value = data["_if"]["when"]
    ret = _jq(value, context)

    # remove if retrun true
    out.pop("_if", None)
    if ret:
        return
    else:
        for k in obj.keys():
            data.pop(k, None)

def _process(data, context, out={}):
    _debug("***: Input = %s", data)
    _debug("***: Context = %s", context)
    _debug("***: Output = %s", out)

    if isinstance(data, dict):
        # process meta-key
        if "_dup" in data.keys():
            value = data["_dup"]["with"]
            data.pop("_dup", None)
            ret = _jq(value, context)

            # duplicate with loop
            for elm in enumerate(ret) if isinstance(ret, list) else ret.items():
                # import pdb; pdb.set_trace()
                context.update({"item": elm})
                tmp = {}
                _process(data, context, tmp)
                out.update(tmp)
        elif "_include" in data.keys():
            _debug("###: ignore include ...")
        else:
            for k, v in data.items():
                key = _jq(k, context)
                out[key] = _process(v, context, out={})

    elif isinstance(data, list):
        _debug("###: ignore list ...")
        out = data
    else:
        out = _jq(data, context)

    #_debug("***: Output = %s", out)
    return out

def process(data, context):
    return _process(deepcopy(data), deepcopy(context), {})

#        _process_include(data, context, out)
#        _process_dup(data, context, out)
#        _process_if(data, context, out)
#        for k, v in data.items():
#            logger.debug("+++: Out %s", out)
#            logger.debug("+++: Iter %s, %s", k, v)
#            if isinstance(v, dict):
#                out[k] = {}
#                process(data[k], context, out[k])
#                continue
#            out[k] = v
            
def _process_with_debug(idx, ex, data, context, out={}):
    logger.setLevel(DEBUG)
    _debug("%03d: ##############################", idx)
    ret = process(data, context, out)
    _debug("***: Result = %s", ret)
    _debug("-->: Expect = %s", ex)
    _debug("-->: %s", (ret == ex))
    _debug("")
    logger.setLevel(WARNING)

def main():
    context = DATA
    for i, ex in enumerate(EXAMPLES):
        if i not in (7,):
            continue
        d = yaml.load(ex["data"])
        e = ex["result"]
        ret = process(d, context)
        if (ret != e):
            _process_with_debug(i, e, d, context)

if __name__ == '__main__':
    main()
