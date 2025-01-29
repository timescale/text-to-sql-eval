"""
Given a postgres dump file, run through the file and:
1. remove any line that starts with --
2. remove any line that starts with SET or SELECT
3. remove any consecutive empty lines
"""

import click


@click.command()
@click.argument("file_path")
def main(file_path):
    with open(file_path, "r") as inp:
        to_write = []
        lines = 0
        last_line_empty = False
        for line in inp:
            if line.startswith("SELECT"):
                continue
            if line.startswith("SET"):
                continue
            if line.startswith("--") and (lines == 0 or last_line_empty):
                continue
            last_line_empty = line.strip() == ""
            to_write.append(line)
            lines += 1
        while to_write and to_write[0].strip() == "":
            to_write.pop(0)
        while to_write and to_write[-1].strip() == "":
            to_write.pop()
    with open(file_path, "w") as out:
        for i in range(len(to_write)):
            if i > 0 and to_write[i - 1].strip() == "" and to_write[i].strip() == "":
                continue
            out.write(to_write[i])
        out.write("\n")


if __name__ == "__main__":
    main()
