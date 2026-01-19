from YukkuriC.files.file_loader import loadjson, loadtext
from YukkuriC.minecraft.secret_loader import SECRETS
from YukkuriC.minecraft.version_picker import load_curseforge_version_map
import os, requests, json

CFG = {}
CHANGELOG = ''


def load_cfg_changelog(cfg_path, changelog_path=None):
    global CFG
    CFG = loadjson(cfg_path)

    if changelog_path:
        global CHANGELOG
        try:
            CHANGELOG = loadtext(changelog_path)
        except:
            CHANGELOG = ''

    if CFG.get('mock'):

        def mock_post(*a, **kw):
            print('POST', a, kw)
            return mock_post

        mock_post.text = 'MOCK'
        mock_post.status_code = 114514

        requests.post = mock_post


curseforge_version_map = load_curseforge_version_map()


def build_pusher(
    filename_contents='mod_name,platform,game_version,mod_version',
    mod_name='foo',
    platform=None,
    game_version='bar',
    mod_version='baz',
    mod_version_full_format="{game_version}-{mod_version}",
):
    filename_arg_names = filename_contents.split(',')

    deps = [
        {"project_id": dep, "dependency_type": "required"}
        for dep in CFG['MR']['dependencies']
    ]
    if 'optional' in CFG['MR']:
        deps += [
            {"project_id": dep, "dependency_type": "optional"}
            for dep in CFG['MR']["optional"]
        ]

    def push_file(file):
        arg_map = {
            'platform': platform,
            'game_version': game_version,
            'mod_version': mod_version,
            'mod_name': mod_name,
        }
        filename = os.path.basename(file)
        print("UPLOADING:", filename)
        filename_body = os.path.splitext(filename)[0]
        for arg, data in zip(filename_arg_names, filename_body.split('-')):
            arg_map[arg] = data
        mod_version_full = mod_version_full_format.format_map(arg_map)

        # https://docs.modrinth.com/api/operations/createversion/
        if not CFG['MR'].get('ignored'):
            header = {
                "Authorization": SECRETS['auth_mr'],
                "User-Agent": f"YukkuriC/{arg_map['mod_name']}",
                # "Content-Type": "multipart/form-data"
            }
            data = {
                "name": filename_body,
                "version_number": mod_version_full,
                "changelog": CHANGELOG,
                "dependencies": deps,
                "game_versions": [arg_map['game_version']],
                "version_type": "release",
                "loaders": [arg_map['platform']],
                "featured": True,
                "status": "listed",
                "project_id": CFG['MR']['project_id'],
                "file_parts": [filename],
                "primary_file": filename,
            }

            response = requests.post(
                "https://api.modrinth.com/v2/version",
                data={
                    "data": json.dumps(data),
                },
                headers=header,
                files={filename: open(file, 'rb')},
            )
            print(response.text, "MR", response.status_code)

        # https://support.curseforge.com/en/support/solutions/articles/9000197321-curseforge-upload-api
        if not CFG['CF'].get('ignored'):
            data = {
                "changelog": CHANGELOG,
                "changelogType": "markdown",
                "displayName": filename,
                "gameVersions": [
                    # client & server
                    *(9638, 9639),
                    8326,  # java 17 TODO java 21
                    (
                        7498 if arg_map['platform'] == 'forge' else 7499
                    ),  # forge or fabric TODO neoforge
                    curseforge_version_map[arg_map['game_version']],
                ],
                "releaseType": "release",
            }
            header = {
                "X-Api-Token": SECRETS['auth_cf'],
            }

            response = requests.post(
                f"https://minecraft.curseforge.com/api/projects/{CFG['CF']['project_id']}/upload-file",
                data={
                    "metadata": json.dumps(data),
                },
                headers=header,
                files={"file": open(file, 'rb')},
            )
            print(response.text, "CF", response.status_code)

    return push_file


def push_all(root, pusher):
    for sub in os.listdir(root):
        if not sub.endswith('.jar'):
            continue
        pusher(sub)


__all__ = [
    'load_cfg_changelog',
    'build_pusher',
    'push_all',
]

if __name__ == '__main__':
    for sub in os.listdir('.'):
        if not sub.endswith('.jar'):
            continue
        push_file(sub)
