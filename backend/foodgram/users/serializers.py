from django.contrib.auth.hashers import make_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from .models import Subscribe, User
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=make_password(validated_data['password'])
        )
        return user


class AuthorRecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserFollowSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Subscribe
        fields = ['author', 'user']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на автора.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance.author,
            context={'request': request}
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на автора.'
            )
        ]
    
    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на себя.'
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Подписка уже существует.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
    
    def get_is_subscribed(self, user):
        current_user = self.context['request'].user
        return (
            current_user.is_authenticated
            and Subscribe.objects.filter(user=current_user, author=user).exists()
        )

    def get_recipes(self, user):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return AuthorRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        return user.recipes.count()
