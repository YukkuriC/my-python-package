import os, glob, shutil
from functools import partial


blacklisted_names = ['sources', 'dev']


def do_collect(root, pattern, do_clean=True, pattern_exist=None, renamer=None):
    if os.path.isfile(root):
        root = os.path.dirname(root)

    if do_clean:
        pp = pattern[0] if isinstance(pattern, (list, tuple)) else pattern
        exist_glob_root = pattern_exist or os.path.join(root, os.path.basename(pp))
        print('Cleaning:', exist_glob_root)
        for path in glob.glob(exist_glob_root):
            print('>', path)
            os.remove(path)

    patterns = pattern if isinstance(pattern, (list, tuple)) else [pattern]
    res = []
    for pattern in patterns:
        glob_root = os.path.abspath(os.path.join(root, pattern))
        print('Pattern:', glob_root)
        for path in glob.glob(glob_root):
            if any(x in path for x in blacklisted_names):
                continue
            print('>', path)
            if renamer:
                shutil.copy(path, os.path.join(root, renamer(os.path.basename(path))))
            else:
                shutil.copy(path, root)
            res.append(path)
    return res


do_collect_simple = partial(do_collect, pattern='../build/libs/*.jar')
do_collect_arch = partial(
    do_collect,
    pattern=[f'../{p}/build/libs/*.jar' for p in ('forge', 'neoforge', 'fabric')],
)

__all__ = ['do_collect', 'do_collect_simple', 'do_collect_arch']
