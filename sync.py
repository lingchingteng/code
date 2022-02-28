import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def sync(source, dest):
    # traverse source folder, and construct a dictionary which key is the hash of the path.
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for fn in files:
            source_hashes[hash_file(Path(folder) / fn)] = fn

    # trace the files we found in target.
    seen = set()

    # traverse traget folder, and get filename and hash
    for folder, _, files in os.walk(dest):
        for fn in files:
            dest_path = Path(folder) / fn
            dest_hash = hash_file(dest_path)

            seen.add(dest_hash)

            # if the file is not in source files.
            if dest_hash not in source_hashes:
                dest_path.remove()
            elif dest_path != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    for src_path, fn in source_hashes.items():
        if src_path not in seen:
            shutil.copy(Path(source) / fn, Path(dest) / fn)
