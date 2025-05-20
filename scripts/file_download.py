import os
import shutil
import time
from typing import Collection, Dict

import libtorrent as lt
import pandas as pd


def dump_subreddit_submissions(
    subnames: Collection[str], download_dir: str, torrent_path: str
) -> Dict[str, str]:
    file_paths = {}
    os.makedirs(download_dir, exist_ok=True)
    torrent_info = lt.torrent_info(torrent_path)

    session = lt.session()
    params = {
        "save_path": download_dir,
        "storage_mode": lt.storage_mode_t.storage_mode_sparse,
    }
    torrent_handle = session.add_torrent({"ti": torrent_info, **params})

    # Disable all files initially
    torrent_handle.prioritize_files([0] * torrent_info.num_files())

    # Selectively enable files based on partial matches and pre-check if they exist
    file_storage = torrent_info.files()
    selected_indices = []

    for idx in range(torrent_info.num_files()):
        file_path = file_storage.file_path(idx)

        # Extract only the filename (ignore folder structure)
        filename = os.path.basename(file_path)

        for subname in subnames:
            if filename.lower() == f"{subname}_submissions.zst":
                full_path = os.path.join(download_dir, filename)
                file_paths[subname] = full_path

                # Skip if the file is already downloaded
                if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                    print(f"Skipping (already exists): {filename}")
                else:
                    torrent_handle.file_priority(idx, 1)  # Enable download
                    selected_indices.append((idx, filename))
                    print(f"Selected for download: {filename}")

    if not selected_indices:
        print("No new matching files found. Exiting.")
        return file_paths

    # Start downloading
    print(f"Downloading {len(selected_indices)} selected files...")

    while True:
        s = torrent_handle.status()
        file_progress = torrent_handle.file_progress()

        # Check if all selected files are fully downloaded
        if all(
            file_progress[idx] >= file_storage.file_size(idx)
            for idx, _ in selected_indices
        ):
            print("\nAll selected files downloaded. Stopping torrent...")
            session.remove_torrent(torrent_handle)  # Removes torrent but keeps files
            break

        # Print progress
        progress = s.progress * 100
        print(f"Progress: {progress:.2f}% - Downloaded {s.total_done} bytes", end="\r")
        time.sleep(5)

    # **Move files to the final location (flatten the structure)**
    for idx, filename in selected_indices:
        # Find the actual downloaded file path
        subdir_file_path = os.path.join(download_dir, file_storage.file_path(idx))
        final_path = os.path.join(download_dir, filename)

        # Move only if it exists in a subdirectory
        if os.path.exists(subdir_file_path) and subdir_file_path != final_path:
            shutil.move(subdir_file_path, final_path)  # Move the file
            print(f"Moved: {subdir_file_path} -> {final_path}")

    # **Remove any leftover empty folders inside Download/**
    for root, dirs, files in os.walk(download_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):  # If folder is empty
                os.rmdir(dir_path)

    print("All files moved to:", download_dir)
    return file_paths


if __name__ == "__main__":
    csv_file = "data/sublist.csv"
    df = pd.read_csv(csv_file, names=["subs"])
    subs = {sub.strip().lower() for sub in df["subs"]}
    print("Found file ",subs)

    # Define torrent paths
    torrent_path = "reddit.torrent"
    download_dir = "./data/archived_submissions/"  # Custom download directory
    dump_subreddit_submissions(subs, download_dir, torrent_path)
