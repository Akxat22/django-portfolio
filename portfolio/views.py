# portfolio/views.py
from django.shortcuts import render
from .models import *

def home(request):
    # Fetching the first (and likely only) About object
    about = About.objects.first() 
    
    # Fetching all other objects, ordered as desired
    jobs = Experience.objects.order_by('-start_date') # Order by most recent job
    educations = Education.objects.order_by('-end_year')
    projects = Project.objects.all()
    social_links = SocialLink.objects.all()
    
    # --- MODIFIED THIS QUERY ---
    # Fetching recent posts (e.g., the 5 most recent)
    recent_posts = BlogPost.objects.order_by('-published_at')[:5] # <-- Changed from 3 to 5
    
    # Create a dictionary to easily access social links in the template
    socials = {link.platform: link.link for link in social_links}

    context = {
        'about': about,
        'jobs': jobs,
        'educations': educations,
        'projects': projects,
        'socials': socials,
        'recent_posts': recent_posts, # <-- Add this to context
    }
    
    return render(request, 'portfolio/home.html', context)