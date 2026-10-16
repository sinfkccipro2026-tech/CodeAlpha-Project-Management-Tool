from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Project, Task, Comment

class Command(BaseCommand):
    help = 'Create a demo account, project, members, tasks and comments.'
    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username='demo', defaults={'email':'demo@example.com'})
        if created: user.set_password('Demo@12345'); user.save()
        p, _ = Project.objects.get_or_create(name='Website Launch', owner=user, defaults={'description':'Demo collaborative project for the CodeAlpha internship task.'})
        p.members.add(user)
        t1, _ = Task.objects.get_or_create(project=p, title='Design landing page', defaults={'description':'Create the responsive landing page.','assigned_to':user,'status':'progress','priority':'high','created_by':user})
        t2, _ = Task.objects.get_or_create(project=p, title='Prepare release checklist', defaults={'description':'Review testing, documentation and deployment steps.','assigned_to':user,'status':'todo','priority':'medium','created_by':user})
        Comment.objects.get_or_create(task=t1, author=user, body='Started the first draft.')
        self.stdout.write(self.style.SUCCESS('Demo data ready. Login: demo / Demo@12345'))
