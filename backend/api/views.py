from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers import UsersCreateSerializers

User = get_user_model()


class UsersViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    queryset = User.objects.order_by('id').all()
    permission_classes = [permissions.AllowAny]
    # serializer_class = UsersCreateSerializers

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
    #     if self.action == 'list':
    #         return UsersSerializers
    #     # elif self.action == 'retrieve':
    #     #     return RetrieveUserSerializer
    #     return self.serializer_class

    # def get_permissions(self):
    #     if self.action == 'create':
    #         self.permission_classes = [permissions.AllowAny]
    #     elif self.action == 'list':
    #         self.permission_classes = [permissions.IsAuthenticated]
    #     elif self.action == 'retrieve':
    #         self.permission_classes = [permissions.IsAuthenticated]
    #     return super().get_permissions()

    @action(['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            # filterset_class=[]
            )
    def me(self, request, *args, **kwargs):
        # self.retrieve(request, *args, **kwargs)
        serializer = UsersCreateSerializers(self.request.user)
        return Response(serializer.data)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
