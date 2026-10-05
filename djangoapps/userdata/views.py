import datetime
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import IntegrityError
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


class LikedAlbumsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing like_albums
    POST: Add to liked_albums, remove from liked_albums
    GET: View if an album was liked by a user
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = LikedAlbumsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def update(self, request, user__username=None):
        try:
            album_id = request.data['liked_albums']
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()
            new_album = Album.objects.filter(id=album_id).first()

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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            # TO DO: fix this, this doesn't work the way I expected it to
            return self.create(request=request)


class LikedSongsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing liked_songs
    Add to liked_songs, remove from liked_songs
    View if a song was liked by a user
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = LikedSongsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def update(self, request, user__username=None):
        try:
            song_id = request.data['liked_songs']
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            new_song = Song.objects.filter(id=song_id).first()

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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class LikedPlaylistsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing liked_playlists
    Add to liked_playlists, remove from liked_playlists
    View if a playlist was liked by a user
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = LikedPlaylistsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def update(self, request, user__username=None):
        try:
            playlist_id = request.data['liked_playlists']
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()
            new_playlist = Playlist.objects.filter(id=playlist_id).first()

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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class RecentlyPlayedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing recently played albums / playlists
    Add to recently played, remove from recently played
    Storing maximum of the 6 most recent records each
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = RecentlyPlayedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def retrieve(self, request, user__username=None):
        '''
        lists a user's top 6 recently played items, either albums or playlists
        based on their timestamps
        '''
        try:
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()

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
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()

            try:
                album_id = request.data['recently_played_albums']
            except KeyError:
                album_id = None

            # for albums
            if album_id:
                recent_album = Album.objects.filter(id=album_id).first()
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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)

    @action(detail=True, methods=['put'])
    def update_playlists(self, request, user__username=None):
        '''
        performs list updates for recently_played_playlists and saves only the
        six most recent records for this many-to-many field
        '''
        try:
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()

            try:
                playlist_id = request.data['recently_played_playlists']
            except KeyError:
                playlist_id = None

            # for playlists
            if playlist_id:
                recent_playlist = Playlist.objects.filter(
                    id=playlist_id
                ).first()
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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class UserLibraryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user library items
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = UserLibrarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    @action(detail=True, methods=['get'])
    def retrieve_artists(self, request, user__username=None):
        '''
        lists a user's artists based on the timestamps they were followed on
        '''
        try:
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()

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
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()

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
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()
            new_playlist = Playlist.objects.filter(id=playlist_id).first()

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
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class FollowersViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing followers for a user
    Add to followers, remove from followers using their username
    List a users followers
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = FollowersSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def update(self, request, user__username=None):
        ''' takes the username of the follower and adds or removes them from
        the user's list of followers depending on if the follower is already
        present in the list '''
        try:
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            follower_username = request.data['followers']
            new_follower = User.objects.filter(
                username=follower_username
            ).first()

            follower_list = userdata.followers.all()
            if new_follower in follower_list:
                userdata.followers.remove(new_follower)
                return Response(
                    data={"status": "removed from followers"},
                    status=status.HTTP_200_OK
                )
            else:
                userdata.followers.add(new_follower)
                return Response(
                    data={"status": "added to followers"},
                    status=status.HTTP_200_OK
                )
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class FollowingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing following for a user
    Add to following, remove from following
    List a users following
    """
    queryset = UserData.objects.prefetch_related('user')
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def update(self, request, user__username=None):
        ''' takes the username of the user to follow and adds or removes them
        from the user's list of followed users depending on if the followed
        user is already present in the list '''
        try:
            following_username = request.data['following']
            userdata = UserData.objects.filter(
                user__username=user__username
            ).first()
            new_following = User.objects.filter(
                username=following_username
            ).first()
            user = User.objects.filter(
                username=user__username
            ).first()

            following_list = userdata.following.all()
            if new_following in following_list:
                userdata.following.remove(new_following)
                # only remove from artist library if the user is an artist
                if new_following.is_artist:
                    duplicate_object = UserArtistLibrary.objects.filter(
                        user=user,
                        artist=new_following,
                    ).first()
                    userdata.artist_library.remove(duplicate_object)
                    duplicate_object.delete()
                return Response(
                    data={"status": "removed from following"},
                    status=status.HTTP_200_OK
                )
            else:
                userdata.following.add(new_following)
                # only add to artist library if the user is an artist
                if new_following.is_artist:
                    new_object = UserArtistLibrary.objects.create(
                        user=user,
                        artist=new_following,
                    )
                    userdata.artist_library.add(new_object)
                return Response(
                    data={"status": "added to following"},
                    status=status.HTTP_200_OK
                )
        except UserData.DoesNotExist:
            # if userdata object does not exist, create it
            return self.create(request=request)


class RetrieveSearchResultsView(generics.RetrieveAPIView):
    '''class based view to allow list search results for 5 categories
        1. Songs
        2. artist
        3. album
        4. playlist
        5. profile // users that are not artists
    '''
    '''class based view to get user details for profile headers'''
    queryset = UserData.objects.prefetch_related('user')
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
        # get songs first
        queryset = Song.objects.filter(
            song_name__icontains=keyword,
        )
        serializer = SongSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['songs'] = serializer.data[0:5]

        # get artists
        queryset = User.objects.filter(
            profile_name__icontains=keyword,
            is_artist=True,
        )
        serializer = UserProfileDataSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['artists'] = serializer.data[0:10]

        # get albums
        queryset = Album.objects.filter(
            album_name__icontains=keyword
        ).order_by('-album_publish_year')
        serializer = AlbumSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['albums'] = serializer.data[0:10]

        # get playlists
        queryset = Playlist.objects.filter(
            playlist_name__icontains=keyword,
            is_private=False,
        ).order_by('-date_created')
        serializer = PlaylistSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['playlists'] = serializer.data[0:10]

        # get user profiles
        queryset = User.objects.filter(
            profile_name__icontains=keyword,
            is_artist=False,
        )
        serializer = UserProfileDataSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        search_results['profiles'] = serializer.data[0:10]

        return Response(
            data={'results': search_results},
            status=status.HTTP_200_OK
        )
