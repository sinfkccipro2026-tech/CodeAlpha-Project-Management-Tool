from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegisterForm, ProjectForm, TaskForm, CommentForm
from .models import Project, Task

@login_required
def dashboard(request):
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    assigned = Task.objects.filter(assigned_to=request.user)
    stats = {'projects': projects.count(), 'todo': assigned.filter(status='todo').count(), 'progress': assigned.filter(status='progress').count(), 'done': assigned.filter(status='done').count()}
    return render(request, 'tasks/dashboard.html', {'projects': projects, 'stats': stats})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False); user.set_password(form.cleaned_data['password']); user.save()
            login(request, user); messages.success(request, 'Account created successfully.'); return redirect('dashboard')
    else: form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False); project.owner = request.user; project.save(); project.members.add(request.user)
            messages.success(request, 'Project created.'); return redirect('project_board', project.id)
    else: form = ProjectForm()
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create Project', 'back': 'dashboard'})

@login_required
def project_board(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner and not project.members.filter(id=request.user.id).exists():
        messages.error(request, 'You do not have access to this project.'); return redirect('dashboard')
    tasks = project.tasks.select_related('assigned_to','created_by')
    return render(request, 'tasks/project_board.html', {'project': project, 'tasks': tasks, 'comment_forms': {t.id: CommentForm() for t in tasks}})

@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner and not project.members.filter(id=request.user.id).exists(): return redirect('dashboard')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['assigned_to'].queryset = project.members.all()
        if form.is_valid():
            task = form.save(commit=False); task.project = project; task.created_by = request.user; task.save()
            messages.success(request, 'Task created and assigned.'); return redirect('project_board', project.id)
    else:
        form = TaskForm(); form.fields['assigned_to'].queryset = project.members.all()
    return render(request, 'tasks/form.html', {'form': form, 'title': f'Add Task · {project.name}', 'back': 'project_board', 'back_id': project.id})


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if (
        request.user != task.project.owner
        and not task.project.members.filter(id=request.user.id).exists()
    ):
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
    else:
        form = TaskForm(instance=task)

    # Include the project owner and all project members.
    form.fields['assigned_to'].queryset = (
        User.objects.filter(
            Q(id=task.project.owner_id)
            | Q(projects__id=task.project.id)
        ).distinct()
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Task updated.')
        return redirect('project_board', task.project.id)

    return render(
        request,
        'tasks/form.html',
        {
            'form': form,
            'title': 'Edit Task',
            'back': 'project_board',
            'back_id': task.project.id,
        },
    )



@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project_id = task.project.id

    if request.method == 'POST' and (
        request.user == task.project.owner
        or task.project.members.filter(id=request.user.id).exists()
    ):
        task.delete()
        messages.success(request, 'Task deleted.')

    return redirect('project_board', project_id)


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST' and (
        request.user == task.project.owner
        or task.project.members.filter(id=request.user.id).exists()
    ):
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added.')

    return redirect('project_board', task.project.id)
