from django.urls import path, include
from . import views

urlpatterns = [
    path('list/', views.CourseListView.as_view(), name='course_list'),
    path('explore/', views.CourseExploreView.as_view(), name='course_explore'),
    path('enroll/<int:pk>/', views.EnrollCourseView.as_view(), name='course_enroll'),
    path('create/', views.ProposedCourseCreateView.as_view(), name='course_create'),
    path('update_proposal/<int:pk>/', views.ProposedCourseUpdateView.as_view(), name='proposed_course_update'),
    path('approve/', views.ApproveCourseView.as_view(), name='course_approve'),
    path('update/<int:pk>/', views.ProposeCourseEdit.as_view(), name='course_edit'),
    path('delete/<int:pk>/', views.ProposeCourseDelete.as_view(), name='course_delete'),
    path('proposed_delete/<int:pk>/', views.ProposedCourseDelete.as_view(), name='proposed_course_delete'),
    path('detail/', include('learn.urls')),
    path('assignments/', include('assignments.urls')),
]