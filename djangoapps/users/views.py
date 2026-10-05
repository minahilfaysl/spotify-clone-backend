from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from djangoapps.users.serializers import (
    UserProfileDataSerializer,
    SignupSerializer,
    EmailTokenObtainPairSerializer,
    UpdateUserProfileSerializer,
    UserPermissionSerializer,
)
from djangoapps.userdata.models import UserData

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignupView(generics.CreateAPIView):
    '''class based view to allow a new user to sign up'''
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if (serializer.is_valid()):
            user = serializer.save()
            # create user data for on making a new user object
            userdata = UserData(user=user)
            userdata.save()
            return Response({
                'token': get_tokens_for_user(user),
                'user': UserProfileDataSerializer(
                    user,
                    context={'request': request}
                ).data,
            })

        return Response(serializer.errors)


class EmailTokenObtainPairView(TokenObtainPairView):
    '''class based view to allow an existing user to login via email or
    username'''
    permission_classes = (AllowAny,)
    serializer_class = EmailTokenObtainPairSerializer


class UpdateProfileView(generics.UpdateAPIView):
    '''class based view to allow a user to update their profile name and
    picture'''
    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserProfileSerializer


class UpdateUserPermissionsView(generics.UpdateAPIView):
    '''class based view to change user permissions - is_artist'''
    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = (IsAuthenticated,)
    serializer_class = UserPermissionSerializer


class UserProfileView(generics.RetrieveAPIView):
    '''class based view to get user details for profile headers'''
    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserProfileDataSerializer
