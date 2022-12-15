import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open(
            'data/ingredients.json', encoding='utf-8'
        ) as json_file:
            ingredients = json.load(json_file)
            for row in ingredients:
                ingredient = Ingredient()
                ingredient.name = row['name']
                ingredient.measurement_unit = row['measurement_unit']
                ingredient.save()
        print('Ингредиенты успешно добавлены.')
