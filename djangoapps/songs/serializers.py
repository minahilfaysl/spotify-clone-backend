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
    # always the logged-in artist, never taken from the request body; the
    # default keeps the (artist, album_name) uniqueness check working
    artist = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
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

    def validate_album(self, album):
        request = self.context.get('request')
        if request and album.artist_id != request.user.id:
            raise serializers.ValidationError(
                'You can only add songs to your own albums.')
        return album
