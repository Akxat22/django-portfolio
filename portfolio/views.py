from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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
            # This prints the exact error to Render Logs so we can debug
            print(f"❌ Error sending email in background: {e}")

def home(request):
    # --- HANDLE CONTACT FORM ---
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

                # --- 1. GUARANTEE TEXT CONTENT (Fixes Brevo 400 Error) ---
                # We manually create the string so 'body' is never empty
                text_content_admin = f"New Contact from Portfolio!\n\nName: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
                text_content_user = f"Hi {name},\n\nThanks for reaching out! I have received your message regarding '{subject}' and will get back to you shortly.\n\nBest,\nAkshat Singh"

                # --- 2. TRY TO LOAD HTML (But don't crash if missing) ---
                html_admin = None
                html_user = None
                try:
                    html_admin = render_to_string('emails/contact_admin.html', context)
                    html_user = render_to_string('emails/contact_user.html', context)
                except Exception as e:
                    print(f"⚠️ Template Warning: HTML templates not found ({e}). Sending text-only version.")

                # --- 3. CONSTRUCT ADMIN EMAIL ---
                msg_admin = EmailMultiAlternatives(
                    subject=f"Portfolio Contact: {subject}",
                    body=text_content_admin, # Always has content now
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL]
                )
                if html_admin: 
                    msg_admin.attach_alternative(html_admin, "text/html")

                # --- 4. CONSTRUCT USER EMAIL ---
                msg_user = EmailMultiAlternatives(
                    subject="Thanks for contacting me!",
                    body=text_content_user, # Always has content now
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                if html_user:
                    msg_user.attach_alternative(html_user, "text/html")

                # --- 5. SEND IN BACKGROUND ---
                EmailThread(msg_admin).start()
                EmailThread(msg_user).start()

                messages.success(request, "Message sent successfully!")
                return redirect('home')
            
            except Exception as e:
                print(f"❌ General Error in view: {e}")
                messages.error(request, "Error processing request.")
        else:
            messages.error(request, "Please fill in all fields.")

    # --- FETCH DATA (Existing Code) ---
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