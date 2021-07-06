# usage: python auto_update_endpoint_support_file.py <sdk_directory> <block_name>

from copy import deepcopy
import os, sys
api_version = 3200
block_number = 0  # block_number is 1 for OV and 2 for i3s
block_count = 0
file_name = "endpoints-support.md"
new_file_name = "endpoints-support_new.md"
column_count = 0
dir_name = "."


def is_endpoint_header(line, column_count):
    if line.startswith("| Endpoints"):
        versions = line.split('|')[:-1]

        if versions[-1].strip()[1:] == str(api_version):
            print("New api version already present in header..")
            versions.append("")
        else:
            last_version = deepcopy(versions[-1])
            new_version = last_version.replace(last_version.strip()[1:], str(api_version))
            versions.extend([new_version, ""])
            column_count = len(versions)
            print("Added new api version in header..")
        line = "|".join(versions)

    return line, column_count

def update_each_endpoint(line, column_count):
    line_column_count = len(line.split('|'))
    if line_column_count == column_count - 1:
        splitted_columns = line.split('|')[:-1]
        last_column = deepcopy(splitted_columns[-1])
        splitted_columns.extend([last_column, ""])
        line = "|".join(splitted_columns)
    return line, column_count


if len(sys.argv) == 2:
    dir_name = sys.argv[1]
elif len(sys.argv) == 3:
    dir_name = sys.argv[1]
    if sys.argv[2].lower() == "ov":
        block_number = 1
    elif sys.argv[2].lower() == "i3s":
        block_number = 2

os.chdir(dir_name)
f_read = open(file_name, "r")
f_write = open(new_file_name, "a")
endpoint_lines = f_read.readlines()
for line in endpoint_lines:
    line = line.strip("\n")
    if line.startswith("##"):
        block_count += 1
    if block_count == block_number:
        line, column_count = is_endpoint_header(line, column_count)
        if line.startswith("|<sub>") or line.startswith("| ----"):
            line, column_count = update_each_endpoint(line, column_count)

    f_write.write(line + "\n")
f_write.close()
f_read.close()
# deleting older file and renaming the new file
os.remove(file_name)
os.rename(new_file_name, file_name)