# portfolio/migrations/0004_create_superuser.py (or whatever yours is named)

import os
from django.db import migrations
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    """
    Creates a superuser from environment variables.
    """
    User = get_user_model()
    
    # Get details from environment variables
    SUPERUSER_NAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    # Don't create if any variable is missing
    if not all([SUPERUSER_NAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD]):
        print("\nSKIPPING SUPERUSER CREATION: ")
        print("Please set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL,")
        print("and DJANGO_SUPERUSER_PASSWORD environment variables.\n")
        return

    # Create the superuser
    if not User.objects.filter(username=SUPERUSER_NAME).exists():
        print(f"\nCreating superuser: {SUPERUSER_NAME}")
        User.objects.create_superuser(
            username=SUPERUSER_NAME,
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD
        )
    else:
        print(f"\nSuperuser '{SUPERUSER_NAME}' already exists. Skipping.")


class Migration(migrations.Migration):

    dependencies = [
        # Change '0003_auto_...' to the name of your *previous* migration file
        ('portfolio', '0004_alter_blogpost_content'), 
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]