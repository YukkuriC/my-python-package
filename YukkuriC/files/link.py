import os, subprocess


def linkFolder(link: str, src: str, flag='/J'):
    if not os.path.isdir(src) or os.path.isdir(link):
        return
    os.makedirs(os.path.dirname(link), exist_ok=True)
    subprocess.run(
        ['cmd', '/c', 'mklink', flag, os.path.abspath(link), os.path.abspath(src)],
        shell=True,
    )
