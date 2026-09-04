from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# =====================================================
# USER
# =====================================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('paysan', 'Paysan'),
        ('expert', 'Expert'),
        ('admin', 'Admin'),
        ("eleveur", "Eleveur"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='paysan')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

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
    type_animal = models.CharField(max_length=50, blank=True)
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
    
# =====================================================
# MODULE (GUIDES EXPERT)
# =====================================================
class Module(models.Model):
    expert = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="modules"
    )

    titre = models.CharField(max_length=255)
    description = models.TextField()
    fichier = models.FileField(upload_to="modules/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


# =====================================================
# ELEVEUR
# =====================================================

class Elevage(models.Model):

    TYPE_ANIMAL_CHOICES = [
        ("poulet", "Poulet"),
        ("vache", "Vache"),
        ("chevre", "Chèvre"),
        ("mouton", "Mouton"),
        ("porc", "Porc"),
        ("poisson", "Poisson"),
        ("autre", "Autre"),
    ]

    SYSTEME_ELEVAGE = [
        ("intensif", "Intensif"),
        ("extensif", "Extensif"),
        ("semi-intensif", "Semi-intensif"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="elevages"
    )

    type_animal = models.CharField(
        max_length=50,
        choices=TYPE_ANIMAL_CHOICES
    )

    nom = models.CharField(
        max_length=150,
        help_text="Nom de l'élevage ou du projet"
    )

    nombre = models.PositiveIntegerField()

    systeme = models.CharField(
        max_length=20,
        choices=SYSTEME_ELEVAGE,
        default="extensif"
    )

    description = models.TextField(blank=True)

    localisation = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.type_animal})"
    


class SuiviSante(models.Model):

    elevage = models.ForeignKey(
        Elevage,
        on_delete=models.CASCADE,
        related_name="sante"
    )

    maladie = models.CharField(max_length=150)
    traitement = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.maladie} - {self.elevage.nom}"


class Production(models.Model):

    TYPE_PRODUCTION = [
        ("lait", "Lait"),
        ("oeufs", "Œufs"),
        ("viande", "Viande"),
        ("poisson", "Poisson"),
    ]

    elevage = models.ForeignKey(
        Elevage,
        on_delete=models.CASCADE,
        related_name="productions"
    )

    type_production = models.CharField(
        max_length=50,
        choices=TYPE_PRODUCTION
    )

    quantite = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_production} - {self.quantite}"