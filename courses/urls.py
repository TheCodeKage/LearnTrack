from django.urls import path

from learn.views import CourseDetailView, LectureCreateView, LectureListView, StudyMaterialCreateView, \
    StudyMaterialListView, URLMaterialUpdateView, LectureUpdateView, PDFMaterialUpdateView
from . import views

urlpatterns = [
    path('list/', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.ProposedCourseCreateView.as_view(), name='course_create'),
    path('update_proposal/<int:pk>/', views.ProposedCourseUpdateView.as_view(), name='proposed_course_update'),
    path('approve/', views.ApproveCourseView.as_view(), name='course_approve'),
    path('update/<int:pk>/', views.ProposeCourseEdit.as_view(), name='course_edit'),
    path('delete/<int:pk>/', views.ProposeCourseDelete.as_view(), name='course_delete'),
    path('proposed_delete/<int:pk>/', views.ProposedCourseDelete.as_view(), name='proposed_course_delete'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/upload/', StudyMaterialCreateView.as_view(), name='upload'),
    path('<int:pk>/upload-lecture/', LectureCreateView.as_view(), name='upload-lecture'),
    path('<int:pk>/Lectures/', LectureListView.as_view(), name='lectures'),
    path('<int:pk>/urlmaterial/', StudyMaterialListView.as_view(), name='materials'),
    path('update/url-material/<int:pk>/', URLMaterialUpdateView.as_view(), name='update-url-material'),
    path('update/lecture/<int:pk>/', LectureUpdateView.as_view(), name='update-lecture'),
    path('update/pdf-material/<int:pk>/', PDFMaterialUpdateView.as_view(), name='pdf-update'),
]