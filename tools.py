import os
import requests
import shutil
import re

def retry(func):
    def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}")
        return None
    return wrapper


def check_file_exists(local_dir, check_files):
    if not isinstance(check_files, list):
        check_files = list(check_files)
    return all(os.path.exists(os.path.join(local_dir, file)) for file in check_files)


@retry
def DownloadGithubProject(repo_id: str, local_dir: str, check_file: list) -> None:
    owner, repository = repo_id.split('/')
    url = f"https://api.github.com/repos/{owner}/{repository}/zipball"
    if not check_file_exists(os.path.join(local_dir, repository), check_file):
        print("Downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            zip_file_path = f"{local_dir}/{repository}.zip"
            with open(zip_file_path, "wb") as file:
                file.write(response.content)
            shutil.unpack_archive(zip_file_path, local_dir)
            os.remove(zip_file_path)
            for folder in os.listdir(local_dir):
                if os.path.isdir(f"{local_dir}/{folder}") and folder.startswith(f"{owner}-{repository}-"):
                    os.rename(f"{local_dir}/{folder}", f"{local_dir}/{repository}")
                    break
        

def check_uvr():
    folders = [i for i in os.listdir() if os.path.isdir(i)]
    for folder in folders:
        if re.search(r"ultimatevocalremovergui", folder):
            return folder, check_file_exists(folder, ["UVR.py", "separate.py"])
    return None, None


def copy_folder(source_folder, target_folder):
    os.makedirs(target_folder, exist_ok=True)

    for root, dirs, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        target_path = os.path.join(target_folder, relative_path)
        os.makedirs(target_path, exist_ok=True)

        for file in files:
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, file)
            shutil.copy(source_file_path, target_file_path)


DownloadGithubProject("MiyazonoKaori137/ultimatevocalremovergui",
                                     os.getcwd(), ["UVR.py", "separate.py"])
copy_folder("assets/uvr5_config", "ultimatevocalremovergui/gui_data")
shutil.copy("assets/code/UVR-CLI.py", "ultimatevocalremovergui")