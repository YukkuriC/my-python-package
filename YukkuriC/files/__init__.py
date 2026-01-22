import os


def wrap_folder(root, postProcess=os.path.abspath):
    if os.path.isfile(root):
        root = os.path.dirname(root)
    if postProcess:
        root = postProcess(root)
    return root


# https://stackoverflow.com/questions/47469836/how-to-tell-if-a-directory-is-a-windows-junction-in-python
def is_junction(path: str) -> bool:
    try:
        return bool(os.readlink(path))
    except OSError:
        return False
