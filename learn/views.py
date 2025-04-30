from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from courses.models import Course
from .forms import URLMaterialForm, PDFMaterialForm, LectureForm, StudyMaterialForm
from .models import URLMaterial, PDFMaterial, Lecture, StudyMaterial


class CheckFacultyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profile.get_real_instance() == self.get_object().course.faculty


class StudyMaterialCreateView(UserPassesTestMixin, View):
    template_name = 'learn/upload.html'
    form_class = StudyMaterialForm

    def get_success_url(self):
        return reverse('materials', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Course, pk=self.kwargs['pk']).faculty

    def get(self, request, *args, **kwargs):
        form = StudyMaterialForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        if file := request.POST.get('file'):
            PDFMaterial.objects.create(
                name=name,
                file=file,
                course=get_object_or_404(Course, pk=self.kwargs['pk'])
            )
        elif url := request.POST.get('url'):
            URLMaterial.objects.create(
                name=name,
                url=url,
                course=get_object_or_404(Course, pk=self.kwargs['pk'])
            )
        else:
            return self.get(request, *args, **kwargs)

        return redirect(self.get_success_url())


class URLMaterialUpdateView(CheckFacultyMixin, UpdateView):
    success_url = reverse_lazy('learn')
    model = URLMaterial
    template_name = 'learn/url_upload.html'
    form_class = URLMaterialForm


class LectureCreateView(UserPassesTestMixin, CreateView):
    success_url = reverse_lazy('learn')
    model = Lecture
    template_name = 'learn/lecture_upload.html'
    form_class = LectureForm

    def test_func(self):
        return self.request.user.profile.get_real_instance() == get_object_or_404(Course, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return super().form_valid(form)


class LectureUpdateView(CheckFacultyMixin, UpdateView):
    success_url = reverse_lazy('learn')
    model = Lecture
    template_name = 'learn/lecture_upload.html'
    form_class = LectureForm


class PDFMaterialUpdateView(CheckFacultyMixin, UpdateView):
    success_url = reverse_lazy('learn')
    model = PDFMaterial
    template_name = 'learn/pdf_upload.html'
    form_class = PDFMaterialForm


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course

    def get_template_names(self):
        user = self.request.user.profile.get_real_instance()
        course = self.get_object()
        if user in course.enrollments.all() or course.faculty == user:
            return ['learn/course_detail.html']
        else:
            return ['learn/course_enroll.html']

    context_object_name = 'course'
    paginate_by = 9


class StudyMaterialListView(LoginRequiredMixin, ListView):
    template_name = 'learn/material_list.html'
    model = StudyMaterial
    context_object_name = 'materials'
    ordering = ['-created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['real_user'] = self.request.user.profile.get_real_instance()
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        return get_object_or_404(Course, pk=self.kwargs['pk']).materials.all()




class LectureListView(LoginRequiredMixin, ListView):
    model = Lecture
    template_name = 'learn/lecture_list.html'
    context_object_name = 'lectures'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user.profile.get_real_instance()
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'])
        print(context['user'], context['course'].faculty)
