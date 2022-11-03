from django.urls import path, include
from .views import (
    DocListApiView,
    DocDetailApiView,
    EntityListApiView,
    ProjectListApiView,
    ProjectDetailApiView,
    ExtractionListApiView,
    EntityListApiView,
    EntityFoundListApiView
)

urlpatterns = [
    path('project/', ProjectListApiView.as_view()),
    path('project/<int:project_id>', ProjectDetailApiView.as_view()),
    path('project/<int:project_id>/docs', DocListApiView.as_view()),
    path('project/<int:project_id>/extractions', ExtractionListApiView.as_view()),
    path('project/<int:project_id>/entities/<int:extraction_id>', EntityListApiView.as_view()),
    path('doc/<int:doc_id>', DocDetailApiView.as_view()),
    path('doc/<int:doc_id>/extractions', ExtractionListApiView.as_view()),
    path('doc/<int:doc_id>/entities', EntityFoundListApiView.as_view()),
    path('entity/<int:entity_id>', EntityFoundListApiView.as_view()),
    path('entity/delete', EntityListApiView.as_view()),
]