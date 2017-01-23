from django_comments import forms
from pagedown.widgets import PagedownWidget

class CommentForm(forms.CommentForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget = PagedownWidget()

