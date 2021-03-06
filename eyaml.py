import yaml
from copy import deepcopy
from logging import getLogger, StreamHandler, DEBUG, WARNING
from jq import jq

# initialize logging
logger = getLogger(__name__)
_handler = StreamHandler()
_handler.setLevel(DEBUG)
logger.addHandler(_handler)
logger.setLevel(WARNING)
_debug = logger.debug


def _jq(s, c):
    """
    Process jq-string

    :param str s: jq-string starting with '$'
    :param str c: jq process context
    :return: jq-processed string
    """
    _debug("    +++: jq in %s, %s", s, c)
    if isinstance(s, str) and s.startswith("$"):
        ret = jq(s[1:]).transform(c)
    else:
        ret = s
    _debug("    +++: jq out %s", ret)
    return ret


def _process(data, context, out={}):
    """
    private process extended-yaml data

    :param dict, list: target data
    :param dict: context data
    :param out: store recursive-function output
    :return: processed extended-yaml data
    """
    _debug("***: Input = %s", data)
    _debug("***: Context = %s", context)
    _debug("***: Output = %s", out)

    if isinstance(data, dict):
        # process meta-key
        if "_dup" in data.keys():
            value = data["_dup"]["with"]
            context_name = data["_dup"].get("to", "item")
            data.pop("_dup", None)
            ret = _jq(value, context)

            # prepare context
            if context_name == "item":
                if context_name not in context:
                    context[context_name] = []
                context[context_name].append({})
                
            # duplicate with loop
            for elm in enumerate(ret) if isinstance(ret, list) else ret.items():
                # update context
                if context_name == "item":
                    context[context_name][-1] = elm
                else:
                    context[context_name] = elm

                tmp = {}
                # modify data, this data must be clone
                _process(deepcopy(data), context, tmp)
                out.update(tmp)
            
            # remove context
            if context_name == "item":
                context[context_name].pop()

        elif "_include" in data.keys():
            value = data["_include"]["from"]
            data.pop("_include")
            data.update(_jq(value, context))
            _process(data, context, out)
        else:
            for k, v in data.items():
                key = _jq(k, context)
                out[key] = _process(v, context, out={})

    elif isinstance(data, list):
        out = []
        for elm in data:
            if isinstance(elm, dict):
                if "_dup" in elm.keys():
                    value = elm["_dup"]["with"]
                    context_name = elm["_dup"].get("to", "item")
                    ret = _jq(value, context)

                    # clear out.
                    # _dup is overwrite every items
                    out = []

                    # prepare context
                    if context_name == "item":
                        if context_name not in context:
                            context[context_name] = []
                        context[context_name].append({})

                    data_tmp = [elm for elm in data
                            if not isinstance(elm, dict) or (isinstance(elm, dict) and "_dup" not in elm.keys())]
                    # duplicate loop
                    for elm2 in enumerate(ret) if isinstance(ret, list) else ret.items():
                        # update context
                        if context_name == "item":
                            context[context_name][-1] = elm2
                        else:
                            context[context_name] = elm2

                        # clone data without "_dup" object
                        tmp = []
                        tmp = _process(data_tmp, context, tmp)
                        out.extend(tmp)

                    # remove context
                    if context_name == "item":
                        context[context_name].pop()

                    # replace list with duplicated list
                    break

                elif "_include" in elm.keys():
                    # import pdb; pdb.set_trace()
                    value = elm["_include"]["from"]
                    data.extend(_jq(value, context))
                else:
                    out.append(_process(elm, context, out={}))
            else:
                out.append(_process(elm, context, out=[]))
    else:
        out = _jq(data, context)

    return out

def process(data, context):
    """
    process extended-yaml data

    :param dict, list: target data
    :param dict: context data
    :return: processed extended-yaml data
    """
    return _process(deepcopy(data), deepcopy(context), {})
