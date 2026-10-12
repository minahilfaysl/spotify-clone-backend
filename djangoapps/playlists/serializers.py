from rest_framework import serializers
from djangoapps.playlists.models import Playlist, Track
from djangoapps.songs.serializers import SongSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    # always the logged-in user, never taken from the request body; the
    # default keeps the (user, playlist_name) uniqueness check working
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

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

    def validate_playlist(self, playlist):
        request = self.context.get('request')
        if request and playlist.user_id != request.user.id:
            raise serializers.ValidationError(
                'You can only add songs to your own playlists.')
        return playlist
