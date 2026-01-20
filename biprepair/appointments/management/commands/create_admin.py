from django.core.management.base import BaseCommand, CommandError

from appointments.models import AdminUser


class Command(BaseCommand):
    help = "Create or update a local admin account for the student repair panel."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for admin login')
        parser.add_argument('full_name', type=str, help='Technician full name')
        parser.add_argument('password', type=str, help='Temporary password')

    def handle(self, *args, **options):
        username = options['username']
        full_name = options['full_name']
        password = options['password']

        admin, created = AdminUser.objects.get_or_create(username=username, defaults={'full_name': full_name})
        if not created:
            admin.full_name = full_name
        admin.set_password(password)
        admin.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'{action} admin user "{username}"'))
