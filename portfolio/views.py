from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import *
import threading # <--- Import this

# --- CLASS TO HANDLE BACKGROUND EMAILS ---
class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email_message.send()
        except Exception as e:
            print(f"Error sending email in background: {e}")

def home(request):
    """
    Main portfolio view handling display and contact form submission.
    """
    # --- HANDLE CONTACT FORM SUBMISSION ---
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and message:
            try:
                # Prepare context
                current_site = get_current_site(request)
                email_context = {
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'message_body': message,
                    'domain': current_site.domain
                }

                # 1. Prepare Admin Email (Do NOT send yet)
                html_admin = render_to_string('emails/contact_admin.html', email_context)
                text_admin = strip_tags(html_admin)
                
                msg_admin = EmailMultiAlternatives(
                    subject=f"Portfolio Contact: {subject} from {name}",
                    body=text_admin,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.EMAIL_HOST_USER]
                )
                msg_admin.attach_alternative(html_admin, "text/html")

                # 2. Prepare User Email (Do NOT send yet)
                html_user = render_to_string('emails/contact_user.html', email_context)
                text_user = strip_tags(html_user)
                
                msg_user = EmailMultiAlternatives(
                    subject="Thanks for contacting me!",
                    body=text_user,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg_user.attach_alternative(html_user, "text/html")

                # 3. Send Both in Background Threads
                # This prevents the server from waiting/timing out
                EmailThread(msg_admin).start()
                EmailThread(msg_user).start()

                messages.success(request, "Message sent successfully! I'll be in touch soon.")
                return redirect('home')
            
            except Exception as e:
                print(f"Email Error: {e}") 
                messages.error(request, "Error processing your request.")
        else:
            messages.error(request, "Please fill in all required fields.")

    # --- FETCH DATA ---
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