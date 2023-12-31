# Generated by Django 4.2.4 on 2023-09-08 15:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='NormalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('adhar_id', models.CharField(max_length=10, unique=True)),
                ('contact_number', models.CharField(max_length=12)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blogs',
            fields=[
                ('blog_number', models.AutoField(primary_key=True, serialize=False)),
                ('blog_image', models.ImageField(upload_to='blog_images')),
                ('blog_descripton', models.TextField()),
                ('blog_date', models.DateField(auto_now_add=True)),
                ('is_vote', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='VoteReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.CharField(choices=[('STRONGLY_SUPPORT', 'Strongly Support'), ('SUPPORT', 'Support'), ('MODERATE', 'Moderate'), ('DISAGREE', 'Disagree'), ('STRONGLY_DISAGREE', 'Strongly Disagree')], max_length=50)),
                ('voted_date', models.DateField(auto_now=True)),
                ('blog_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vote_reactions', to='api.blogs')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GovBodyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('LOCAL', 'Local'), ('DISTRICT', 'District'), ('STATE', 'State')], max_length=20)),
                ('email', models.EmailField(error_messages={'unique': 'A user with the same email already exists.'}, max_length=254, unique=True)),
                ('gov_body_name', models.CharField(max_length=50)),
                ('contact_number', models.CharField(max_length=12)),
                ('groups', models.ManyToManyField(blank=True, related_name='gov_body_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='gov_body_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GovBodyAddress',
            fields=[
                ('address_id', models.AutoField(primary_key=True, serialize=False)),
                ('locality', models.CharField(max_length=20)),
                ('district', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=20)),
                ('country', models.CharField(default='INDIA', max_length=20)),
                ('gov_body', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.govbodyuser')),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_text', models.TextField()),
                ('comment_date', models.DateField(auto_now=True)),
                ('blog_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_set', to='api.blogs')),
                ('commenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replay_set', to='api.comments')),
            ],
            options={
                'ordering': ['comment_date'],
            },
        ),
        migrations.AddField(
            model_name='blogs',
            name='blogger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.govbodyuser'),
        ),
        migrations.CreateModel(
            name='BlogReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.BooleanField(default=True)),
                ('like_date', models.DateField(auto_now=True)),
                ('blog_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_reactions', to='api.blogs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
