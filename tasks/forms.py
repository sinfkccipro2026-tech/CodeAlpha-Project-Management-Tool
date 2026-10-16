from django import forms
from django.contrib.auth.models import User
from .models import Project, Task, Comment

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    class Meta:
        model = User
        fields = ['username','email','password']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name','description']
        widgets = {'description': forms.Textarea(attrs={'rows':4})}

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','assigned_to','status','priority','due_date']
        widgets = {'description': forms.Textarea(attrs={'rows':4}), 'due_date': forms.DateInput(attrs={'type':'date'})}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows':3, 'placeholder':'Write a comment...'} )}
