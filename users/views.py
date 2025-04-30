from io import TextIOWrapper

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import redis

from profiles.models import StudentProfile, FacultyProfile
from .forms import RegisterForm
import csv

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_progress(request):
    progress = r.get(f'register_progress:{request.session.session_key}')
    return JsonResponse({'progress': progress or 0})

def register(request):

    def parse_csv(file):
        file.seek(0)
        wrapper = TextIOWrapper(file, encoding='utf-8')
        reader = csv.reader(wrapper)
        rows = list(reader)
        print(f"Parsed {len(rows)} rows from {file.name}")
        return rows[1:]

    @transaction.atomic
    def create_users(data, student=False):
        print("Creating users")
        successful = 0
        existing_usernames = set(
            User.objects.filter(username__in=[i[0] for i in data]).values_list('username', flat=True))
        total = len(data)
        for i in data:
            if len(i) < (6 if student else 5):
                print(i)
                continue
            if not i[0] in existing_usernames:
                print('right username')
                user = User(username=i[0], email=i[1], password=make_password(i[2]))
                if student:
                    profile = StudentProfile(user=user, name=i[3], phone_number=i[4], roll_no=i[5])
                else:
                    profile = FacultyProfile(user=user, name=i[3], phone_number=i[4])
                user.save()
                profile.save()
                successful += 1
            else:
                print('wrong username')
            r.set(f'register_progress:{request.session.session_key}', successful / total * 100)

        return successful

    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            student_details = form.cleaned_data['student_details']
            teacher_details = form.cleaned_data['teacher_details']
            created_users = 0
            r.set(f'register_progress:{request.session.session_key}', 0)

            if student_details:
                print("Hello")
                if not student_details.name.endswith('.csv'):
                    form.add_error('student_details', 'File is not a CSV.')
                    return render(request, 'users/upload.html', {'form': form})
                created_users += create_users(parse_csv(student_details), True)

            if teacher_details:
                if not teacher_details.name.endswith('.csv'):
                    form.add_error('teacher_details', 'File is not a CSV.')
                    return render(request, 'users/upload.html', {'form': form})
                created_users += create_users(parse_csv(teacher_details))

            request.session['message'] = f'{created_users} user(s) created successfully!'
            return HttpResponseRedirect(reverse('register'))
    else:
        form = RegisterForm()
        message = request.session.pop('message', None)
    return render(request, 'users/upload.html', {'form': form, 'message': message})
