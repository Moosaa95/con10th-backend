from django.core.management.base import BaseCommand
from apps.services.models import Skill

# List of predefined skills
SKILLS_TO_ADD = [
    {"name": "Python", "code": "PY01"},
    {"name": "Django", "code": "DJ02"},
    {"name": "React", "code": "RJ03"},
    {"name": "Machine Learning", "code": "ML04"},
    {"name": "Data Analysis", "code": "DA05"},
    {"name": "Cybersecurity", "code": "CS06"},
    {"name": "DevOps", "code": "DO07"},
    {"name": "Cloud Computing", "code": "CC08"},
    {"name": "Mobile Development", "code": "MD09"},
    {"name": "UI/UX Design", "code": "UX10"},
]

class Command(BaseCommand):
    help = "Automatically adds predefined skills to the database."

    def handle(self, *args, **kwargs):
        added_count = 0
        for skill_data in SKILLS_TO_ADD:
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"], 
                code=skill_data["code"]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added: {skill.name} ({skill.code})"))
                added_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {skill.name} ({skill.code})"))

        if added_count > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully added {added_count} skills!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No new skills were added. All already exist."))
