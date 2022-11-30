from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipes_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated and Favorite.objects.filter(user=user,
                                                             recipe=recipe
                                                             ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if (user.is_authenticated and ShoppingCart.objects.filter(user=user,
                                                                  recipe=recipe
                                                                  ).exists()):
            return True
        return False


class IngredoentForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredoentForRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
                                              many=True,
                                              queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)
        extra_kwargs = {
            'cooking_time': {'required': True}
        }

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Добавьте теги.')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиенты.')
        unique_check = list()
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if ((ingredient_id not in unique_check)
                and get_object_or_404(Ingredient,
                                      id=ingredient_id)):
                unique_check.append(ingredient_id)
            else:
                raise serializers.ValidationError('Проверьте id ингредиентов.')
        return ingredients

    def validate_name(self, name):
        if not name:
            raise serializers.ValidationError('Добавьте название.')
        return name

    def validate_text(self, text):
        if not text:
            raise serializers.ValidationError('Добавьте описание рецепта.')
        return text

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Добавьте изображение.')
        return image

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise serializers.ValidationError('Добавьте время приготовления.')
        return cooking_time

    def create(self, validated_data):
        taken_ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in taken_ingredients:
            its_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            RecipeIngredient.objects.create(
                ingredient=its_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        taken_ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        for ingredient in taken_ingredients:
            its_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            RecipeIngredient.objects.create(
                ingredient=its_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class MinInfoRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
