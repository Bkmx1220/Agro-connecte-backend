from django.db import models
from django.contrib.auth.models import AbstractUser


# =====================================================
# USER
# =====================================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('paysan', 'Paysan'),
        ('expert', 'Expert'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='paysan')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# =====================================================
# PAYSAN (NOUVEAU)
# =====================================================
class Paysan(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="paysan_profile"
    )
    region = models.CharField(max_length=100)
    type_culture = models.CharField(max_length=150)
    superficie = models.FloatField(help_text="Superficie en hectares")
    experience = models.IntegerField(help_text="Années d'expérience agricole")

    def __str__(self):
        return self.user.username


# =====================================================
# EXPERT
# =====================================================
class Expert(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='expert_profile'
    )
    domaine = models.CharField(max_length=200)
    experience = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.user.username


# =====================================================
# CONSULTATION
# =====================================================
class Consultation(models.Model):
    STATUS = (
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
        ('completed', 'Terminée'),
    )

    paysan = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='paysan_consultations'
    )
    expert = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expert_consultations',
        null=True,
        blank=True
    )

    sujet = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sujet


# =====================================================
# MESSAGE
# =====================================================
class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]
