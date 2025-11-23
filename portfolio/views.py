from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import *
import threading 

# --- BACKGROUND EMAIL WORKER ---
class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email_message.send()
        except Exception as e:
            # This prints the exact error to Render Logs
            print(f"❌ Error sending email: {e}")

def home(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and message:
            try:
                current_site = get_current_site(request)
                context = {
                    'name': name, 'email': email, 'subject': subject,
                    'message_body': message, 'domain': current_site.domain
                }

                # --- FIX FOR 400 ERROR: ENSURE BODY IS NEVER EMPTY ---
                # We define a default text message first.
                text_content_admin = f"Name: {name}\nEmail: {email}\nMessage: {message}"
                text_content_user = f"Hi {name},\nThanks for contacting me. I received your message: {subject}"

                # Try to load HTML, but don't crash if missing
                try:
                    html_admin = render_to_string('emails/contact_admin.html', context)
                    html_user = render_to_string('emails/contact_user.html', context)
                except Exception as e:
                    print(f"⚠️ Template Warning: Could not load HTML templates: {e}")
                    html_admin = None
                    html_user = None

                # 1. Admin Email
                msg_admin = EmailMultiAlternatives(
                    subject=f"Portfolio Contact: {subject}",
                    body=text_content_admin, # Forced text content
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL]
                )
                if html_admin: 
                    msg_admin.attach_alternative(html_admin, "text/html")

                # 2. User Email
                msg_user = EmailMultiAlternatives(
                    subject="Thanks for contacting me!",
                    body=text_content_user, # Forced text content
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                if html_user:
                    msg_user.attach_alternative(html_user, "text/html")

                # Send in background
                EmailThread(msg_admin).start()
                EmailThread(msg_user).start()

                messages.success(request, "Message sent successfully!")
                return redirect('home')
            
            except Exception as e:
                print(f"General Error: {e}")
                messages.error(request, "Error processing request.")
        else:
            messages.error(request, "Please fill in all fields.")

    # ... (Keep the rest of your view code for About, Jobs, etc. exactly the same)
    about = About.objects.first()
    jobs = Experience.objects.order_by('-start_date')
    educations = Education.objects.order_by('-end_year')
    projects = Project.objects.all()
    social_links = SocialLink.objects.all()
    recent_posts = BlogPost.objects.order_by('-published_at')[:5]
    
    socials = {}
    for link in social_links:
        socials[link.platform] = link.link
        if link.platform == 'email':
            socials['email_link'] = link.link.replace('mailto:', '')

    context = {
        'about': about,
        'jobs': jobs,
        'educations': educations,
        'projects': projects,
        'socials': socials,
        'recent_posts': recent_posts,
    }
    return render(request, 'portfolio/home.html', context)

def resume_html_view(request):
    """
    Renders the printable resume page.
    """
    about = About.objects.first()
    if not about:
        return HttpResponse("No 'About' data found.", status=404)

    skills = about.skills.all()
    jobs = Experience.objects.order_by('-start_date')
    educations = Education.objects.order_by('-end_year')
    projects = Project.objects.all()
    social_links = SocialLink.objects.all()
    
    socials = {}
    for link in social_links:
        socials[link.platform] = link.link
        if link.platform == 'email':
            socials['email_link'] = link.link.replace('mailto:', '')

    context = {
        'about': about,
        'skills': skills,
        'jobs': jobs,
        'educations': educations,
        'socials': socials,
        'projects': projects,
    }

    return render(request, 'portfolio/resume_page.html', context)


def custom_404(request, exception):
    about = About.objects.first()
    social_links = SocialLink.objects.all()
    socials = {link.platform: link.link for link in social_links}
    context = {
        'about': about,
        'socials': socials,
    }
    return render(request, 'portfolio/404.html', context, status=404)