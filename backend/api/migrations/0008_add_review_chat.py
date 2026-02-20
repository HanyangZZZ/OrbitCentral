# Generated manually for ReviewChat model

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_review_unique_review_per_user_per_business_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewChat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rating', models.IntegerField(help_text='Star rating the user chose before starting the chat (1-5)')),
                ('messages', models.JSONField(default=list, help_text='Full conversation history [{role, content}, ...]')),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('abandoned', 'Abandoned')], default='active', max_length=12)),
                ('tags_to_add', models.JSONField(blank=True, default=list, help_text='Tag names the AI wants to ADD to the business')),
                ('tags_to_remove', models.JSONField(blank=True, default=list, help_text='Tag names the AI wants to REMOVE from the business')),
                ('generated_description', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_chats', to='api.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_chats', to=settings.AUTH_USER_MODEL)),
                ('review', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_session', to='api.review')),
            ],
            options={
                'db_table': 'review_chats',
                'ordering': ['-created_at'],
            },
        ),
    ]
