from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from djangoapps.users.views import (
    SignupView,
    EmailTokenObtainPairView,
    UpdateProfileView,
    UpdateUserPermissionsView,
    UserProfileView
)


urlpatterns = [
    # login is actually the obtain token pair view
    path('login/', EmailTokenObtainPairView.as_view(),
         name='login'),
    path('signup/', SignupView.as_view(),
         name='signup'),
    path('token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('update_profile/<str:username>/', UpdateProfileView.as_view(),
         name='auth_update_profile'),
    path('update_permission/<str:username>/',
         UpdateUserPermissionsView.as_view(),
         name='auth_update_profile'),
    path('user_profile/<str:username>/',
         UserProfileView.as_view(),
         name='usere_profile'),
]
