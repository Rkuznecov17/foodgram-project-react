from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorReadOnly
from .serializers import (IngredientSerializer, MinInfoRecipeSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorReadOnly]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def for_responses(self, request, obj, id):
        item = obj.objects.filter(user=request.user, recipe__id=id)
        if (request.method == 'POST') and (not item.exists()):
            recipe = get_object_or_404(Recipe, id=id)
            obj.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeCreateSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif (request.method == 'DELETE') and (item.exists()):
            item.delete()
            return Response(
                {'success': 'Рецепт успешно удален.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Ошибка валидации.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        shopping_list = {}
        for ingredient in ingredients:
            name = ingredient[0]
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': ingredient[1],
                    'amount': ingredient[2]
                }
            else:
                shopping_list[name]['amount'] += ingredient[2]
        buying_list = 'Список покупок:\n'
        for number, (ingredient, value) in enumerate(
            shopping_list.items(), start=1
        ):
            buying_list += (
                f"{number}. {ingredient} - {value['amount']} "
                f"{value['measurement_unit']}\n"
            )
        spisok = 'buying_list.txt'
        response = HttpResponse(buying_list, content_type='text/plain')
        response['Content-Disposition'] = (f'attachment; filename={spisok}')
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = MinInfoRecipeSerializer
    queryset = Favorite.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = MinInfoRecipeSerializer()
        return Response(serializer.to_representation(instance=recipe),
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        del_object = Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id,
        )
        if del_object.exists():
            del_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
                    {'errors': 'Рецепт не был добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = MinInfoRecipeSerializer
    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в корзину.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = MinInfoRecipeSerializer()
        return Response(serializer.to_representation(instance=recipe),
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        del_object = ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=recipe_id,
        )
        if del_object.exists():
            del_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
                    {'errors': 'Рецепт не был добавлен в корзину.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
