from django.core.management.base import BaseCommand
from apps.services.models import Service, Skill
import random

class Command(BaseCommand):
    help = 'Generate random services and skills'

    def handle(self, *args, **kwargs):
        skills_data = [
            {"name": "Web Development", "code": "WEBDEV"},
            {"name": "Data Analysis", "code": "DATAAN"},
            {"name": "Graphic Design", "code": "GRPHCS"},
            {"name": "Digital Marketing", "code": "DIGMKT"},
            {"name": "Cyber Security", "code": "CYBERSEC"},
        ]
        
        # Create skills if they don't exist
        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(**skill_data)
            skills.append(skill)
            self.stdout.write(self.style.SUCCESS(f"Skill {'created' if created else 'exists'}: {skill.name}"))
        
        # Generate random services
        for i in range(10):
            skill = random.choice(skills)
            service, created = Service.objects.get_or_create(
                skill=skill,
                title=f"{skill.name} Service {i+1}",
                description=f"Description for {skill.name} service {i+1}",
                price=random.uniform(50, 500),
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f"Service {'created' if created else 'exists'}: {service.title}"))
        
        self.stdout.write(self.style.SUCCESS('Random services and skills generated successfully!'))
