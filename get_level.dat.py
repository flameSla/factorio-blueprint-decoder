#!/usr/bin/python
import sys
import zipfile
import zlib
import argparse
from pathlib import Path


def error(*args):
    print(*args, file=sys.stderr, flush=True)


def get_leveldat(save_file_name, out):
    zf = zipfile.ZipFile(save_file_name, "r")
    files = [f for f in zf.namelist()]
    root = Path(save_file_name).stem

    s2 = 0
    if "{}/level.dat".format(root) in files:
        file_name = "{}/level.dat".format(root)
        # unpacking the file
        out_file = open(out, "wb") if out else None
        with zf.open(file_name, "r") as file_to_read:
            compressed_data = file_to_read.read()
            decompressed_data = zlib.decompress(compressed_data)
            if out_file:
                out_file.write(decompressed_data)
            else:
                # to stdout
                sys.stdout.buffer.write(decompressed_data)

        if out_file:
            out_file.close()
    else:
        if "{}/level-init.dat".format(root) in files:
            index = 0
            file_name = "{}/level.dat{}".format(root, index)
            # unpacking the file
            out_file = open(out, "wb") if out else None
            while file_name in files:
                with zf.open(file_name, "r") as file_to_read:
                    compressed_data = file_to_read.read()
                    decompressed_data = zlib.decompress(compressed_data)
                    if out_file:
                        s2 += out_file.write(decompressed_data)
                    else:
                        # to stdout
                        s2 += sys.stdout.buffer.write(decompressed_data)

                index += 1
                file_name = "{}/level.dat{}".format(root, index)
            if out_file:
                out_file.close()

            # checking the file size
            with zf.open(
                "{0}/level.datmetadata".format(root), "r"
            ) as level_datmetadata:
                s1 = int.from_bytes(level_datmetadata.read(), "little", signed=False)
                if s1 != s2:
                    error(f"ERROR - incorrect size of the unpacked file.")
                    exit(2)


################################################################
#
# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Unpacks the level.dat file from the save."
    )
    parser.add_argument("save_file_name", nargs="?", default="_autosave1.zip")
    parser.add_argument("-o", "--out", type=str, default="")
    opt = parser.parse_args()

    get_leveldat(opt.save_file_name, opt.out)
