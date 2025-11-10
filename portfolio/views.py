from django.shortcuts import render
from .models import *
from django.http import HttpResponse 
# (Delete fpdf, xhtml2pdf, and any other PDF imports)


def home(request):
    # ... (this view is fine, no changes) ...
    about = About.objects.first() 
    jobs = Experience.objects.order_by('-start_date')
    educations = Education.objects.order_by('-end_year')
    projects = Project.objects.all()
    social_links = SocialLink.objects.all()
    recent_posts = BlogPost.objects.order_by('-published_at')[:5]
    socials = {link.platform: link.link for link in social_links}
    context = {
        'about': about,
        'jobs': jobs,
        'educations': educations,
        'projects': projects,
        'socials': socials,
        'recent_posts': recent_posts,
    }
    return render(request, 'portfolio/home.html', context)


# --- DELETE the old 'download_resume_pdf' function ---
# --- ADD THIS NEW VIEW ---

def resume_html_view(request):
    """
    Renders a standalone HTML page for the resume.
    """
    # 1. Fetch all the data
    about = About.objects.first()
    if not about:
        return HttpResponse("No 'About' data found. Please add data in the admin panel.", status=404)

    skills = about.skills.all()
    jobs = Experience.objects.order_by('-start_date')
    educations = Education.objects.order_by('-end_year')
    social_links = SocialLink.objects.all()
    
    # --- ADD THIS LINE ---
    projects = Project.objects.all() # <-- This line was missing

    socials = {}
    for link in social_links:
        socials[link.platform] = link.link
        if link.platform == 'email':
            socials['email_link'] = link.link.replace('mailto:', '')

    # 2. Define the context for the HTML template
    context = {
        'about': about,
        'skills': skills,
        'jobs': jobs,
        'educations': educations,
        'socials': socials,
        'projects': projects, # <-- Add 'projects' to the context
    }

    # 3. Render the new HTML page
    return render(request, 'portfolio/resume_page.html', context)
# --- END OF NEW VIEW ---


def custom_404(request, exception):
    # ... (this view is fine, no changes) ...
    about = About.objects.first()
    social_links = SocialLink.objects.all()
    socials = {link.platform: link.link for link in social_links}
    context = {
        'about': about,
        'socials': socials,
    }
    return render(request, 'portfolio/404.html', context, status=404)







