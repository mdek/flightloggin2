from django.utils.safestring import mark_safe
from django import forms

from constants import GRAPH_FIELDS, FIELD_ABBV
   
def print_table(data, row_length):
    out = '<table id="filter_table">'
    counter = 0
    for element in data:
        if counter % row_length == 0:
            out += '<tr>'
        out += '<td>%s</td>' % element
        counter += 1
        if counter % row_length == 0:
            out += '</tr>'
    if counter % row_length != 0:
        for i in range(0, row_length - counter % row_length):
            out += '<td> </td>'
        out += '</tr>'
    out += '</table>'
    
    return mark_safe(out)
    
def render_table(self):
    out=[]
    for field in GRAPH_FIELDS:
        num_field = str(self[field])
        op = str(self[field + "_op"])
        title = getattr(self, 'fields')[field].label
        out.append( title + op + num_field )

    return print_table(out, 4)
        
                
def make_filter_form():
    operators = ( (0, "="), (1, ">"), (2, "<") )
    fields = {'tags': forms.CharField(),
              'tailnumber': forms.CharField(),
              'type_': forms.ChoiceField(choices=[(0,'C-152'),(1,'C-172')]),
              'cat_class': forms.ChoiceField(choices=[(0,'SEL'),(1,'MEL')]),
              'start_date': forms.DateField(widget=forms.TextInput(attrs={"class": "date_picker"})),
              'end_date': forms.DateField(widget=forms.TextInput(attrs={"class": "date_picker"})),
             }
             
    for field in GRAPH_FIELDS:
        d = {field: forms.FloatField(label=FIELD_ABBV[field], widget=forms.TextInput(attrs={"class": "small_picker"})), 
             field + "_op": forms.ChoiceField(choices=operators, widget=forms.Select(attrs={"class": "op_select"})),
             }
        fields.update(d)
        
    FilterForm = type('FilterForm', (forms.BaseForm,), { 'base_fields': fields })
    FilterForm.render_table = render_table
    
    return FilterForm











