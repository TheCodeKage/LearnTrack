from django.core.validators import FileExtensionValidator
from django.db import models

from courses.models import Course
from profiles.models import StudentProfile


# Create your models here.
class Assignment(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.FileField(upload_to='assignments/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def __str__(self):
        return f'{self.name} - {self.course}'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    solution = models.FileField(upload_to='submissions/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
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

    def __str__(self):
        return f'{self.assignment} - {self.student} - {self.grade}'

