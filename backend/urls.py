from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings

from djangoapps.users.permissions import is_demo_account

# The public demo logins never get Django admin access, even though the seeded
# "minahil" account is a superuser.
_admin_has_permission = admin.site.has_permission
admin.site.has_permission = (
    lambda request: _admin_has_permission(request) and not is_demo_account(request.user))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('djangoapps.users.urls')),
    path('api/token/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('api/', include('djangoapps.songs.urls')),
    path('api/', include('djangoapps.playlists.urls')),
    path('api/userdata/', include('djangoapps.userdata.urls')),
]

# In production, media is served straight from Cloudinary's CDN.
if not settings.CLOUDINARY_URL:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
