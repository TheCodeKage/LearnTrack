from django import forms

from courses.models import Course, ProposedCourse


class CourseForm(forms.ModelForm):
    class Meta:
        model = ProposedCourse
        fields = ['name', 'credit', 'syllabus', 'prerequisites']

    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prerequisites'].queryset = Course.objects.all()


class ProposedCourseSelectionForm(forms.Form):
    courses_to_accept = forms.ModelMultipleChoiceField(
        queryset=ProposedCourse.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    courses_to_reject = forms.ModelMultipleChoiceField(
        queryset=ProposedCourse.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()

        # Extract the course IDs for acceptance and rejection
        accepted_ids = cleaned_data.get('courses_to_accept', [])
        rejected_ids = cleaned_data.get('courses_to_reject', [])

        # Check for intersection (courses cannot be selected for both accept and reject)
        common_courses = set(accepted_ids).intersection(set(rejected_ids))
        if common_courses:
            raise forms.ValidationError("A course cannot be selected for both approval and rejection.")

        # Ensure at least one course is selected
        if not accepted_ids and not rejected_ids:
            raise forms.ValidationError("You must select at least one course to approve")

        return cleaned_data
