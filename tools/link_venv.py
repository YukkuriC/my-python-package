try:
    from YukkuriC.files.link import *
except:
    from linkSelf import *
    from YukkuriC.files.link import *
import os

module_name = 'YukkuriC'
root_path = os.path.dirname(os.path.dirname(__file__))
root_path = os.path.join(root_path, module_name)

target = input('venv outer location:')
target = os.path.join(target, 'venv/Lib/site-packages', module_name)

link_folder(target, root_path)
