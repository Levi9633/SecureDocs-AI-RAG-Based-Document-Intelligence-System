"""
Documents App Serializers
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'filename', 'filepath', 'upload_date']
        read_only_fields = ['id', 'upload_date']
