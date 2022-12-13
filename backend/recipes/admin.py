from django.contrib import admin

from .models import (Ingredient, Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_of_favorites')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')

    def count_of_favorites(self, obj):
        return obj.favorites.count()
    count_of_favorites.short_description = 'счетчик добавлений в избранное'
