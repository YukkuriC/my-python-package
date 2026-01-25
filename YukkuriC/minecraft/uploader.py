from YukkuriC.files.file_loader import loadjson, loadtext
from YukkuriC.minecraft.secret_loader import SECRETS
from YukkuriC.minecraft.version_picker import load_curseforge_version_map
import os, requests, json
import webbrowser

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

        def gen_mock(type):
            def mocker(*a, **kw):
                print(type.upper(), a, kw)
                return mocker

            mocker.text = 'MOCK'
            mocker.status_code = 114514
            print("MOCKED:", type)
            return mocker

        for t in 'get', 'post', 'patch':
            setattr(requests, t, gen_mock(t))


curseforge_version_map = load_curseforge_version_map()


HEADER_CF = {
    "X-Api-Token": SECRETS['auth_cf'],
}
HEADER_MR = {
    "Authorization": SECRETS['auth_mr'],
    "User-Agent": "YukkuriC/mod_uploader_py",
    # "Content-Type": "multipart/form-data"
}


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
        if 'MR' in CFG and not CFG['MR'].get('ignored'):
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
                headers=HEADER_MR,
                files={filename: open(file, 'rb')},
            )
            print(response.text, "MR", response.status_code)

        # https://support.curseforge.com/en/support/solutions/articles/9000197321-curseforge-upload-api
        if 'CF' in CFG and not CFG['CF'].get('ignored'):
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
            response = requests.post(
                f"https://minecraft.curseforge.com/api/projects/{CFG['CF']['project_id']}/upload-file",
                data={
                    "metadata": json.dumps(data),
                },
                headers=HEADER_CF,
                files={"file": open(file, 'rb')},
            )
            print(response.text, "CF", response.status_code)

    return push_file


def push_all(root, pusher):
    for sub in os.listdir(root):
        if not sub.endswith('.jar'):
            continue
        pusher(sub)


def upload_readme(readme_path='../README.md'):
    readme_path = os.path.abspath(readme_path)
    print("UPLOADING:", readme_path)

    with open(readme_path, encoding='utf-8') as f:
        readme = f.read()

    # https://docs.modrinth.com/api/operations/modifyproject/
    if 'MR' in CFG and not CFG['MR'].get('ignored'):
        response = requests.patch(
            f"https://api.modrinth.com/v2/project/{CFG['MR']['project_id']}",
            json={"body": readme},
            headers=HEADER_MR,
        )

        print(response.text, "MR", response.status_code)

    # damn, there's no such API for CF
    if 'CF' in CFG and not CFG['CF'].get('ignored'):
        url = f'https://authors.curseforge.com/#/projects/{CFG['CF']['project_id']}/description'
        webbrowser.open(url)


__all__ = [
    'load_cfg_changelog',
    'build_pusher',
    'push_all',
    'upload_readme',
]
