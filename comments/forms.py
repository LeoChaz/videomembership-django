from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Comment

# Pour tester
# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ('text', 'user', 'path')

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Write your comment."}))

    def __init__(self, data=None, files=None, **kwargs):
        super(CommentForm, self).__init__(data, files, kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.add_input(Submit('Submit', 'Add comment', css_class='btn btn-primary',))















