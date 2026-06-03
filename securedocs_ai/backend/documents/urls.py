"""
Documents App — URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # POST /api/documents/upload/ → upload + process document
    path('documents/upload/', views.DocumentUploadView.as_view(), name='document-upload'),

    # GET /api/documents/ → list all documents
    path('documents/', views.DocumentListView.as_view(), name='document-list'),

    # DELETE /api/documents/{id}/ → delete document
    path('documents/<int:doc_id>/', views.DocumentDeleteView.as_view(), name='document-delete'),
]
