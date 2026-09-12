from django.db import migrations
from django.contrib.auth.hashers import make_password
import os


def create_admin_if_missing(apps, schema_editor):
    User = apps.get_model("core", "User")

    username = os.environ.get("ADMIN_USERNAME")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")

    if not username or not email or not password:
        return

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

    user.password = make_password(password)
    user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_create_admin"),
    ]

    operations = [
        migrations.RunPython(create_admin_if_missing),
    ]