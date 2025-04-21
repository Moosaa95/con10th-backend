import uuid
from django.core.management.base import BaseCommand, CommandError
from apps.category.models import Skill, Category

class Command(BaseCommand):
    help = "Create a new skill"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str)
        parser.add_argument("category_id", type=str)

    def handle(self, *args, **options):
        name = options["name"]
        category_id = options["category_id"]

        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise CommandError("Invalid UUID format for category_id.")

        try:
            category = Category.objects.get(id=category_uuid)
        except Category.DoesNotExist:
            raise CommandError(f"No category found with ID {category_id}")

        skill = Skill.create_skill(name=name, category=category)
        self.stdout.write(self.style.SUCCESS(f'Skill "{skill.name}" created with ID {skill.id}'))
