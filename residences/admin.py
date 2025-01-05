from django.contrib import admin
from .models import CustomUser, Residence, Image, Video

admin.site.register(CustomUser)
admin.site.register(Residence)
admin.site.register(Image)
admin.site.register(Video)
