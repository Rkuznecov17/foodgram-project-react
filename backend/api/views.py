from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .paginations import RecipesPagination
from .permissions import IsAdminOrReadOnly, IsAuthorReadOnly
from .serializers import (IngredientSerializer, MinInfoRecipeSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorReadOnly,)
    pagination_class = RecipesPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

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

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def add_remove_favorite(self, request, pk=id):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = MinInfoRecipeSerializer()
            return Response(serializer.to_representation(instance=recipe),
                            status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(Favorite, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def add_remove_shopping_cart(self, request, pk=None):
        user = self.request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = MinInfoRecipeSerializer()
            return Response(serializer.to_representation(instance=recipe),
                            status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(ShoppingCart,
                                          user=user, recipe__id=pk)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
