import os, subprocess, shutil
from YukkuriC.files import is_junction


def link_folder(link: str, src: str, flag='/J'):
    if not is_junction(link):
        shutil.rmtree(link)
    if not os.path.isdir(src):
        return
    os.makedirs(os.path.dirname(link), exist_ok=True)
    subprocess.run(
        ['cmd', '/c', 'mklink', flag, os.path.abspath(link), os.path.abspath(src)],
        shell=True,
    )


__all__ = ['link_folder']
