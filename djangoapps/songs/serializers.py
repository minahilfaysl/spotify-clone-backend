from rest_framework import serializers
from djangoapps.songs.models import Song, Album, Genre
from django.contrib.auth import get_user_model


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['profile_name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    artist_details = ArtistSerializer(
        source='artist',
        many=False,
        read_only=True
    )

    class Meta:
        model = Album
        fields = '__all__'


class SongSerializer(serializers.ModelSerializer):
    album_details = AlbumSerializer(source='album', many=False, read_only=True)

    class Meta:
        model = Song
        fields = '__all__'
