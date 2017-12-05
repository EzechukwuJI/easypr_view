# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-09 09:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(max_length=300, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('country', models.CharField(choices=[(b'Nigeria', b'Nigeria'), (b'Ghana', b'Ghana'), (b'Kenya', b'Kenya')], max_length=20, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Address',
            },
        ),
        migrations.CreateModel(
            name='ClientFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=125)),
                ('email', models.CharField(max_length=225)),
                ('subject', models.CharField(max_length=225)),
                ('message', models.TextField(max_length=1000)),
                ('date_sent', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[(b'Open', b'Open'), (b'Closed', b'Closed'), (b'Pending', b'Pending')], default=b'Open', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='LatestNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('news_content', models.CharField(max_length=300)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=175)),
            ],
        ),
        migrations.CreateModel(
            name='PwResetRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reset_code', models.CharField(max_length=50)),
                ('expired', models.BooleanField(default=False)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[(b'Press Release Distribution', b'Press Release Distribution'), (b'Content Writing and Marketing', b'Content Marketing'), (b'Advertising', b'Advertising'), (b'SME Start Up Toolkit', b'SME Start Up Toolkit'), (b'Sales and Marketing', b'Sales and Marketing'), (b'Events Bureau', b'Events Bureau'), (b'Blogger Distribution', b'Blogger Distribution')], default=b'Press Release Distribution', max_length=175)),
                ('name_slug', models.CharField(max_length=175)),
                ('description', models.TextField(max_length=1000)),
                ('banner', models.FileField(blank=True, null=True, upload_to=b'banners/services_categories')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[(b'Press Release', b'Press Release Distribution'), (b'Photo News', b'Photo News'), (b'News Features', b'News Features'), (b'Interviews', b'Interviews'), (b'Newspapers/Magazines', b'Newspapers/Magazines'), (b'Radio Advertising', b'Radio Advertising'), (b'TV Advertising', b'TV Advertising'), (b'Scripting/Story-Boarding', b'Scripting/Story-Boarding'), (b'Audio/Visual content Production', b'Audio/Visual Content Production'), (b'Press/Release', b'Press/Release'), (b'Feature Articles', b'Feature Articles'), (b'Speeches', b'Speeches'), (b'Product Reviews', b'Product Reviews'), (b'Content Marketing', b'Content Marketing'), (b'Brand Design & Logo', b'Brand Design & Logo'), (b'Go-to-market Strategy/Consultancy', b'Go-to-market Strategy/Consultancy'), (b'Web Development', b'Web Development'), (b'Blogger Distribution', b'Blogger distribution'), (b'Social Media Influencing', b'Social Media Influencing'), (b'Social Media Ads', b'Social Media Ads'), (b'Digital Marketing Bundles', b'Digital marketing Bundles'), (b'Event Conceptualization', b'Event Conceptualization'), (b'Conference/Seminar', b'Conference/Seminar'), (b'Sponsorship Bureau', b'Sponsorship Bureau'), (b'Speaker Bureau', b'Speaker Bureau')], max_length=150)),
                ('name_slug', models.CharField(max_length=175)),
                ('image', models.FileField(blank=True, null=True, upload_to=b'item_images')),
                ('description', models.TextField(max_length=750)),
                ('call_to_action', models.CharField(blank=True, choices=[(b'Get Started', b'Get Started'), (b'Request Service', b'Request Service'), (b'Buy Now', b'Buy Now')], max_length=75, null=True)),
                ('icon_text', models.CharField(blank=True, max_length=75, null=True)),
                ('action_type', models.CharField(choices=[(b'select_service', b'select service'), (b'buy_bundle', b'buy bundle'), (b'request_service', b'request service')], default=b'', max_length=175)),
                ('active', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='easypr_general.ServiceCategory')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[(b'Mr', b'Mr'), (b'Mrs', b'Mrs'), (b'Dr', b'Dr')], default=b'', max_length=15)),
                ('account_type', models.CharField(max_length=20)),
                ('phone_no', models.CharField(max_length=15)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('economy_sector', models.CharField(max_length=75)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('profile_upto_date', models.BooleanField(default=False)),
                ('website', models.CharField(max_length=175, null=True)),
                ('brand_logo', models.ImageField(upload_to=b'Client/logo/')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('registration_code', models.CharField(max_length=50)),
                ('address', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='easypr_general.Address')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
