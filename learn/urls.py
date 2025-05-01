from django.urls import path
from .views import *

urlpatterns = [
    path('<int:pk>/upload/', StudyMaterialCreateView.as_view(), name='upload'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/upload-lecture/', LectureCreateView.as_view(), name='upload-lecture'),
    path('<int:pk>/Lectures/', LectureListView.as_view(), name='lectures'),
    path('<int:pk>/urlmaterial/', StudyMaterialListView.as_view(), name='materials'),
    path('update/url-material/<int:pk>/', URLMaterialUpdateView.as_view(), name='update-url-material'),
    path('update/lecture/<int:pk>/', LectureUpdateView.as_view(), name='update-lecture'),
    path('update/pdf-material/<int:pk>/', PDFMaterialUpdateView.as_view(), name='pdf-update'),
]