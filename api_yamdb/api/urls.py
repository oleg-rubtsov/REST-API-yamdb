from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import (APIGetToken, APISignup, CategoryViewSet, CommentsViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet, UsersViewSet,)

router_v1 = SimpleRouter()

app_name = 'api'

router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')
router_v1.register(r'users',
                   UsersViewSet, basename='users')

router_v1.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    'genres',
    GenreViewSet,
    basename='genres'
)

urlpatterns = [
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    path('v1/', include(router_v1.urls)),
    path('v1/api-token-auth/', views.obtain_auth_token, name='auth_token'),
    path('v1/auth/signup/', APISignup.as_view(), name='signup')
]
