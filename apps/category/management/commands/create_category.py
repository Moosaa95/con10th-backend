from django.core.management.base import BaseCommand
from apps.category.models import Category


class Command(BaseCommand):
    help = "Create a new category from the command line"

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Name of the category')
        parser.add_argument('--status', type=str, default='pending', help='Status of the category')
        parser.add_argument('--is_predefined', type=bool, default=False, help='Is this category predefined?')
        parser.add_argument('--image', type=str, default=None, help='Optional image path or URL')

    def handle(self, *args, **options):
        category = Category.create_category(
            name=options['name'],
            status=options['status'],
            is_predefined=options['is_predefined'],
            image=options['image'],
        )
        print("category", category.id)
        if category:
            self.stdout.write(self.style.SUCCESS(f'✅ Category "{category.name}" created successfully.'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to create category.'))
