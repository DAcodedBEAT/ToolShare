from django import forms
from django.forms import ModelForm

from ToolShare.models import Tool, Checkout, Category
from accounts.models import Locations

star_dict = (
    (5, '★★★★★ (5 stars)'),
    (4, '★★★★☆ (4 stars)'),
    (3, '★★★☆☆ (3 stars)'),
    (2, '★★☆☆☆ (2 stars)'),
    (1, '★☆☆☆☆ (1 star)'))

yes_no_dict = ((False, 'No'), (True, 'Yes'))


class AddToolForm(ModelForm):
    """
    Creates the form to add a new Tool. (also used to edit existing Tools)
    """
    location = forms.ModelChoiceField(queryset=Locations.objects.none())
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    #request = forms.ChoiceField(choices=yes_no_dict, label="Do you want users to request this object?")

    def __init__(self, user=None, *args, **kwargs):
        super(AddToolForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Locations.objects.filter(user=user)

    class Meta:
        model = Tool
        fields = ['title', 'description', 'location', 'pic', 'category']
        exclude = ('tid', 'owner')


class CheckInForm(ModelForm):
    rating = forms.ChoiceField(choices=star_dict)

    def __init__(self, user=None, *args, **kwargs):
        super(CheckInForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Checkout
        fields = ['rating', 'review']

class OptionsForm(forms.Form):
    show_all = forms.ChoiceField(choices=[('false','Show Available Tools'), ('true','Show All Tools')], label="Show All Tools?", required=False)
    sort_by  = forms.ChoiceField(choices=[('nearest','nearest'),('farthest','farthest'), ('','whatever')], label="Sort by", required=False)
    distance = forms.CharField(label="Search radius (miles)", required=False)
    search = forms.CharField(label="Text Search", required=False)
    cat_id     = forms.ModelChoiceField(queryset=Category.objects.all(),required=False, label="Category")


class AddCat(ModelForm):

    class Meta:
        model = Category
        fields = ['value']