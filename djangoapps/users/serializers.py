import uuid

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class UserProfileDataSerializer(serializers.ModelSerializer):

    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'profile_name', 'profile_photo',
                  'is_artist']

    def get_profile_photo(self, obj):
        return self.context.get('request').build_absolute_uri(
            obj.profile_photo.url)


class UserPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['is_artist']


class SignupSerializer(serializers.ModelSerializer):
    '''serializer to allow the user to signup'''
    User = get_user_model()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password', 'password2', 'profile_name',
                  'date_of_birth', 'gender']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create(
            username=uuid.uuid4().hex,
            email=validated_data['email'],
            profile_name=validated_data['profile_name'],
            date_of_birth=validated_data['date_of_birth'],
            gender=validated_data['gender']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''serializer to help the user login with either username or email'''

    def validate(self, attrs):
        '''overriding this method to allow login with either username or
        email, returns the username and token'''
        User = get_user_model()
        credentials = {
            'username': attrs.get("username"),
            'password': attrs.get("password")
        }

        user = (User.objects.filter(email=attrs.get("username")).first() or
                User.objects.filter(username=attrs.get("username")).first())

        if user:
            credentials['username'] = user.username

        token = super().validate(credentials)

        return {
            'user': UserProfileDataSerializer(user, context={
                'request': self.context.get('request')
            }).data,
            'token': token
        }

    @classmethod
    def get_token(cls, user):
        token = super(EmailTokenObtainPairSerializer, cls).get_token(user)
        return token


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    '''
    PUT /api/users/update_profile/{username}/
    '''
    class Meta:
        model = get_user_model()
        fields = ('profile_name', 'profile_photo')

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.username != instance.username:
            raise serializers.ValidationError({
                "authorize": "You dont have permission for this user."})

        instance.profile_name = validated_data['profile_name']
        # uploading a profile picture is optional
        try:
            instance.profile_photo = validated_data['profile_photo']
        except KeyError:
            pass

        instance.save()

        return instance
