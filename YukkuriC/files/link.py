import os, subprocess


def link_folder(link: str, src: str, flag='/J'):
    if not os.path.isdir(src) or os.path.isdir(link):
        return
    os.makedirs(os.path.dirname(link), exist_ok=True)
    subprocess.run(
        ['cmd', '/c', 'mklink', flag, os.path.abspath(link), os.path.abspath(src)],
        shell=True,
    )


__all__ = ['link_folder']
