#!/usr/bin/python3

import base64
import collections
import json
import zlib
import io
import sys
import argparse

def error(*args):
    print(*args, file=sys.stderr, flush=True)

################################################################
#
# main

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Converts a import/export string into plain JSON")
    parser.add_argument("-i", "--indent", default=1, type=int, dest="i",
        help="If indent is a non-negative integer or string, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0, negative, or "" will only insert newlines (default=1)."),
    parser.add_argument("-s1", "--separator1", default=",", type=str, dest="s1",
        help='The default is ",".')
    parser.add_argument("-s2", "--separator2", default=":", type=str, dest="s2",
        help='The default is ":".')
    opt = parser.parse_args()
    
    exchange_str = sys.stdin.read().strip()
    version_byte = exchange_str[0]

    if version_byte=='0':
        json_str = zlib.decompress( base64.b64decode(exchange_str[1:]) )
        data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
        json.dump(data, sys.stdout, separators=( (opt.s1, opt.s2) ), indent=opt.i, ensure_ascii=False )
    else:
        error( "Unsupported version: {0}".format( version_byte ) )
        exit(2)
