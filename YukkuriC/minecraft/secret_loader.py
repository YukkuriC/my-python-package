from YukkuriC.files.file_loader import loadjson
import os

try:
    secret_root = os.path.dirname(__file__)
    secret_path = os.path.join(secret_root, 'secrets.json')
    SECRETS = loadjson(secret_path)
except:
    print(f'put "secrets.json" under {secret_root}')
    exit()


__all__ = ['SECRETS']
