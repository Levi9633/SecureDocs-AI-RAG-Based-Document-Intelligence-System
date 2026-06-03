"""
Documents App Models
- Document: metadata for an uploaded file (id, filename, filepath, upload_date)
  NOTE: Embeddings are stored in FAISS, NOT here. This table only stores metadata.
"""

from django.db import models


class Document(models.Model):
    """Stores metadata for uploaded documents. Actual embeddings live in FAISS."""
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.filename
