import yaml
from copy import deepcopy
from logging import getLogger, StreamHandler, DEBUG, WARNING
from pprint import pprint as pp
from jq import jq
from eyaml import process

# initialize logging
logger = getLogger(__name__)
_handler = StreamHandler()
_handler.setLevel(DEBUG)
logger.addHandler(_handler)
logger.setLevel(WARNING)
_debug = logger.debug


def _process_with_debug(idx, ex, data, context, out={}):
    # enable debug while process data
    logger.setLevel(DEBUG)
    _debug("%03d: ##############################", idx)

    # process
    ret = process(data, context)
    
    # print summary
    _debug("<--: Input = %s", data)
    _debug("***: Result = %s", ret)
    _debug("-->: Expect = %s", ex)
    _debug("-->: %s", (ret == ex))
    _debug("")

    # restore logging level
    logger.setLevel(WARNING)

def main():

    # load example yaml
    with open("example.yml") as f:
        examples = yaml.load_all(f.read())

    # pull context data
    context = next(examples)

    # loop with test datas
    for index, data in enumerate(examples):
        for expect in examples:
            ret = process(data, context)
            if (ret != expect):
                _process_with_debug(index, expect, data, context)
            break

if __name__ == '__main__':
    main()
