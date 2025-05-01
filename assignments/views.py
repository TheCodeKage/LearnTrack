from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from courses.models import Course
from .forms import AssignmentForm
from .models import Assignment, Submission


# Create your views here.
class AssignmentCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Course, pk=self.kwargs['pk']).faculty

    def get_success_url(self):
        return reverse('assignment-list')

    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/create.html'

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return super().form_valid(form)


class AssignmentUpdateView(UserPassesTestMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/create.html'

    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Assignment, pk=self.kwargs['pk']).course.faculty

    def get_success_url(self):
        return reverse('assignment-list')


class AssignmentDeleteView(UserPassesTestMixin, DeleteView):
    model = Assignment

    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Assignment, pk=self.kwargs['pk']).course.faculty

    def get_success_url(self):
        return reverse('assignment-list')


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    context_object_name = 'assignments'
    template_name = 'assignments/list.html'
    paginate_by = 5

    def get_queryset(self):
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return Assignment.objects.filter(course=self.course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile.get_real_instance()
        context['user_type'] =user_profile.__class__.__name__

        # If student, pass a map of assignment id to their submission (or None)
        if context['user_type'] == 'StudentProfile':
            submission_map = {}
            for assignment in context['assignments']:
                submission = assignment.submission_set.filter(student=user_profile).first()
                submission_map[assignment.id] = submission
            context['submission_map'] = submission_map

        return context



class SubmissionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        student = request.user.profile.get_real_instance()

        # Check if already submitted
        if Submission.objects.filter(assignment=assignment, student=student).exists():
            messages.warning(request, "You have already submitted a solution for this assignment.")
            return redirect('assignment-list', pk=assignment.course.pk)

        # Check if a file is uploaded
        if 'solution' not in request.FILES:
            messages.error(request, "Please upload a PDF file to submit.")
            return redirect('assignment-list', pk=assignment.course.pk)

        # Save the submission
        Submission.objects.create(
            student=student,
            assignment=assignment,
            solution=request.FILES['solution'],
        )

        messages.success(request, "Submission successful!")
        return redirect('assignment-list', pk=assignment.course.pk)


class SubmissionListView(UserPassesTestMixin, ListView):
    model = Submission
    context_object_name = 'submissions'

    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Assignment, pk=self.kwargs['pk']).course.faculty

    def get_queryset(self):
        return Submission.objects.filter(assignment=get_object_or_404(Assignment, pk=self.kwargs['pk']))


class SubmissionGradeView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Assignment, pk=self.kwargs['pk']).course.faculty

    def post(self, request, *args, **kwargs):
        if request.POST.get('grade'):
            get_object_or_404(Submission, pk=self.kwargs['pk']).grade = request.POST.get('grade')
            return redirect('')
