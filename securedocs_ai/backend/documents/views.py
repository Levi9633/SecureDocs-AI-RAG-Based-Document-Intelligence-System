"""
Documents App — Views (API Endpoints)

Endpoints per spec:
  POST   /api/documents/upload/  → Upload + process document
  GET    /api/documents/         → List all documents
  DELETE /api/documents/{id}/    → Delete document + remove from FAISS

Error handling per spec:
  - Invalid file type
  - Empty file
  - Corrupted file
"""

import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document
from .serializers import DocumentSerializer
from .services import validate_file, process_document, remove_document_from_index


class DocumentUploadView(APIView):
    """
    POST /api/documents/upload/
    Upload pipeline: Save → Extract → Clean → Chunk → Embed → FAISS → SQLite
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {'error': 'No file provided. Please upload a PDF, DOCX, or TXT file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type and content
        try:
            validate_file(file)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save file to disk
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents')
        os.makedirs(upload_dir, exist_ok=True)

        safe_filename = file.name.replace(' ', '_')
        filepath = os.path.join(upload_dir, safe_filename)

        with open(filepath, 'wb') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # Save metadata to SQLite
        doc = Document.objects.create(
            filename=safe_filename,
            filepath=filepath,
        )

        # Process document (extract → chunk → embed → FAISS)
        try:
            result = process_document(doc)
        except ValueError as e:
            # Clean up failed upload
            doc.delete()
            if os.path.exists(filepath):
                os.remove(filepath)
            return Response({'error': str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            doc.delete()
            if os.path.exists(filepath):
                os.remove(filepath)
            return Response(
                {'error': f'Document processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = DocumentSerializer(doc)
        return Response({
            **serializer.data,
            'chunks_created': result.get('chunks', 0),
            'message': f'Document "{safe_filename}" uploaded and indexed successfully.',
        }, status=status.HTTP_201_CREATED)


class DocumentListView(APIView):
    """
    GET /api/documents/ → List all uploaded documents for the sidebar
    """

    def get(self, request):
        documents = Document.objects.all().order_by('-upload_date')
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentDeleteView(APIView):
    """
    DELETE /api/documents/{id}/ → Remove document from SQLite + FAISS
    """

    def delete(self, request, doc_id):
        try:
            doc = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            return Response(
                {'error': f'Document {doc_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        filename = doc.filename
        filepath = doc.filepath

        # Remove vectors from FAISS
        try:
            remove_document_from_index(filename)
        except Exception as e:
            # Log but don't fail — still delete from DB
            print(f"Warning: Could not remove from FAISS index: {e}")

        # Delete physical file
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete from SQLite
        doc.delete()

        return Response({
            'message': f'Document "{filename}" deleted successfully.'
        }, status=status.HTTP_200_OK)
