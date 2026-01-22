import os


def wrap_folder(root, postProcess=os.path.abspath):
    if os.path.isfile(root):
        root = os.path.dirname(root)
    if postProcess:
        root = postProcess(root)
    return root
