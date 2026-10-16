from django.contrib import admin
from .models import Project, Task, Comment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','owner','created_at')
    search_fields = ('name','description')
    filter_horizontal = ('members',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title','project','assigned_to','status','priority','due_date')
    list_filter = ('status','priority','project')
    search_fields = ('title','description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task','author','created_at')
