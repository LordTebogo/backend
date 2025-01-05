from rest_framework import serializers
from .models import CustomUser, Residence, Image, Video

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'profile_image', 'password', 'reference_number',
                'is_images_subscribed', 'is_videos_subscribed', 'is_on_premium'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video']

class ResidenceSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Residence
        fields = [
            'id', 'user', 'name', 'address', 'residence_type', 'room_price', 'rooms_include', 'description',
            'cover_image', 'rooms_available', 'number_of_rooms_available', 'room_available_date', 'last_updated',
            'business_contacts', 'business_email', 'images', 'videos'
        ]
