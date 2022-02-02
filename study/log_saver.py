import os
from pathlib import Path


def rename_files(base_path):
    log_file_numbers = []
    log_path = Path(base_path) / Path("logs/")
    log_path = log_path.absolute()
    log_files = log_path.rglob("log_file*.txt")
    if os.path.exists(log_path / "log_file.txt"):
        for file_name in list(log_files):
            last_item = file_name.name.split("_")[-1]
            if last_item != "file.txt":
                log_file_numbers.append(last_item)
        new_number = len(log_file_numbers) + 1
        os.rename(log_path / "log_file.txt", f"{str(log_path)}/log_file_{new_number}.txt")


if __name__ == "__main__":
    rename_files(Path(__file__).parent)
    exit(0)
