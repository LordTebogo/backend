from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CustomUserViewSet, ResidenceViewSet, ImageViewSet, VideoViewSet, register, login_view, logout_view, get_user_details, stream_video, submit_residence_form

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'residences', ResidenceViewSet)
router.register(r'images', ImageViewSet)
router.register(r'videos', VideoViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/me/', get_user_details, name='get_user_details'),
    path('submit-residence/', submit_residence_form, name='submit_residence_form'),
    path('stream_video/<uuid:video_id>/', stream_video, name='stream_video'),
]
