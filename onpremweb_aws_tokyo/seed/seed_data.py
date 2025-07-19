# onpremweb/seed/seed_data.py
from django.core.management.base import BaseCommand
from community.models import Category

class Command(BaseCommand):
    help = 'Seed initial sample data for the community app'

    def handle(self, *args, **options):
        categories = ['공지사항', '자유게시판', '질문과답변']
        for name in categories:
            obj, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category "{name}" created.'))
            else:
                self.stdout.write(f'Category "{name}" already exists.')
