import os
import requests
import shutil
import re
from rich.progress import Progress

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
def DownloadGithubProject(repo_id: str, branch: str, local_dir: str, check_file: list) -> None:
    owner, repository = repo_id.split('/')
    url = f"https://api.github.com/repos/{owner}/{repository}/zipball/{branch}"
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


def DownloadGithubProject1(repo_id: str, branch: str, local_dir: str, check_file: list) -> None:
    from git import Repo
    owner, repository = repo_id.split('/')
    if not check_file_exists(os.path.join(local_dir, repository), check_file):
        print("Downloading...")
        repo_dir = os.path.join(local_dir, repository)
        
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        
        Repo.clone_from(f"https://github.com/{owner}/{repository}.git", repo_dir, branch=branch)


def check_uvr1():
    folders = [i for i in os.listdir() if os.path.isdir(i)]
    for folder in folders:
        if re.search(r"ultimatevocalremovergui", folder):
            return folder, check_file_exists(folder, ["UVR.py", "separate.py"])
    return None, None

def check_uvr2():
    folders = [i for i in os.listdir() if os.path.isdir(i)]
    for folder in folders:
        if re.search(r"Music-Source-Separation-Training", folder):
            return folder, check_file_exists(folder, ["train.py", "inference.py", "README.md"])
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


def download_model(url, local_dir, model_name):
    import wget
    os.makedirs(local_dir, exist_ok=True)
    if not os.path.exists(os.path.join(local_dir, model_name)):
        with Progress() as progress:
            task_id = progress.add_task("[cyan]Downloading...", total=100)

            def bar_progress(current, total, width=80):
                progress.update(task_id, advance=(current / total * 100) - progress.tasks[task_id].completed)

            wget.download(url, out=local_dir, bar=bar_progress)

def main1():
    if not check_uvr1()[1]:
        DownloadGithubProject("Anjok07/ultimatevocalremovergui",
                    "v5.6.0_roformer_add", os.getcwd(), ["UVR.py", "separate.py"])

    # DownloadGithubProject1("Anjok07/ultimatevocalremovergui",
    #                     "v5.6.0_roformer_add", os.getcwd(), ["UVR.py", "separate.py"])
    # DownloadGithubProject("Anjok07/ultimatevocalremovergui",
    #                     "master", os.getcwd(), ["UVR.py", "separate.py"])
    uvr_folder, uvr_exist = check_uvr1()
    if uvr_exist:
        if not os.path.exists(f"{uvr_folder}/UVR-CLI.py"):
            shutil.copy("assets/code/UVR-CLI.py", uvr_folder)
        if not os.path.exists(f"{uvr_folder}/separate.py"):
            shutil.copy("assets/code/separate.py", uvr_folder)
        copy_folder("assets/uvr5_config", f"{uvr_folder}/gui_data")

def main2():
    if not check_uvr2()[1]:
        DownloadGithubProject("ZFTurbo/Music-Source-Separation-Training",
                        "main", os.getcwd(), ["train.py", "inference.py", "README.md"])
    copy_folder("assets/config", "Music-Source-Separation-Training/configs/viperx")
    download_model("https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_368_sdr_12.9628.ckpt",
                    "Music-Source-Separation-Training/results", "model_bs_roformer_ep_368_sdr_12.9628.ckpt")
    if not os.path.exists("Music-Source-Separation-Training/inference-opt.py"):
        shutil.copy("assets/code/inference-opt.py", "Music-Source-Separation-Training")

if __name__ == "__main__":
    main1()
    main2()