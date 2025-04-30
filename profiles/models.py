from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=30)
    phone_number = PhoneNumberField(region='IN')

    def get_real_instance(self):
        for subclass in (StudentProfile, FacultyProfile):
            try:
                return getattr(self, subclass.__name__.lower())
            except subclass.DoesNotExist:
                continue
        return self

class StudentProfile(BaseProfile):
    roll_no = models.IntegerField(validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)], primary_key=True)

class FacultyProfile(BaseProfile):
    pass


    