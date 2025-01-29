import os
import sys

limit = 95
# GitHub has a 100MB file size limit, so we need to make sure our split files are smaller than that.
chunk_size = limit * 1024 * 1024  # 95MB

file_path = sys.argv[1]
# print(file_path)
file_size = os.path.getsize(file_path)

if file_size <= chunk_size:
    # print(f"The file is {file_size / (1024 * 1024):.2f} MB, which is not larger than {limit}MB.")
    raise SystemExit()

with open(file_path, 'rb') as f:
    chunk_number = 0
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break  # End of file reached

        chunk_name = f"{file_path}-part{chunk_number:03}.bin"
        with open(chunk_name, 'wb') as chunk_file:
            chunk_file.write(chunk)

        # print(f"Written chunk {chunk_number:03} to {chunk_name}")
        chunk_number += 1

os.remove(file_path)
