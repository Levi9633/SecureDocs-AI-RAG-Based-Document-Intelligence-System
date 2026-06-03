"""
SecureDocs AI — Root URL Configuration
All API routes registered here
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Chat endpoints: /api/chats/
    path('api/', include('chats.urls')),

    # Document endpoints: /api/documents/
    path('api/', include('documents.urls')),

    # RAG chat endpoint: /api/chat/
    path('api/', include('rag.urls')),
]

# Serve uploaded media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
