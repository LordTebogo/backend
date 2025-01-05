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
            Image.objects.filter(residence=instance).delete()
            for image in images:
                Image.objects.create(residence=instance, image=image)
        else:
            images = Image.objects.filter(residence=instance)
            for image in images:
                Image.objects.create(residence=instance, image=image.image)

        if videos:
            Video.objects.filter(residence=instance).delete()
            for video in videos:
                Video.objects.create(residence=instance, video=video)
        else:
            videos = Video.objects.filter(residence=instance)
            for video in videos:
                Video.objects.create(residence=instance, video=video.video)

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
        max_residences = 5
    elif user.is_videos_subscribed:
        max_residences = 2
    else:
        max_residences = 1

    if user_residences_count >= max_residences:
        return Response({
            'message': f'You have reached the maximum limit of {max_residences} residences.'
        }, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    images = request.FILES.getlist('images')
    videos = request.FILES.getlist('videos')

    logger.debug(f"Received data: {data}")
    logger.debug(f"Received images: {images}")
    logger.debug(f"Received videos: {videos}")

    serializer = ResidenceSerializer(data=data)
    if serializer.is_valid():
        residence = serializer.save()
        for image in images:
            Image.objects.create(residence_id=residence.id, image=image)
        for video in videos:
            Video.objects.create(residence=residence, video=video)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        logger.error(f"Validation errors: {serializer.errors}")
        return Response({
            'errors': serializer.errors,
            'message': 'Validation failed. Check the provided data.'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def stream_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        video_path = video.video.path

        if not os.path.exists(video_path):
            return HttpResponse(status=404)

        def video_stream():
            with open(video_path, 'rb') as f:
                while chunk := f.read(8192):  # Read in 8KB chunks
                    yield chunk

        response = StreamingHttpResponse(video_stream(), content_type="video/mp4")
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(video_path)}"'
        return response
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
