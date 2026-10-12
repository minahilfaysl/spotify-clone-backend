import datetime
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djangoapps.users.permissions import OwnsUserDataInURL
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djangoapps.songs.models import Song, Album
from djangoapps.playlists.models import Playlist
from djangoapps.userdata.models import (
    UserData,
    RecentlyPlayedAlbum,
    RecentlyPlayedPlaylist,
    UserArtistLibrary,
    UserAlbumLibrary,
    UserPlaylistLibrary,
)
from djangoapps.users.serializers import UserProfileDataSerializer
from djangoapps.songs.serializers import (
    SongSerializer,
    AlbumSerializer
)
from djangoapps.playlists.serializers import PlaylistSerializer
from djangoapps.userdata.serializers import (
    LikedAlbumsSerializer,
    LikedSongsSerializer,
    LikedPlaylistsSerializer,
    RecentAlbumsSerializer,
    RecentPlaylistsSerializer,
    RecentlyPlayedSerializer,
    ArtistLibrarySerializer,
    PlayistLibrarySerializer,
    AlbumLibrarySerializer,
    UserLibrarySerializer,
    FollowersSerializer,
    FollowingSerializer,
)
User = get_user_model()



class UserDataViewSet(viewsets.ModelViewSet):
    """
    Base for /api/userdata/<endpoint>/<username>/ routes.
    - Only the user themself can change (and, unless public_read, read) them.
    - Listing everyone's data, creating and deleting UserData rows over the
      API are disabled; only GET and PUT are exposed.
    """
    queryset = UserData.objects.select_related('user')
    permission_classes = [OwnsUserDataInURL]
    lookup_field = 'user__username'
    http_method_names = ['get', 'put', 'head', 'options']
    public_read = False

    def get_userdata(self, username):
        return get_object_or_404(UserData, user__username=username)


class LikedAlbumsViewSet(UserDataViewSet):
    """
    ViewSet for viewing and editing like_albums
    POST: Add to liked_albums, remove from liked_albums
    GET: View if an album was liked by a user
    """
    serializer_class = LikedAlbumsSerializer

    def update(self, request, user__username=None):
        try:
            album_id = request.data['liked_albums']
            userdata = self.get_userdata(user__username)
            user = request.user
            new_album = get_object_or_404(Album, id=album_id)

            # create new model object to add to albums library
            try:
                new_object = UserAlbumLibrary.objects.create(
                    user=user,
                    album=new_album
                )
                # continue adding to the list with updated timestamp
                userdata.album_library.add(new_object)
            except IntegrityError:
                duplicate_object = UserAlbumLibrary.objects.filter(
                    user=user,
                    album=new_album
                ).first()
                # delete that object and create the new one
                userdata.album_library.remove(duplicate_object)
                duplicate_object.delete()

            liked_list = userdata.liked_albums.all()
            if new_album in liked_list:
                userdata.liked_albums.remove(new_album)
                return Response(
                    data={"status": "removed from liked albums"},
                    status=status.HTTP_200_OK
                )
            else:
                userdata.liked_albums.add(new_album)
                return Response(
                    data={"status": "added to liked albums"},
                    status=status.HTTP_200_OK
                )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LikedSongsViewSet(UserDataViewSet):
    """
    ViewSet for viewing and editing liked_songs
    Add to liked_songs, remove from liked_songs
    View if a song was liked by a user
    """
    serializer_class = LikedSongsSerializer

    def update(self, request, user__username=None):
        try:
            song_id = request.data['liked_songs']
            userdata = self.get_userdata(user__username)
            new_song = get_object_or_404(Song, id=song_id)

            liked_list = userdata.liked_songs.all()
            if new_song in liked_list:
                userdata.liked_songs.remove(new_song)
                return Response(
                    data={"status": "removed from liked songs"},
                    status=status.HTTP_200_OK
                )
            else:
                userdata.liked_songs.add(new_song)
                return Response(
                    data={"status": "added to liked songs"},
                    status=status.HTTP_200_OK
                )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LikedPlaylistsViewSet(UserDataViewSet):
    """
    ViewSet for viewing and editing liked_playlists
    Add to liked_playlists, remove from liked_playlists
    View if a playlist was liked by a user
    """
    serializer_class = LikedPlaylistsSerializer

    def update(self, request, user__username=None):
        try:
            playlist_id = request.data['liked_playlists']
            userdata = self.get_userdata(user__username)
            user = request.user
            new_playlist = get_object_or_404(Playlist, id=playlist_id)

            # create new model object to add to albums library
            try:
                new_object = UserPlaylistLibrary.objects.create(
                    user=user,
                    playlist=new_playlist
                )
                # continue adding to the list with updated timestamp
                userdata.playlist_library.add(new_object)
            except IntegrityError:
                duplicate_object = UserPlaylistLibrary.objects.filter(
                    user=user,
                    playlist=new_playlist
                ).first()
                # delete that object and create the new one
                userdata.playlist_library.remove(duplicate_object)
                duplicate_object.delete()

            liked_list = userdata.liked_playlists.all()
            if new_playlist in liked_list:
                userdata.liked_playlists.remove(new_playlist)
                return Response(
                    data={"status": "removed from liked playlists"},
                    status=status.HTTP_200_OK
                )
            else:
                userdata.liked_playlists.add(new_playlist)
                return Response(
                    data={"status": "added to liked playlists"},
                    status=status.HTTP_200_OK
                )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )


class RecentlyPlayedViewSet(UserDataViewSet):
    """
    ViewSet for viewing and editing recently played albums / playlists
    Add to recently played, remove from recently played
    Storing maximum of the 6 most recent records each
    """
    serializer_class = RecentlyPlayedSerializer

    def retrieve(self, request, user__username=None):
        '''
        lists a user's top 6 recently played items, either albums or playlists
        based on their timestamps
        '''
        try:
            userdata = self.get_userdata(user__username)

            recents_list = []

            recently_played_albums = (userdata
                                      .recently_played_albums.all()
                                      .order_by('-date_added'))
            recently_played_playlists = (userdata
                                         .recently_played_playlists.all()
                                         .order_by('-date_added'))

            # get serialized album data
            serializer = RecentAlbumsSerializer(
                recently_played_albums,
                many=True,
                context={'request': request}
            )
            for item in serializer.data:
                recents_list.append(item)

            # get serialized playlist data
            serializer = RecentPlaylistsSerializer(
                recently_played_playlists,
                many=True,
                context={'request': request}
            )
            for item in serializer.data:
                recents_list.append(item)

            # sort the list according to date added (newest first)
            recents_list.sort(
                key=lambda x: datetime.datetime.strptime(
                    x['date_added'],
                    '%Y-%m-%dT%H:%M:%S.%f%z'
                ),
                reverse=True
            )

            # only return the most recent 6 records
            if len(recents_list) > 6:
                recents_list = recents_list[0:6]

            return Response(
                data={"recents_list": recents_list},
                status=status.HTTP_200_OK
            )
        except UserData.DoesNotExist:
            return Response(
                data={"recents_list": []},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=['put'])
    def update_albums(self, request, user__username=None):
        '''
        performs list updates for recently_played_albums and saves only the
        six most recent records for this many-to-many field
        '''
        try:
            userdata = self.get_userdata(user__username)
            user = request.user

            try:
                album_id = request.data['recently_played_albums']
            except KeyError:
                album_id = None

            # for albums
            if album_id:
                recent_album = get_object_or_404(Album, id=album_id)
                # create new model object to add to albums
                try:
                    new_object = RecentlyPlayedAlbum.objects.create(
                        user=user,
                        album=recent_album
                    )
                except IntegrityError:
                    duplicate_object = RecentlyPlayedAlbum.objects.filter(
                        user=user,
                        album=recent_album
                    ).first()
                    # delete that object and create the new one
                    userdata.recently_played_albums.remove(duplicate_object)
                    duplicate_object.delete()
                    new_object = RecentlyPlayedAlbum.objects.create(
                        user=user,
                        album=recent_album
                    )

                # continue adding to the list with updated timestamp
                userdata.recently_played_albums.add(new_object)

                # remove the oldest item from the list if length > 6
                data_list = (userdata
                             .recently_played_albums.all()
                             .order_by('-date_added'))
                list_length = len(data_list)
                if list_length > 6:
                    userdata.recently_played_albums.remove(data_list[-1])

                return Response(
                    data={"status": "added to recently played albums"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={"status": "please enter a valid album id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def update_playlists(self, request, user__username=None):
        '''
        performs list updates for recently_played_playlists and saves only the
        six most recent records for this many-to-many field
        '''
        try:
            userdata = self.get_userdata(user__username)
            user = request.user

            try:
                playlist_id = request.data['recently_played_playlists']
            except KeyError:
                playlist_id = None

            # for playlists
            if playlist_id:
                recent_playlist = get_object_or_404(Playlist, id=playlist_id)
                # create new model object to add to albums
                try:
                    new_object = RecentlyPlayedPlaylist.objects.create(
                        user=user,
                        playlist=recent_playlist
                    )
                except IntegrityError:
                    duplicate_object = RecentlyPlayedPlaylist.objects.filter(
                        user=user,
                        playlist=recent_playlist
                    ).first()
                    # delete that object and create the new one
                    userdata.recently_played_playlists.remove(duplicate_object)
                    duplicate_object.delete()
                    new_object = RecentlyPlayedPlaylist.objects.create(
                        user=user,
                        playlist=recent_playlist
                    )

                # continue adding to the list with updated timestamp
                userdata.recently_played_playlists.add(new_object)

                # remove the oldest item from the list if length > 6
                data_list = (userdata
                             .recently_played_playlists.all()
                             .order_by('-date_added'))
                list_length = len(data_list)
                while list_length > 6:
                    list_length = len(data_list)
                    userdata.recently_played_playlists.remove(
                        data_list[list_length-1]
                    )

                return Response(
                    data={"status": "added to recently played playlists"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={"status": "please enter a valid album id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLibraryViewSet(UserDataViewSet):
    """
    ViewSet for viewing and editing user library items
    """
    serializer_class = UserLibrarySerializer

    @action(detail=True, methods=['get'])
    def retrieve_artists(self, request, user__username=None):
        '''
        lists a user's artists based on the timestamps they were followed on
        '''
        try:
            userdata = self.get_userdata(user__username)

            artists = (userdata
                       .artist_library.all()
                       .order_by('-date_added'))

            # get serialized artist data
            serializer = ArtistLibrarySerializer(
                artists,
                many=True,
                context={'request': request}
            )
            artist_list = serializer.data
            # sort the list according to date added (newest first)
            artist_list.sort(
                key=lambda x: datetime.datetime.strptime(
                    x['date_added'],
                    '%Y-%m-%dT%H:%M:%S.%f%z'
                ),
                reverse=True
            )

            return Response(
                data={"artist_list": artist_list},
                status=status.HTTP_200_OK
            )
        except UserData.DoesNotExist:
            return Response(
                data={"artist_list": []},
                status=status.HTTP_204_NO_CONTENT
            )

    def retrieve(self, request, user__username=None):
        '''
        lists a user's library items, either albums or playlists or artists
        based on the timestamps they were liked on / followed on
        '''
        try:
            userdata = self.get_userdata(user__username)

            library_items = []

            artists = (userdata
                       .artist_library.all()
                       .order_by('-date_added'))
            albums = (userdata
                      .album_library.all()
                      .order_by('-date_added'))
            playlists = (userdata
                         .playlist_library .all()
                         .order_by('-date_added'))

            # get serialized artist data
            serializer = ArtistLibrarySerializer(
                artists,
                many=True,
                context={'request': request}
            )
            for item in serializer.data:
                library_items.append(item)

            # get serialized album data
            serializer = AlbumLibrarySerializer(
                albums,
                many=True,
                context={'request': request}
            )
            for item in serializer.data:
                library_items.append(item)

            # get serialized playlist data
            serializer = PlayistLibrarySerializer(
                playlists,
                many=True,
                context={'request': request}
            )
            for item in serializer.data:
                library_items.append(item)

            # sort the list according to date added (newest first)
            library_items.sort(
                key=lambda x: datetime.datetime.strptime(
                    x['date_added'],
                    '%Y-%m-%dT%H:%M:%S.%f%z'
                ),
                reverse=True
            )

            return Response(
                data={"library_items": library_items},
                status=status.HTTP_200_OK
            )
        except UserData.DoesNotExist:
            return Response(
                data={"library_items": []},
                status=status.HTTP_204_NO_CONTENT
            )

    def update(self, request, user__username=None):
        try:
            playlist_id = request.data['playlist_library']
            userdata = self.get_userdata(user__username)
            user = request.user
            new_playlist = get_object_or_404(Playlist, id=playlist_id)

            # create new model object to add to albums library
            try:
                new_object = UserPlaylistLibrary.objects.create(
                    user=user,
                    playlist=new_playlist
                )
                # continue adding to the list with updated timestamp
                userdata.playlist_library.add(new_object)
            except IntegrityError:
                duplicate_object = UserPlaylistLibrary.objects.filter(
                    user=user,
                    playlist=new_playlist
                ).first()
                # delete that object and create the new one
                userdata.playlist_library.remove(duplicate_object)
                duplicate_object.delete()
                new_object = UserPlaylistLibrary.objects.create(
                    user=user,
                    playlist=new_playlist
                )
                # continue adding to the list with updated timestamp
                userdata.playlist_library.add(new_object)

            # if added to library, then it needs to be in the liked list
            liked_list = userdata.liked_playlists.all()
            if new_playlist not in liked_list:
                userdata.liked_playlists.add(new_playlist)

            return Response(
                data={"status": "added to playlists library"},
                status=status.HTTP_200_OK
            )
        except KeyError:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowersViewSet(UserDataViewSet):
    """
    Read-only list of a user's followers (public).
    Followers are updated automatically when someone follows or unfollows
    through the following endpoint, so both sides always stay in sync.
    """
    serializer_class = FollowersSerializer
    public_read = True
    http_method_names = ['get', 'head', 'options']


class FollowingViewSet(UserDataViewSet):
    """
    ViewSet for viewing (public) and editing (own only) who a user follows.
    PUT {"following": "<username>"} toggles following that user.
    """
    serializer_class = FollowingSerializer
    public_read = True

    def update(self, request, user__username=None):
        """toggle following another user; updates both users' lists together"""
        if 'following' not in request.data:
            return Response(
                data={"status": "missing field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        userdata = self.get_userdata(user__username)
        target = get_object_or_404(User, username=request.data['following'])
        if target == user:
            return Response(
                data={"status": "you can't follow yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        target_userdata, _ = UserData.objects.get_or_create(user=target)

        # all-or-nothing: my "following" and their "followers" never disagree
        with transaction.atomic():
            if userdata.following.filter(pk=target.pk).exists():
                userdata.following.remove(target)
                target_userdata.followers.remove(user)
                # artists also live in the follower's library
                UserArtistLibrary.objects.filter(user=user, artist=target).delete()
                result = "removed from following"
            else:
                userdata.following.add(target)
                target_userdata.followers.add(user)
                if target.is_artist:
                    library_item, _ = UserArtistLibrary.objects.get_or_create(
                        user=user, artist=target)
                    userdata.artist_library.add(library_item)
                result = "added to following"

        return Response(data={"status": result}, status=status.HTTP_200_OK)


class RetrieveSearchResultsView(generics.RetrieveAPIView):
    '''class based view to allow list search results for 5 categories
        1. Songs
        2. artist
        3. album
        4. playlist
        5. profile // users that are not artists
    '''
    '''class based view to get user details for profile headers'''
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'keyword'

    def get(self, request, keyword=None):
        search_results = {
            "songs": [],
            "artists": [],
            "albums": [],
            "playlists": [],
            "profiles": [],
        }
        # each category is limited in SQL (LIMIT), not after serializing
        # every match in Python
        # get songs first
        queryset = Song.objects.filter(
            song_name__icontains=keyword,
        ).select_related('album__artist', 'album__genre')[:5]
        serializer = SongSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['songs'] = serializer.data

        # get artists
        queryset = User.objects.filter(
            profile_name__icontains=keyword,
            is_artist=True,
        )[:10]
        serializer = UserProfileDataSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['artists'] = serializer.data

        # get albums
        queryset = Album.objects.filter(
            album_name__icontains=keyword
        ).select_related('artist', 'genre').order_by('-album_publish_year')[:10]
        serializer = AlbumSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['albums'] = serializer.data

        # get playlists
        queryset = Playlist.objects.filter(
            playlist_name__icontains=keyword,
            is_private=False,
        ).order_by('-date_created')[:10]
        serializer = PlaylistSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['playlists'] = serializer.data

        # get user profiles
        queryset = User.objects.filter(
            profile_name__icontains=keyword,
            is_artist=False,
        )[:10]
        serializer = UserProfileDataSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['profiles'] = serializer.data

        return Response(
            data={'results': search_results},
            status=status.HTTP_200_OK
        )
