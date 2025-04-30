from django.core.validators import FileExtensionValidator
from django.db import models

from profiles.models import FacultyProfile, StudentProfile


# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100)
    credit = models.IntegerField(default=1)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='courses')
    syllabus = models.FileField(upload_to='syllabus/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])


class ProposedCourse(models.Model):
    name = models.CharField(max_length=100)
    credit = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    prerequisites = models.ManyToManyField(Course, blank=True, related_name='proposed_dependent_courses')
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='proposed_courses')
    syllabus = models.FileField(upload_to='syllabus/', validators=[FileExtensionValidator(['pdf'])])
    course = models.OneToOneField(Course, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    GRADE_CHOICES = [
        ('O', 'Outstanding'),
        ('A+', 'Excellent'),
        ('A', 'Very Good'),
        ('B+', 'Good'),
        ('B', 'Average'),
        ('C', 'Below Average'),
        ('D', 'Pass'),
        ('F', 'Fail'),
    ]
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('course', 'student')


class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='course_feedback')
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    ratings = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(blank=True, null=True)
