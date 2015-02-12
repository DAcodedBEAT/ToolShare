from django import forms
from django.contrib.auth.models import User

from notifications.models import Notification


class ComposeNotification(forms.Form):
    """
    A simple default form for composition of private notifications.
    """

    recipient = forms.CharField(max_length=30, label="Recipient")
    title = forms.CharField(max_length=120, label="Title")
    message = forms.CharField(label="Message", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ComposeNotification, self).__init__(*args, **kwargs)

    def save(self, sender, commit=True):
        recipient_string = self.cleaned_data['recipient']
        recipient = User.objects.get(username=recipient_string)
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']
        notif = Notification(sender=sender, recipient=recipient, title=title, message=message)
        if commit:
            notif.save()
        return notif