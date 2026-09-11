from django.db import migrations
import os


def create_admin(apps, schema_editor):
    User = apps.get_model("core", "User")

    username = os.environ.get("ADMIN_USERNAME")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")

    # Si les variables ne sont pas définies, on ne fait rien
    if not username or not email or not password:
        return

    # Évite de créer deux fois le même compte
    if User.objects.filter(username=username).exists():
        return

    user = User(
        username=username,
        email=email,
        role="admin",
        is_staff=True,
        is_superuser=True,
        is_verified=True,
        is_active=True,
    )

    user.set_password(password)
    user.save()


def remove_admin(apps, schema_editor):
    User = apps.get_model("core", "User")

    username = os.environ.get("ADMIN_USERNAME")

    if username:
        User.objects.filter(username=username).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_user_is_suspended"),
    ]

    operations = [
        migrations.RunPython(create_admin, remove_admin),
    ]