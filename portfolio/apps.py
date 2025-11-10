from django.apps import AppConfig
import os
import json

class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio'

    def ready(self):
        """
        This method is called when the app is ready.
        We'll load our JSON data here.
        """
        # Import models here to avoid AppRegistryNotReady error
        from .models import Skill, About, Experience, Education, Project, SocialLink

        # --- CHECK: Only run if DB is empty ---
        # We check a key model (like About). If it has data, we assume
        # the database is already seeded and we skip this.
        if About.objects.exists():
            return  # Exit if data already exists

        print("Database is empty. Seeding data from data.json...")

        # --- Define path to JSON file ---
        # This assumes 'data.json' is in the same directory as this 'apps.py'
        json_path = os.path.join(os.path.dirname(__file__), 'data.json')

        if not os.path.exists(json_path):
            print(f"Warning: data.json not found at {json_path}. Cannot seed database.")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # --- 1. Load Skills ---
            # We must create these first to link them to 'About'
            skill_objects = {} # To hold the created Skill instances
            if 'skills' in data:
                for skill_data in data['skills']:
                    skill, _ = Skill.objects.get_or_create(**skill_data)
                    skill_objects[skill.name] = skill # Store by name
                print(f"Loaded {len(skill_objects)} skills.")

            # --- 2. Load About ---
            if 'about' in data:
                about_data = data['about']
                skill_names = about_data.pop('skills', []) # Get skill names
                
                # Use get_or_create for safety
                about, _ = About.objects.get_or_create(name=about_data.get('name'), defaults=about_data)
                
                # Link skills
                for skill_name in skill_names:
                    if skill_name in skill_objects:
                        about.skills.add(skill_objects[skill_name])
                print(f"Created 'About' entry for {about.name}.")

            # --- 3. Load Experience ---
            if 'experience' in data:
                for exp_data in data['experience']:
                    Experience.objects.get_or_create(**exp_data)
                print(f"Loaded {len(data['experience'])} experience entries.")

            # --- 4. Load Education ---
            if 'education' in data:
                for edu_data in data['education']:
                    Education.objects.get_or_create(**edu_data)
                print(f"Loaded {len(data['education'])} education entries.")

            # --- 5. Load Projects ---
            if 'projects' in data:
                for proj_data in data['projects']:
                    Project.objects.get_or_create(**proj_data)
                print(f"Loaded {len(data['projects'])} project entries.")

            # --- 6. Load Social Links ---
            if 'social_links' in data:
                for link_data in data['social_links']:
                    SocialLink.objects.get_or_create(**link_data)
                print(f"Loaded {len(data['social_links'])} social link entries.")
            
            print("--- Database seeding complete. ---")

        except Exception as e:
            print(f"An error occurred during data seeding: {e}")