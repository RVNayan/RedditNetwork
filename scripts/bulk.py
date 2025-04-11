import os
import subprocess

def process_line():
    list_file = "./data/bulk/list.csv"
    sublist_file = "./data/sublist.csv"
    done_file = "./data/bulk/done.csv"

    if not os.path.exists(list_file) or os.stat(list_file).st_size == 0:
        print("list.csv is empty or does not exist.")
        return False

    with open(list_file, "r") as file:
        lines = file.readlines()

    if not lines:
        print("list.csv is empty.")
        return False

    with open(sublist_file, "w") as file:
        file.write(lines[0])

    with open(list_file, "w") as file:
        file.writelines(lines[1:])

    print(f"Moved line to {sublist_file}: {lines[0].strip()}")

    print("Running file_download.py...")
    subprocess.run(["python3", "./scripts/file_download.py"])

    print("Running extractor.py...")
    subprocess.run(["python3", "./scripts/extractor.py"])

    # Append the processed line to done.csv
    with open(done_file, "a") as file:
        file.write(lines[0])

    # Clear sublist.csv
    open(sublist_file, "w").close()

    # Track progress
    total_done = sum(1 for _ in open(done_file))
    print(f"Progress: {total_done} files processed.")

    return True


while True:
    if not process_line():
        print("Processing complete. list.csv is empty.")
        break