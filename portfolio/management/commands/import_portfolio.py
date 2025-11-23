import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import About, Experience, Education, Project, SocialLink, BlogPost, Skill

class Command(BaseCommand):
    help = 'Import portfolio data from data.json'

    def handle(self, *args, **kwargs):
        # 1. Locate data.json in the root of the project (same level as manage.py)
        file_path = os.path.join(settings.BASE_DIR, 'data.json')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as file:
            data = json.load(file)

        self.stdout.write('Importing data...')

        # --- IMPORT ABOUT & SKILLS ---
        about_data = data.get('about', {})
        if about_data:
            # Create About Object
            about, created = About.objects.update_or_create(
                id=1, # Force ID 1 so we only have one "About" section
                defaults={
                    'name': about_data.get('name', 'My Name'),
                    'title': about_data.get('title', 'Developer'),
                    'description': about_data.get('description', ''),
                    # Note: We skip profile_image because importing images from URLs 
                    # requires downloading. We rely on template fallbacks.
                }
            )
            
            # Create and Add Skills
            skill_list = about_data.get('skills', [])
            current_skills = []
            for skill_name in skill_list:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                current_skills.append(skill_obj)
            
            about.skills.set(current_skills)
            self.stdout.write(self.style.SUCCESS(f'Updated About section for {about.name}'))

        # --- IMPORT SOCIAL LINKS ---
        socials = data.get('social_links', {})
        for platform, link in socials.items():
            SocialLink.objects.update_or_create(
                platform=platform,
                defaults={'link': link}
            )
        self.stdout.write(self.style.SUCCESS(f'Updated {len(socials)} Social Links'))

        # --- IMPORT PROJECTS ---
        projects = data.get('projects', [])
        for proj in projects:
            Project.objects.update_or_create(
                title=proj['title'],
                defaults={
                    'short_description': proj.get('short_description', ''),
                    'long_description': proj.get('long_description', ''),
                    'link': proj.get('link', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Updated {len(projects)} Projects'))

        # --- IMPORT EXPERIENCE ---
        experiences = data.get('experience', [])
        for exp in experiences:
            Experience.objects.update_or_create(
                company=exp['company'],
                role=exp['role'],
                defaults={
                    'start_date': exp.get('start_date', ''),
                    'end_date': exp.get('end_date', ''),
                    'description': exp.get('description', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Updated {len(experiences)} Experience entries'))

        # --- IMPORT EDUCATION ---
        educations = data.get('education', [])
        for edu in educations:
            # Convert string years to int if necessary
            s_year = int(edu.get('start_year', 2020))
            e_year = int(edu.get('end_year', 2024))
            
            Education.objects.update_or_create(
                institution=edu['institution'],
                degree=edu['degree'],
                defaults={
                    'start_year': s_year,
                    'end_year': e_year,
                    'description': edu.get('description', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Updated {len(educations)} Education entries'))

        # --- IMPORT BLOG POSTS ---
        posts = data.get('blog_posts', [])
        author = About.objects.first() # Assign the 'About' user as author
        
        for post in posts:
            BlogPost.objects.update_or_create(
                title=post['title'],
                defaults={
                    'excerpt': post.get('excerpt', ''),
                    'content': post.get('content', ''),
                    'author': author
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Updated {len(posts)} Blog Posts'))