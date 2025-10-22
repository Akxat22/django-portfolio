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

def custom_404(request, exception):
    """
    Custom view for 404 Page Not Found errors.
    """
    # We still need to fetch 'about' and 'socials'
    # so the sidebar and header render correctly.
    about = About.objects.first()
    social_links = SocialLink.objects.all()
    socials = {link.platform: link.link for link in social_links}

    context = {
        'about': about,
        'socials': socials,
    }
    
    # Render the 404.html template with a 404 status code
    return render(request, 'portfolio/404.html', context, status=404)