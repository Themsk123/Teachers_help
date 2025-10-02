from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_url = models.URLField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.youtube_url}"

class UploadedFile(models.Model):
    file = models.FileField(upload_to='user_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)