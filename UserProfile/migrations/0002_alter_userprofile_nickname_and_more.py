# Generated by Django 4.2.8 on 2024-07-28 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ProfilePic', '0001_initial'),
        ('UserProfile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='nickname',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profilepic_id',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ProfilePic.profilepic'),
        ),
    ]
