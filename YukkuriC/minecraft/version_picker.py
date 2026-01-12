from YukkuriC.minecraft.secret_loader import SECRETS
from YukkuriC.files.file_loader import opentext
import requests, json


def pick_versions(
    filterByFileTargets=(
        73407,  # 1.19.x
        75125,  # 1.20.x
        77784,  # 1.21.x
    ),
    versions_io=None,
    versionByName_io=None,
):
    header = {
        "X-Api-Token": SECRETS['auth_cf'],
    }
    versions = requests.get(
        "https://minecraft.curseforge.com/api/game/versions", headers=header
    )
    if versions_io:
        print(versions.text, file=versions_io)
    data = json.loads(versions.text)
    versionByName = {}
    for entry in data:
        if entry["gameVersionTypeID"] in filterByFileTargets:
            versionByName[entry['name']] = entry['id']
    if versionByName_io:
        json.dump(versionByName, versionByName_io, indent='\t')


if __name__ == '__main__':
    with open('versionByName.json', 'w') as f:
        pick_versions(versionByName_io=f)
