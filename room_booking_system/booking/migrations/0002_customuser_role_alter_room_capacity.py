# Generated by Django 5.2.3 on 2025-06-16 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=10),
        ),
        migrations.AlterField(
            model_name='room',
            name='capacity',
            field=models.PositiveIntegerField(default=10, verbose_name='Capacity'),
        ),
    ]
