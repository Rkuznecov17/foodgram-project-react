from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientsViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)
from users.views import SubscribeViewSet


app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/',
         SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create',
                                   'delete': 'destroy'}), name='subscribe'),
    path('recipes/<int:id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'destroy'}), name='favorite'),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
]
