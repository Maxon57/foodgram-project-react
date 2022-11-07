import json
import os
from inspect import getmembers, isclass
from typing import List
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()
from recipes import models
from recipes.models import Ingredient, Tag


def drop_data():
    for i in (i for i in getmembers(models) if
              isclass(i[1]) and "recipe.models" in i[1].__module__):
        i[1].objects.all().delete()


def open_file_json(file: str) -> List[dict]:
    path = os.path.join('static/data/', file + '.json')
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'Файла с путем {path} не существует!')


def main():
    data_files = [
        'ingredients',
        'tag'
    ]
    data_models = [
        Ingredient,
        Tag
    ]
    try:
        for num in range(len(data_models)):
            data_models[num].objects.bulk_create([
                data_models[num](**data) for data in open_file_json(data_files[num])
            ])
    except Exception as err:
        drop_data()
        print(f'Возникла ошибка: {err}')


if __name__ == '__main__':
    main()
