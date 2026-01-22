import os, zipfile, datetime
from YukkuriC.files import wrap_folder, is_junction


def do_zip(
    root,
    blacklist=["DIM1", "DIM-1", "dimensions"],
    target=None,
    axis_range_x=[-1, 0],
    axis_range_y=[-1, 0],
):
    root = wrap_folder(root)
    os.chdir(root)

    if not target:
        target = f"PACK_{os.path.basename(os.getcwd())}_{datetime.datetime.now().strftime('%m-%d')}.zip"

    try:
        os.remove(target)
    except:
        pass

    pack = zipfile.ZipFile(target, "w")

    skipped = []

    for f in os.listdir("."):
        if f.lower().endswith(".zip") or f == 'session.lock':
            continue
        if os.path.isfile(f):
            pack.write(f, f, 0)
            continue
        if f in blacklist:
            continue
        for root, dirs, files in os.walk(f):
            if is_junction(root):
                print('Skipped:', root)
                skipped.append(root)
                continue
            if any(root.startswith(black) for black in skipped):
                print('Skipped (sub):', root)
                continue
            for file in files:
                if file.startswith("r") and file.endswith(".mca"):
                    _, x, y, _ = file.split(".")
                    x = int(x)
                    y = int(y)
                    if not (x in axis_range_x and y in axis_range_y):
                        continue
                file = os.path.join(root, file)
                pack.write(file, file, 0)


__all__ = ['do_zip']
