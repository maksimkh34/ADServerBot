import os
import shutil


def import_data(filename: str,
                sym='='):
    result = []
    for line in open(filename, "r").readlines():
        line = line.replace("\n", "")
        result.append(line.split(sym))
    return result


def export_data(filename: str, data: [],
                sym='='):
    out = open(filename, "w")
    for line in data:
        out.write(sym.join(line) + "\n")
