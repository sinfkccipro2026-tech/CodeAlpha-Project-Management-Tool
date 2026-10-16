TaskFlow sample dataset

Files:
- projects_dataset.csv: 20 sample projects
- tasks_dataset.csv: 100 sample tasks linked to project_id values 1-20

Important:
These are sample CSV files only. They do not change your Django dashboard or database automatically.
The task status values are todo, progress, and done to match the status values visible in the TaskFlow project error trace.

To use the data, first inspect your models in tasks/models.py and the field names in the Django Project and Task models. If your models differ, the CSV columns may need mapping before importing. Do not replace your database or delete db.sqlite3.
