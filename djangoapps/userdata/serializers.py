from rest_framework import serializers
from djangoapps.userdata.models import (
    UserData,
    RecentlyPlayedAlbum,
    RecentlyPlayedPlaylist,
    UserAlbumLibrary,
    UserArtistLibrary,
    UserPlaylistLibrary,
)
from djangoapps.users.serializers import UserProfileDataSerializer
from djangoapps.songs.serializers import AlbumSerializer, SongSerializer
from djangoapps.playlists.serializers import PlaylistSerializer


class LikedAlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'user', 'liked_albums']


class LikedSongsSerializer(serializers.ModelSerializer):
    liked_songs_detail = SongSerializer(
        source='liked_songs',
        many=True,
        read_only=True
    )

    class Meta:
        model = UserData
        fields = ['id', 'user', 'liked_songs', 'liked_songs_detail']


class LikedPlaylistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'user', 'liked_playlists']


class RecentAlbumsSerializer(serializers.ModelSerializer):
    album_details = AlbumSerializer(
        source='album',
        many=False,
        read_only=True
    )

    class Meta:
        model = RecentlyPlayedAlbum
        fields = '__all__'


class RecentPlaylistsSerializer(serializers.ModelSerializer):
    playlist_details = PlaylistSerializer(
        source='playlist',
        many=False,
        read_only=True
    )

    class Meta:
        model = RecentlyPlayedPlaylist
        fields = '__all__'


class RecentlyPlayedSerializer(serializers.ModelSerializer):
    recently_played_albums = RecentAlbumsSerializer(many=True)
    recently_played_playlists = RecentPlaylistsSerializer(many=True)

    class Meta:
        model = UserData
        fields = [
            'id',
            'user',
            'recently_played_albums',
            'recently_played_playlists',
        ]


class ArtistLibrarySerializer(serializers.ModelSerializer):
    artist_details = UserProfileDataSerializer(
        source='artist',
        many=False,
        read_only=True
    )

    class Meta:
        model = UserArtistLibrary
        fields = '__all__'


class AlbumLibrarySerializer(serializers.ModelSerializer):
    album_details = AlbumSerializer(
        source='album',
        many=False,
        read_only=True
    )

    class Meta:
        model = UserAlbumLibrary
        fields = '__all__'


class PlayistLibrarySerializer(serializers.ModelSerializer):
    playlist_details = PlaylistSerializer(
        source='playlist',
        many=False,
        read_only=True
    )

    class Meta:
        model = UserPlaylistLibrary
        fields = '__all__'


class UserLibrarySerializer(serializers.ModelSerializer):
    artist_library = ArtistLibrarySerializer(many=True)
    album_library = AlbumLibrarySerializer(many=True)
    playlist_library = PlayistLibrarySerializer(many=True)

    class Meta:
        model = UserData
        fields = [
            'id',
            'user',
            'artist_library',
            'album_library',
            'playlist_library',
        ]


class FollowersSerializer(serializers.ModelSerializer):
    follower_details = UserProfileDataSerializer(
        source='followers',
        many=True,
        read_only=True
    )

    class Meta:
        model = UserData
        fields = ['id', 'user', 'followers', 'follower_details']


class FollowingSerializer(serializers.ModelSerializer):
    following_details = UserProfileDataSerializer(
        source='following',
        many=True,
        read_only=True
    )

    class Meta:
        model = UserData
        fields = ['id', 'user', 'following', 'following_details']
