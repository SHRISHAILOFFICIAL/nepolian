from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

SECURITY_QUESTIONS = [
    ('', 'Select a security question'),
    ('pet', 'What was the name of your first pet?'),
    ('city', 'In which city were you born?'),
    ('school', 'What is the name of your elementary school?'),
    ('color', 'What is your favorite color?'),
    ('mother', 'What is your mother\'s maiden name?'),
]

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    security_question = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    security_answer = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 
                  'security_question', 'security_answer', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.security_question = self.cleaned_data['security_question']
        # Store hashed security answer
        user.security_answer = self.cleaned_data['security_answer'].lower().strip()
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    

class SecurityQuestionForm(forms.Form):
    security_answer = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data
