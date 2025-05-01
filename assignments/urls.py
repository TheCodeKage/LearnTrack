from django.urls import path
from .views import *

urlpatterns = [
    path('<int:pk>/create/', AssignmentCreateView.as_view(), name='assignment-create'),
    path('<int:pk>/update/', AssignmentUpdateView.as_view(), name='assignment-update'),
    path('<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('<int:pk>/', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('<int:pk>/submit/', SubmissionView.as_view(), name='submission-view'),
    path('<int:pk>/grade/', SubmissionGradeView.as_view(), name='submission-grade'),
]