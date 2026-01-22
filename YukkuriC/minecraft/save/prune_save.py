import os
from YukkuriC.files import wrap_folder


def do_prune(
    root,
    prune_sub=['region', 'poi', 'entities'],
    prune_xlim=[-1, 0],
    prune_ylim=[-1, 0],
    dim_roots_base=['.', 'DIM-1', 'DIM1'],
    prune_custom_dims=True,
    onFinish=exit,
):
    root = wrap_folder(root)
    os.chdir(root)

    prune_lims = set()
    for i in range(prune_xlim[0], prune_xlim[1] + 1):
        for j in range(prune_ylim[0], prune_ylim[1] + 1):
            prune_lims.add(f'r.{i}.{j}.mca')

    dim_roots = [*dim_roots_base]
    if prune_custom_dims:
        for sub1 in os.listdir('dimensions'):
            sub1 = os.path.join('dimensions', sub1)
            if not os.path.isdir(sub1):
                continue
            for sub2 in os.listdir(sub1):
                sub2 = os.path.join(sub1, sub2)
                if not os.path.isdir(sub2):
                    continue
                dim_roots.append(sub2)

    to_delete = []
    for dim in dim_roots:
        for sub in prune_sub:
            sub = os.path.join(dim, sub)
            if not os.path.isdir(sub):
                continue
            for f in os.listdir(sub):
                if f in prune_lims:
                    continue
                f = os.path.relpath(os.path.join(sub, f), '.')
                print('TO DELETE:', f)
                to_delete.append(f)

    if not to_delete:
        return onFinish()

    while 1:
        try:
            flag = input('Sure? (Y/n): ')[0].lower()
        except:
            continue
        if flag == 'y':
            for f in to_delete:
                os.remove(f)
        return onFinish()


__all__ = ['do_prune']
