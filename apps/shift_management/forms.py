from django import forms
from .models import Shift, ShiftVolunteer, Store


class ShiftForm(forms.ModelForm):
    shift_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    
    class Meta:
        model = Shift
        fields = ['store', 'title', 'description', 'role_required', 'shift_date', 
                  'start_time', 'end_time', 'slots_available']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'role_required': forms.Select(attrs={'class': 'form-control'}),
            'slots_available': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'city', 'state', 'zip_code', 'phone', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }


class VolunteerReviewForm(forms.ModelForm):
    class Meta:
        model = ShiftVolunteer
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
