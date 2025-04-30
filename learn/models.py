from django.core.validators import FileExtensionValidator
from django.db import models
from courses.models import Course
from profiles.models import StudentProfile


# Create your models here.
class StudyMaterial(models.Model):
    name = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    created = models.DateTimeField(auto_now_add=True)

class PDFMaterial(StudyMaterial):
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

class URLMaterial(StudyMaterial):
    url = models.URLField()

class Lecture(StudyMaterial):
    content = models.TextField(blank=True, null=True)

class Feedback(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='material_feedback')
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    ratings = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(blank=True, null=True)
