from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import ModelFormMixin

from courses.forms import CourseForm, ProposedCourseSelectionForm
from courses.models import Course, ProposedCourse, Enrollment
from profiles.models import StudentProfile, FacultyProfile



# Create your views here.
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'

    paginate_by = 10
    ordering = ['created_at']

    def get_queryset(self):
        profile = self.request.user.profile.get_real_instance()

        # If the user is a student
        if isinstance(profile, StudentProfile):
            return Course.objects.filter(enrollments__student=profile)

        # If the user is a faculty member
        if isinstance(profile, FacultyProfile):
            return Course.objects.filter(
                Q(faculty=profile) | Q(proposedcourse__faculty=profile)
            ).distinct().order_by('created_at')

        # Default case, return an empty queryset
        return Course.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = self.request.user.profile.get_real_instance()
        if isinstance(profile, FacultyProfile):
            proposed_courses = ProposedCourse.objects.filter(faculty=profile)
            context['proposed_courses'] = proposed_courses

        # Add the user type to the context
        if isinstance(profile, StudentProfile):
            context['user_type'] = 'student'
        elif isinstance(profile, FacultyProfile):
            context['user_type'] = 'faculty'
        else:
            context['user_type'] = 'guest'

        return context


class CourseFormSetMixin(ModelFormMixin):
    model = ProposedCourse
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    context_object_name = 'course'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # Handle POST request, form should be populated with data
            context['form'] = CourseForm(self.request.POST,
                                         instance=self.object if hasattr(self, 'object') else None)
        else:
            # Handle GET request, form will be empty or populated with existing instance
            context['form'] = CourseForm(instance=self.object if hasattr(self, 'object') else None)
        return context

    def form_valid(self, form):
        if isinstance(self.request.user.profile.get_real_instance(), FacultyProfile):
            form.instance.faculty = self.request.user.profile.get_real_instance()
        else:
            return redirect('course_list')

        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()
        return redirect(self.get_success_url())


class ProposedCourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CourseFormSetMixin, CreateView):
    def test_func(self):
        return isinstance(self.request.user.profile.get_real_instance(), FacultyProfile)


class ProposedCourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, CourseFormSetMixin, UpdateView):
    def test_func(self):
        proposed_course = self.get_object()
        return self.request.user.profile.get_real_instance() == proposed_course.faculty


class ProposeCourseEdit(LoginRequiredMixin, UserPassesTestMixin, CourseFormSetMixin, UpdateView):
    def test_func(self):
        faculty = self.request.user.profile.get_real_instance()
        course = Course.objects.filter(pk=self.kwargs['pk'], faculty=faculty).exists()
        return isinstance(faculty, FacultyProfile) and course

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['pk'])
        self.faculty = request.user.profile.get_real_instance()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        proposed, created = ProposedCourse.objects.get_or_create(
            course=self.course,
            faculty=self.faculty,
            defaults={
                'name': self.course.name,
                'credit': self.course.credit,
                'syllabus': self.course.syllabus,
            }
        )
        return proposed

    def form_valid(self, form):
        form.instance.faculty = self.faculty  # enforce correct faculty
        form.instance.course = self.course  # enforce course linkage
        return super().form_valid(form)

class ProposeCourseDelete(LoginRequiredMixin, UserPassesTestMixin, View):

    success_url = reverse_lazy('course_list')

    def test_func(self):
        return isinstance(self.request.user.profile.get_real_instance(), FacultyProfile)

    def dispatch(self, request, *args, **kwargs):
        # Set up course and faculty for use in get_object
        self.course = get_object_or_404(Course, pk=kwargs['pk'])
        self.faculty = request.user.profile.get_real_instance()

        if self.course.faculty != self.faculty:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        proposed, created = ProposedCourse.objects.get_or_create(
            course=self.course,
            faculty=self.faculty,
            defaults={
                'name': self.course.name,
                'credit': self.course.credit,
                'syllabus': self.course.syllabus,
            }
        )
        return proposed

    def get(self, request, *args, **kwargs):
        proposed = self.get_object()
        proposed.is_deleted = True
        proposed.save()
        return redirect(self.success_url)



class ApproveCourseView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'courses/approve_courses.html'
    form_class = ProposedCourseSelectionForm

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            accepted_courses = form.cleaned_data['courses_to_accept']
            rejected_courses = form.cleaned_data['courses_to_reject']

            for proposed_course in accepted_courses:
                if proposed_course.is_deleted:
                    if proposed_course.course:
                        proposed_course.course.delete()
                    proposed_course.delete()
                elif not proposed_course.course:
                    new_course = Course.objects.create(
                        name=proposed_course.name,
                        credit=proposed_course.credit,
                        faculty=proposed_course.faculty,
                        syllabus=proposed_course.syllabus,
                    )
                    new_course.prerequisites.clear()
                    new_course.prerequisites.add(*proposed_course.prerequisites.all())
                    new_course.save()

                    proposed_course.delete()
                else:
                    proposed_course.course.name = proposed_course.name
                    proposed_course.course.credit = proposed_course.credit
                    proposed_course.course.faculty = proposed_course.faculty
                    proposed_course.course.syllabus = proposed_course.syllabus
                    proposed_course.course.prerequisites.clear()
                    proposed_course.course.prerequisites.add(*proposed_course.prerequisites.all())
                    proposed_course.course.save()

                    proposed_course.delete()

            for proposed_course in rejected_courses:
                proposed_course.delete()

            return redirect(reverse('course_list'))

        return render(request, self.template_name, {'form': form})


class ProposedCourseDelete(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return type(self.request.user.profile.get_real_instance()) == FacultyProfile

    def dispatch(self, request, *args, **kwargs):
        self.proposed_course = get_object_or_404(ProposedCourse, pk=kwargs['pk'])
        self.faculty = request.user.profile.get_real_instance()

        if self.proposed_course.faculty != self.faculty:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.proposed_course.delete()
        return redirect(reverse('course_list'))

class CourseExploreView(LoginRequiredMixin, ListView):
    template_name = 'courses/explore.html'
    model = Course


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.profile.get_real_instance()
        search_query = self.request.GET.get('q')

        if isinstance(user, StudentProfile):
            base_queryset = Course.objects.exclude(enrollments__student=user)
        elif isinstance(user, FacultyProfile):
            base_queryset = Course.objects.exclude(faculty=user)
        else:
            base_queryset = Course.objects.none()

        if search_query:
            base_queryset = base_queryset.filter(name__icontains=search_query)

        context['courses'] = base_queryset
        context['user'] = user.__class__.__name__
        return context


class EnrollCourseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user.profile.get_real_instance()
        course = get_object_or_404(Course, pk=pk)

        if hasattr(user, 'studentprofile'):
            Enrollment.objects.get_or_create(course=course, student=user)
            messages.success(request, f"You've been enrolled in {course.name}!")
        else:
            messages.error(request, "Only students can enroll in courses.")

        return redirect('course_explore')