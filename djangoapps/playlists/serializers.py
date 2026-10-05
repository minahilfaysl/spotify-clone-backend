from rest_framework import serializers
from djangoapps.playlists.models import Playlist, Track
from djangoapps.songs.serializers import SongSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    playlist_details = PlaylistSerializer(
        source='playlist',
        many=False,
        read_only=True
    )
    song_details = SongSerializer(
        source='song',
        many=False,
        read_only=True
    )

    class Meta:
        model = Track
        fields = '__all__'
