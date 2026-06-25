import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    meta = models.JSONField(default=dict)
    format = models.JSONField(default=dict)
    margins = models.JSONField(default=dict)
    numbering = models.JSONField(default=dict)
    typography = models.JSONField(default=dict)
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} ({self.owner})'
