import os, sys

root_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_path)

from YukkuriC.files.link import *

module_name = 'YukkuriC'
modules_root = [p for p in sys.path if 'site-packages' in p][0]
print('target =', modules_root)
link_folder(
    os.path.join(modules_root, module_name),
    os.path.join(root_path, module_name),
)
