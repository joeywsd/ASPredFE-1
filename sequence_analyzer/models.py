from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MaxLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class PredictionModel(models.Model): 
    # under django's model, view, template structure
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField(blank=True, null=True)
    model_path = models.CharField(max_length=255)  
    # Path to model folder

    # good for production, knowing when a model was first added. when it was updated, if it's active
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # timestamp set only once- when record is created 

    updated_at = models.DateTimeField(auto_now=True)
    # timestamp set every time it is saved

    # optional
    class Meta:
        ordering = ['name']

    # optional, When Django displays a SequenceSubmission (admin interface, error messages, debugging), it shows this string instead of garbage:
    def __str__(self):
        return self.name


class SequenceSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE, null=True, blank=True) #stops asking me for a default value
    title = models.CharField(
        max_length=100,
        default='untitled_sequence',
        help_text='Sequence title/identifier (from FASTA header)'
    )
    sequence = models.CharField(
        max_length=130,
        validators=[
            RegexValidator(
                regex='^[acdefghiklmnpqrstvwxyACDEFGHIKLMNPQRSTVWY]+$',
                message='Sequence must contain only valid amino acid letters (ACDEFGHIKLMNPQRSTVWY)',
                code='invalid_sequence'
            ),
            MaxLengthValidator(130)
        ]
    )
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('done', 'Done')],
        default='pending'
    )
    submit_date = models.DateTimeField(auto_now_add=True)
    result = models.FloatField(default=0)
    result_date = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submit_date']

    def __str__(self):
        return f"{self.title} by {self.user.username} using {self.prediction_model.name} on {self.submit_date}"