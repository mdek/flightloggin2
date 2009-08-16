from django.forms import ModelChoiceField, ModelForm
from models import *
from tagging.forms import TagField
from django import forms

class PlaneForm(ModelForm):
    
    tags = TagField(widget=forms.Textarea)
    
    class Meta:
        model = Plane

class PlaneField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.tailnumber, obj.type)
