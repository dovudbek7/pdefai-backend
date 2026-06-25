from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name',
            'meta', 'format', 'margins', 'numbering', 'typography', 'content',
            'createdAt', 'updatedAt',
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']

    def get_createdAt(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    def get_updatedAt(self, obj):
        return int(obj.updated_at.timestamp() * 1000)
