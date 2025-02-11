"""
Given a sql file, splits the file into multiple smaller files that are less than 100MB,
where it should split at the end of the last full statement within the chunk. Thus,
each split file should be executable on its own within the sequence of files.
"""

import os
import sys

limit = 95
# GitHub has a 100MB file size limit, so we need to make sure our split files are smaller than that.
chunk_size = limit * 1024 * 1024  # 95MB

file_path = sys.argv[1]
if not file_path.endswith(".sql"):
    raise SystemExit(f"{file_path} is not a .sql file.")

# print(file_path)
file_size = os.path.getsize(file_path)

if file_size <= chunk_size:
    raise SystemExit(f"{os.path.basename(file_path)} is {file_size / (1024 * 1024):.2f} MB, which is not larger than {limit}MB, skipping.")

next_chunk = b''
with open(file_path, "rb") as f:
    chunk_number = 0
    [root,ext] = os.path.splitext(file_path)
    while True:
        chunk = next_chunk + f.read(chunk_size)
        next_chunk = b''
        idx = max(chunk.rfind(b"';\n"), chunk.rfind(b");\n"))
        if idx > -1:
            next_chunk = chunk[idx + 3:]
            chunk = chunk[:idx + 3]
        if not chunk:
            break  # End of file reached
        chunk_name = f"{root}.part{chunk_number:03}{ext}"
        with open(chunk_name, "wb") as chunk_file:
            chunk_file.write(chunk)

        # print(f"Written chunk {chunk_number:03} to {chunk_name}")
        chunk_number += 1

if next_chunk.strip():
    raise SystemExit("The file was not split correctly, found dangling chunk.")

os.remove(file_path)
