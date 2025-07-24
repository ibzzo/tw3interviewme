from django.db import models
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """Model to store conversation sessions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Message(models.Model):
    """Model to store individual messages in a conversation."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    # Optional fields for search results
    search_results = models.JSONField(null=True, blank=True)
    sources = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SearchCache(models.Model):
    """Model to cache search results to avoid redundant searches."""
    query = models.CharField(max_length=500, unique=True)
    results = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self, hours=24):
        """Check if cache entry is older than specified hours."""
        age = timezone.now() - self.created_at
        return age.total_seconds() > hours * 3600
    
    def __str__(self):
        return f"Search: {self.query[:50]}..."
