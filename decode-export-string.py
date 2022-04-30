#!/usr/bin/python3

import base64
import collections
import json
import zlib
import io
import sys

def error(*args):
    print(*args, file=sys.stderr, flush=True)

################################################################
#
# main

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")

    exchange_str = sys.stdin.read().strip()
    version_byte = exchange_str[0]

    if version_byte=='0':
        json_str = zlib.decompress( base64.b64decode(exchange_str[1:]) )
        data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
        json.dump(data, sys.stdout, separators=(",", ":"), indent=1, ensure_ascii=False )
    else:
        error( "Unsupported version: {0}".format( version_byte ) )
        exit(2)
