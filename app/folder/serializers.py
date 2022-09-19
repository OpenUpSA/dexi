from rest_framework import serializers
from .models import Folder
class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name", "user", "created_at"]