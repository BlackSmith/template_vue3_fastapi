import json
import yaml
from fastapi import HTTPException, status



def get_yaml(filename: str) -> dict:
    with open(filename, 'r+') as fd:
        return yaml.load(fd, Loader=yaml.FullLoader)


def str2set(value):
    if isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, list):
        value = set(value)
    return value