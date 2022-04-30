#!/usr/bin/python3

import base64
import collections
import json
import zlib
import sys
import io

################################################################
#
# main

if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding="utf-8")
    
    json_str = sys.stdin.read().strip()
    data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)

    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False ).encode("utf8")
    encoded = base64.b64encode( zlib.compress(json_str, 9) )
    
    sys.stdout.write('0' + encoded.decode())

