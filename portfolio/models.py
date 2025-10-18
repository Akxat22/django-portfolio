# portfolio/models.py
from django.db import models
from django.utils.text import slugify # <-- Add this import
from ckeditor.fields import RichTextField 

class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class About(models.Model):
    name = models.CharField(max_length=100, default="Akshat Singh")
    title = models.CharField(max_length=200, default="Software Developer")
    description = models.TextField()
    profile_image = models.ImageField(upload_to='about/',blank=True)
    skills = models.ManyToManyField(Skill)
    
    # Use plural name in admin
    class Meta:
        verbose_name_plural = "About Section"

    def __str__(self):
        return self.name

class Experience(models.Model):
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.CharField(max_length=50) # Using CharField for flexibility like "Sep 2023 - May 2024"
    end_date = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.role} at {self.company}"

class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Project(models.Model):
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=200) # For the card subtitle
    long_description = models.TextField() # For the modal
    image = models.ImageField(upload_to='projects/',blank=True )
    link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
        
class SocialLink(models.Model):
    PLATFORM_CHOICES = [('email', 'Email'), ('github', 'GitHub'), ('linkedin', 'LinkedIn')]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    link = models.CharField(max_length=255) # Use CharField for mailto: links
    
    def __str__(self):
        return self.get_platform_display()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(About, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    
    # --- THIS LINE IS CHANGED ---
    content = RichTextField() # Was models.TextField()
    # --- END OF CHANGE ---

    excerpt = models.TextField(blank=True, help_text="A short summary of the post for list views.")
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at'] # Show newest posts first

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # ... (no changes to save method) ...
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        
        if not self.author:
             self.author = About.objects.first()
             
        super().save(*args, **kwargs)