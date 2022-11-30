from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    search_fields = ('name',)


# class RecipeIngredientInline(admin.TabularInline):
#     model = RecipeIngredient
#     extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_of_favorites')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    # inlines = (RecipeIngredientInline,)

    def count_of_favorites(self, obj):
        return obj.favorites.count()
    count_of_favorites.short_description = 'счетчик добавлений в избранное'


# class RecipeIngredientAdmin(admin.ModelAdmin):
#     inlines = (RecipeIngredientInline,)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
# admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

# Разобраться, почему все работало два дня назад. Ошибка:
# <class 'recipes.admin.RecipeIngredientInline'>: (admin.E202) 'recipes.RecipeIngredient' has no ForeignKey to 'recipes.RecipeIngredient'.
