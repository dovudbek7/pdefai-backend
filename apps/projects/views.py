from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Project
from .serializers import ProjectSerializer


@extend_schema_view(
    list=extend_schema(summary='Barcha loyihalar', tags=['Projects']),
    create=extend_schema(summary='Yangi loyiha', tags=['Projects']),
    retrieve=extend_schema(summary='Bitta loyiha', tags=['Projects']),
    partial_update=extend_schema(summary='Loyihani yangilash (PATCH)', tags=['Projects']),
    destroy=extend_schema(summary='Loyihani o\'chirish', tags=['Projects']),
)
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
