"""
Django management command to create an admin user.
Usage: python manage.py createadmin
"""
from django.core.management.base import BaseCommand
from accounts.models import User
import getpass


class Command(BaseCommand):
    help = 'Create an admin user with role=admin, is_staff=True, and is_superuser=True'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@cvplatform.com',
            help='Email for the admin user (default: admin@cvplatform.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user (if not provided, will prompt)'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Use defaults without prompting (requires --password)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        no_input = options['no_input']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists.')
            )
            
            if not no_input:
                response = input('Update this user to admin? (y/n): ').strip().lower()
                if response != 'y':
                    self.stdout.write(self.style.ERROR('Cancelled.'))
                    return
        else:
            # Get password if not provided
            if not password:
                if no_input:
                    self.stdout.write(
                        self.style.ERROR('Error: --password required when using --no-input')
                    )
                    return
                password = getpass.getpass('Enter password: ')
                password_confirm = getpass.getpass('Confirm password: ')
                
                if password != password_confirm:
                    self.stdout.write(self.style.ERROR('Passwords do not match!'))
                    return
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ User "{username}" created!')
            )

        # Set admin privileges
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Admin user "{username}" is ready!')
        )
        self.stdout.write(f'   Email: {user.email}')
        self.stdout.write(f'   Role: {user.role}')
        self.stdout.write(f'   Staff: {user.is_staff}')
        self.stdout.write(f'   Superuser: {user.is_superuser}')
        self.stdout.write(f'\nYou can now login at: /admin/')

