
import csv
from pathlib import Path
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

from tasks.models import Project, Task


class Command(BaseCommand):
    help = "Import TaskFlow projects and tasks from CSV files without deleting existing data."

    def handle(self, *args, **options):
        base_dir = Path.cwd()
        projects_file = base_dir / "projects_dataset.csv"
        tasks_file = base_dir / "tasks_dataset.csv"

        if not projects_file.exists() or not tasks_file.exists():
            raise CommandError(
                "Place projects_dataset.csv and tasks_dataset.csv "
                "in the same folder as manage.py."
            )

        default_user = User.objects.order_by("id").first()
        if default_user is None:
            raise CommandError(
                "No Django users exist. Create a user first with "
                "python manage.py createsuperuser."
            )

        project_map = {}
        projects_created = 0
        tasks_created = 0
        projects_skipped = 0
        tasks_skipped = 0

        def find_user(value):
            value = (value or "").strip()
            if not value:
                return None

            user = User.objects.filter(username__iexact=value).first()
            if user:
                return user

            parts = value.split(maxsplit=1)
            if len(parts) == 2:
                user = User.objects.filter(
                    first_name__iexact=parts[0],
                    last_name__iexact=parts[1],
                ).first()
                if user:
                    return user

            return None

        def parse_date(value):
            value = (value or "").strip()
            if not value:
                return None
            try:
                return date.fromisoformat(value)
            except ValueError:
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping invalid date value: {value}"
                    )
                )
                return None

        with transaction.atomic():
            with projects_file.open(
                "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                required = {"project_id", "name", "description", "owner"}
                if not reader.fieldnames or not required.issubset(
                    set(reader.fieldnames)
                ):
                    raise CommandError(
                        "projects_dataset.csv is missing required columns: "
                        + ", ".join(sorted(required))
                    )

                for row in reader:
                    external_id = (row.get("project_id") or "").strip()
                    name = (row.get("name") or "").strip()

                    if not external_id or not name:
                        continue

                    owner = find_user(row.get("owner")) or default_user

                    project = Project.objects.filter(name=name).first()
                    if project:
                        projects_skipped += 1
                    else:
                        project = Project.objects.create(
                            name=name,
                            description=(row.get("description") or "").strip(),
                            owner=owner,
                        )
                        projects_created += 1

                    project_map[external_id] = project

            with tasks_file.open(
                "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                required = {
                    "project_id", "title", "description",
                    "status", "priority", "assigned_to", "due_date",
                }
                if not reader.fieldnames or not required.issubset(
                    set(reader.fieldnames)
                ):
                    raise CommandError(
                        "tasks_dataset.csv is missing required columns: "
                        + ", ".join(sorted(required))
                    )

                for row in reader:
                    external_project_id = (
                        row.get("project_id") or ""
                    ).strip()
                    title = (row.get("title") or "").strip()

                    project = project_map.get(external_project_id)
                    if not project or not title:
                        continue

                    if Task.objects.filter(
                        project=project, title=title
                    ).exists():
                        tasks_skipped += 1
                        continue

                    status = (row.get("status") or "todo").strip().lower()
                    if status not in {"todo", "progress", "done"}:
                        status = "todo"

                    priority = (
                        row.get("priority") or "medium"
                    ).strip().lower()
                    if priority not in {"low", "medium", "high"}:
                        priority = "medium"

                    assigned_to = find_user(row.get("assigned_to"))

                    Task.objects.create(
                        project=project,
                        title=title,
                        description=(row.get("description") or "").strip(),
                        status=status,
                        priority=priority,
                        assigned_to=assigned_to,
                        due_date=parse_date(row.get("due_date")),
                        created_by=project.owner,
                    )
                    tasks_created += 1

        self.stdout.write(self.style.SUCCESS("TaskFlow CSV import finished."))
        self.stdout.write(f"Projects created: {projects_created}")
        self.stdout.write(f"Projects already present: {projects_skipped}")
        self.stdout.write(f"Tasks created: {tasks_created}")
        self.stdout.write(f"Tasks already present: {tasks_skipped}")
        self.stdout.write(
            f"Database totals — projects: {Project.objects.count()}, "
            f"tasks: {Task.objects.count()}"
        )
