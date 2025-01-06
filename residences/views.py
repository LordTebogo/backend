from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Residence, Image, Video
from .serializers import CustomUserSerializer, ResidenceSerializer, ImageSerializer, VideoSerializer
import logging
from django.http import StreamingHttpResponse, HttpResponse
import os

logger = logging.getLogger(__name__)

MAX_LIMITS = {
    'premium': {'residences': 5, 'images': 6, 'videos': 3},
    'videos_subscribed': {'residences': 2, 'images': 6, 'videos': 1},
    'images_subscribed': {'residences': 1, 'images': 6, 'videos': 0},
    'freemium': {'residences': 1, 'images': 3, 'videos': 0}
}

def handle_images(residence, images):
    Image.objects.filter(residence=residence).delete()
    for image in images:
        Image.objects.create(residence=residence, image=image)

def handle_videos(residence, videos):
    Video.objects.filter(residence=residence).delete()
    for video in videos:
        Video.objects.create(residence=residence, video=video)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class ResidenceViewSet(viewsets.ModelViewSet):
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.dict()

        if 'cover_image' not in request.FILES:
            data['cover_image'] = instance.cover_image

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')

        if images:
            handle_images(instance, images)
        if videos:
            handle_videos(instance, videos)

        return Response(serializer.data)

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    logout(request)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_residence_form(request):
    user = request.user
    user_residences_count = Residence.objects.filter(user=user).count()

    if user.is_on_premium:
        subscription = 'premium'
    elif user.is_videos_subscribed:
        subscription = 'videos_subscribed'
    elif user.is_images_subscribed:
        subscription = 'images_subscribed'
    else:
        subscription = 'freemium'

    max_residences = MAX_LIMITS[subscription]['residences']
    max_images = MAX_LIMITS[subscription]['images']
    max_videos = MAX_LIMITS[subscription]['videos']

    if user_residences_count >= max_residences:
        return Response({'message': f'You have reached the maximum limit of {max_residences} residences.'}, status=status.HTTP_400_BAD_REQUEST)

    images = request.FILES.getlist('images')
    videos = request.FILES.getlist('videos')

    if len(images) > max_images:
        return Response({'message': f'You can upload up to {max_images} images only.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(videos) > max_videos:
        return Response({'message': f'You cannot upload videos with your current subscription.'}, status=status.HTTP_400_BAD_REQUEST)

    for video in videos:
        if video.size > 250 * 1024 * 1024:  # 250 MB limit
            return Response({'message': 'Each video must not exceed 250 MB in size.'}, status=status.HTTP_400_BAD_REQUEST)
        # Placeholder for video duration check (if needed)

    serializer = ResidenceSerializer(data=request.data)
    if serializer.is_valid():
        residence = serializer.save()
        handle_images(residence, images)
        handle_videos(residence, videos)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'errors': serializer.errors, 'message': 'Validation failed. Check the provided data.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def stream_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        video_path = video.video.path

        if not os.path.exists(video_path):
            return HttpResponse(status=404)

        def video_stream():
            try:
                with open(video_path, 'rb') as f:
                    while chunk := f.read(8192):  # Read in 8KB chunks
                        yield chunk
            except IOError as e:
                logger.error(f"IOError while streaming video: {e}")
                yield b''

        response = StreamingHttpResponse(video_stream(), content_type="video/mp4")
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(video_path)}"'
        return response
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
