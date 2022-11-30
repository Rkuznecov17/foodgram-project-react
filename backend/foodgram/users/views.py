from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Subscribe, User
from .serializers import SubscribeSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            if user.id == request.user.id:
                return Response(
                    {'errors': 'Нельзя подписываться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif Subscribe.objects.filter(user=user, author=user_id).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscribe = Subscribe.objects.create(
            user=request.user, author=user)
        serializer = SubscribeSerializer(subscribe,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['id']
        author = get_object_or_404(User, id=author_id)
        user = request.user
        del_subscribe = Subscribe.objects.filter(user=user, author=author)
        if del_subscribe.exists():
            del_subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
                    {'errors': 'Вы не были подписаны на автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
