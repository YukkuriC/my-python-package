import os, yaml
from jinja2 import Environment, FileSystemLoader
from YukkuriC.files import wrap_folder

if 'prepare data':
    # type,name,side,category,descrip,default_cfg
    data = []

    def load_data_yaml(path):
        global data
        with open(path) as f:
            data = yaml.load(f, yaml.Loader)

    class _AttrGetter:

        def __init__(self, callback):
            self.callback = callback

        def __getattr__(self, attr):
            return self.callback(attr)

        __call__ = __getattr__

    filter_val = _AttrGetter(
        lambda key: _AttrGetter(lambda val: [l for l in data if l[key] == val])
    )

    def define_sub(line):
        type = line['type']
        if type in ('int', 'double'):
            return 'InRange'
        if type == 'enum':
            return 'Enum'
        return ''

    def group_val(subdata, attr):
        grouper, res = {}, []
        for l in subdata:
            key = l[attr]
            if key not in grouper:
                grouper[key] = []
                res.append([key, grouper[key]])
            grouper[key].append(l)
        return res

    def to_java_type(raw):
        if raw == 'int':
            return 'Integer'
        return raw.capitalize()


def load_env(root, dir='templates'):
    root = wrap_folder(root)
    return Environment(loader=FileSystemLoader(os.path.join(root, dir)))


def gen_file(env, template, target):
    print(os.path.relpath(template), '->', os.path.relpath(target))
    with open(os.path.join(target), 'w', encoding='utf-8') as f:
        print(env.get_template(template).render(**globals()), file=f)


def batch_gen(env, targets, ext='.java', root_dir='..'):
    for target in targets:
        gen_file(env, target + ext, os.path.join('..', targets[target]))


__all__ = ['load_data_yaml', 'load_env', 'gen_file', 'batch_gen']
