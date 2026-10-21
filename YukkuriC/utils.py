import os

if 'Input IO':

    def input_choose_from(targets, textPre='Select from:', textInput='index: '):
        while 1:
            try:
                print(textPre)
                for i, x in enumerate(targets):
                    print(f'[{i}] - {x}')
                select = int(input(textInput))
                return targets[select]
            except KeyboardInterrupt:
                raise
            except:  # noqa: E722, S110
                pass

    def _list_folder_depth(root, depth):
        if depth <= 1:
            yield from os.listdir(root)
            return
        for sub in os.listdir(root):
            sroot = os.path.join(root, sub)
            if not os.path.isdir(sroot):
                continue
            for ss in _list_folder_depth(sroot, depth - 1):
                yield os.path.join(sub, ss)

    def input_choose_folder_child(
        root,
        depth=1,
        validator=None,
        sorter=None,
        textPre='Select from:',
        textInput='index: ',
    ):
        subs = [*_list_folder_depth(root, depth)]
        if validator:
            subs = [p for p in subs if validator(os.path.join(root, p))]
        if sorter:
            subs.sort(key=lambda p: sorter(os.path.join(root, p)))
        return os.path.join(root, input_choose_from(subs, textPre, textInput))
