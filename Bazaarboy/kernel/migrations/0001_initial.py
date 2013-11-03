# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('kernel_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('email', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('password', self.gf('django.db.models.fields.CharField')(default=None, max_length=128, null=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(default=None, max_length=128, null=True)),
            ('fb_id', self.gf('django.db.models.fields.CharField')(default=None, max_length=50, unique=True, null=True)),
            ('fb_access_token', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.City'], null=True)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['User'])

        # Adding model 'User_confirmation_code'
        db.create_table('kernel_user_confirmation_code', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kernel.User'], unique=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('kernel', ['User_confirmation_code'])

        # Adding model 'User_reset_code'
        db.create_table('kernel_user_reset_code', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('is_expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('expiration_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('kernel', ['User_reset_code'])

        # Adding model 'Payment_account'
        db.create_table('kernel_payment_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('publishable_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Payment_account'])

        # Adding model 'Checkout'
        db.create_table('kernel_checkout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('payee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Payment_account'])),
            ('checkout_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('is_charged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_refunded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Checkout'])

        # Adding model 'City'
        db.create_table('kernel_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('pseudo', self.gf('django.db.models.fields.related.OneToOneField')(default=None, related_name='pseudo_community', unique=True, null=True, to=orm['kernel.Community'])),
        ))
        db.send_create_signal('kernel', ['City'])

        # Adding model 'Community'
        db.create_table('kernel_community', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.City'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('kernel', ['Community'])

        # Adding model 'User_following'
        db.create_table('kernel_user_following', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Community'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('kernel', ['User_following'])

        # Adding model 'Profile'
        db.create_table('kernel_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='profile_image', null=True, on_delete=models.SET_NULL, to=orm['kernel.Image'])),
            ('cover', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='profile_cover', null=True, on_delete=models.SET_NULL, to=orm['kernel.Image'])),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Community'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.City'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('payment_account', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Payment_account'], null=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Profile'])

        # Adding model 'Profile_manager'
        db.create_table('kernel_profile_manager', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Profile'])),
            ('is_creator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Profile_manager'])

        # Adding model 'Event'
        db.create_table('kernel_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('cover', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='event_image', null=True, on_delete=models.SET_NULL, to=orm['kernel.Image'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('is_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_launched', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='event_community', null=True, to=orm['kernel.Community'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='event_city', null=True, to=orm['kernel.City'])),
            ('access_token', self.gf('django.db.models.fields.CharField')(default=None, max_length=32, null=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal('kernel', ['Event'])

        # Adding model 'Event_organizer'
        db.create_table('kernel_event_organizer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Profile'])),
            ('is_creator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Event_organizer'])

        # Adding model 'Ticket'
        db.create_table('kernel_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('kernel', ['Ticket'])

        # Adding model 'Purchase'
        db.create_table('kernel_purchase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Ticket'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('checkout', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Checkout'], null=True)),
            ('is_expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_checked_in', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('checked_in_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Purchase'])

        # Adding model 'Fundraiser'
        db.create_table('kernel_fundraiser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('cover', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='fundraiser_image', null=True, on_delete=models.SET_NULL, to=orm['kernel.Image'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('is_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_launched', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='fundraiser_community', null=True, to=orm['kernel.Community'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='fundraiser_city', null=True, to=orm['kernel.City'])),
            ('access_token', self.gf('django.db.models.fields.CharField')(default=None, max_length=32, null=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('goal', self.gf('django.db.models.fields.FloatField')()),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('kernel', ['Fundraiser'])

        # Adding model 'Fundraiser_organizer'
        db.create_table('kernel_fundraiser_organizer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fundraiser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Profile'])),
            ('is_creator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Fundraiser_organizer'])

        # Adding model 'Reward'
        db.create_table('kernel_reward', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fundraiser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal('kernel', ['Reward'])

        # Adding model 'Donation'
        db.create_table('kernel_donation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
            ('reward', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Reward'])),
            ('fundraiser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('checkout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Checkout'])),
            ('is_expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Donation'])

        # Adding model 'Event_criteria'
        db.create_table('kernel_event_criteria', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
        ))
        db.send_create_signal('kernel', ['Event_criteria'])

        # Adding model 'Fundraiser_criteria'
        db.create_table('kernel_fundraiser_criteria', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
        ))
        db.send_create_signal('kernel', ['Fundraiser_criteria'])

        # Adding model 'Event_sponsorship'
        db.create_table('kernel_event_sponsorship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_sponsorship_profile', to=orm['kernel.Profile'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('checkout_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_captured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_refunded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('criteria', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event_criteria'])),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
        ))
        db.send_create_signal('kernel', ['Event_sponsorship'])

        # Adding model 'Fundraiser_sponsorship'
        db.create_table('kernel_fundraiser_sponsorship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fundraiser_sponsorship_profile', to=orm['kernel.Profile'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('checkout_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_captured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_refunded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('criteria', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser_criteria'])),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
        ))
        db.send_create_signal('kernel', ['Fundraiser_sponsorship'])

        # Adding model 'Event_sponsorship_display'
        db.create_table('kernel_event_sponsorship_display', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=50, null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default=None, max_length=150, null=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Image'], null=True)),
            ('sponsor', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Profile'], null=True)),
            ('sponsorship', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Event_sponsorship'], null=True)),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Event'])),
        ))
        db.send_create_signal('kernel', ['Event_sponsorship_display'])

        # Adding model 'Fundraiser_sponsorship_display'
        db.create_table('kernel_fundraiser_sponsorship_display', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=50, null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default=None, max_length=150, null=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Image'], null=True)),
            ('sponsor', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Profile'], null=True)),
            ('sponsorship', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Fundraiser_sponsorship'], null=True)),
            ('_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Fundraiser'])),
        ))
        db.send_create_signal('kernel', ['Fundraiser_sponsorship_display'])

        # Adding model 'Image'
        db.create_table('kernel_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('is_archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['Image'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('kernel_user')

        # Deleting model 'User_confirmation_code'
        db.delete_table('kernel_user_confirmation_code')

        # Deleting model 'User_reset_code'
        db.delete_table('kernel_user_reset_code')

        # Deleting model 'Payment_account'
        db.delete_table('kernel_payment_account')

        # Deleting model 'Checkout'
        db.delete_table('kernel_checkout')

        # Deleting model 'City'
        db.delete_table('kernel_city')

        # Deleting model 'Community'
        db.delete_table('kernel_community')

        # Deleting model 'User_following'
        db.delete_table('kernel_user_following')

        # Deleting model 'Profile'
        db.delete_table('kernel_profile')

        # Deleting model 'Profile_manager'
        db.delete_table('kernel_profile_manager')

        # Deleting model 'Event'
        db.delete_table('kernel_event')

        # Deleting model 'Event_organizer'
        db.delete_table('kernel_event_organizer')

        # Deleting model 'Ticket'
        db.delete_table('kernel_ticket')

        # Deleting model 'Purchase'
        db.delete_table('kernel_purchase')

        # Deleting model 'Fundraiser'
        db.delete_table('kernel_fundraiser')

        # Deleting model 'Fundraiser_organizer'
        db.delete_table('kernel_fundraiser_organizer')

        # Deleting model 'Reward'
        db.delete_table('kernel_reward')

        # Deleting model 'Donation'
        db.delete_table('kernel_donation')

        # Deleting model 'Event_criteria'
        db.delete_table('kernel_event_criteria')

        # Deleting model 'Fundraiser_criteria'
        db.delete_table('kernel_fundraiser_criteria')

        # Deleting model 'Event_sponsorship'
        db.delete_table('kernel_event_sponsorship')

        # Deleting model 'Fundraiser_sponsorship'
        db.delete_table('kernel_fundraiser_sponsorship')

        # Deleting model 'Event_sponsorship_display'
        db.delete_table('kernel_event_sponsorship_display')

        # Deleting model 'Fundraiser_sponsorship_display'
        db.delete_table('kernel_fundraiser_sponsorship_display')

        # Deleting model 'Image'
        db.delete_table('kernel_image')


    models = {
        'kernel.checkout': {
            'Meta': {'object_name': 'Checkout'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'checkout_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_charged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_refunded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'payee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Payment_account']"}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"})
        },
        'kernel.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pseudo': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'related_name': "'pseudo_community'", 'unique': 'True', 'null': 'True', 'to': "orm['kernel.Community']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'kernel.community': {
            'Meta': {'object_name': 'Community'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.City']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'kernel.donation': {
            'Meta': {'object_name': 'Donation'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'checkout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Checkout']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fundraiser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"}),
            'reward': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Reward']"})
        },
        'kernel.event': {
            'Meta': {'object_name': 'Event'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '32', 'null': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'event_city'", 'null': 'True', 'to': "orm['kernel.City']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'event_community'", 'null': 'True', 'to': "orm['kernel.Community']"}),
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'event_image'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['kernel.Image']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_launched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kernel.Profile']", 'through': "orm['kernel.Event_organizer']", 'symmetrical': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'kernel.event_criteria': {
            'Meta': {'object_name': 'Event_criteria'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        'kernel.event_organizer': {
            'Meta': {'object_name': 'Event_organizer'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_creator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Profile']"})
        },
        'kernel.event_sponsorship': {
            'Meta': {'object_name': 'Event_sponsorship'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'checkout_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event_criteria']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_captured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_refunded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_sponsorship_profile'", 'to': "orm['kernel.Profile']"})
        },
        'kernel.event_sponsorship_display': {
            'Meta': {'object_name': 'Event_sponsorship_display'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '150', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Image']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'null': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Profile']", 'null': 'True'}),
            'sponsorship': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Event_sponsorship']", 'null': 'True'})
        },
        'kernel.fundraiser': {
            'Meta': {'object_name': 'Fundraiser'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '32', 'null': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'fundraiser_city'", 'null': 'True', 'to': "orm['kernel.City']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'fundraiser_community'", 'null': 'True', 'to': "orm['kernel.Community']"}),
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'fundraiser_image'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['kernel.Image']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'goal': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_launched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kernel.Profile']", 'through': "orm['kernel.Fundraiser_organizer']", 'symmetrical': 'False'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'kernel.fundraiser_criteria': {
            'Meta': {'object_name': 'Fundraiser_criteria'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        'kernel.fundraiser_organizer': {
            'Meta': {'object_name': 'Fundraiser_organizer'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fundraiser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_creator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Profile']"})
        },
        'kernel.fundraiser_sponsorship': {
            'Meta': {'object_name': 'Fundraiser_sponsorship'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'checkout_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser_criteria']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_captured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_refunded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fundraiser_sponsorship_profile'", 'to': "orm['kernel.Profile']"})
        },
        'kernel.fundraiser_sponsorship_display': {
            'Meta': {'object_name': 'Fundraiser_sponsorship_display'},
            '_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '150', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Image']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'null': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Profile']", 'null': 'True'}),
            'sponsorship': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Fundraiser_sponsorship']", 'null': 'True'})
        },
        'kernel.image': {
            'Meta': {'object_name': 'Image'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'kernel.payment_account': {
            'Meta': {'object_name': 'Payment_account'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"}),
            'publishable_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kernel.profile': {
            'Meta': {'object_name': 'Profile'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.City']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Community']"}),
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'profile_cover'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['kernel.Image']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'profile_image'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['kernel.Image']"}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kernel.User']", 'through': "orm['kernel.Profile_manager']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'payment_account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Payment_account']", 'null': 'True'})
        },
        'kernel.profile_manager': {
            'Meta': {'object_name': 'Profile_manager'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_creator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Profile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"})
        },
        'kernel.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'checked_in_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'checkout': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Checkout']", 'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_checked_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Ticket']"})
        },
        'kernel.reward': {
            'Meta': {'object_name': 'Reward'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'fundraiser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Fundraiser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        'kernel.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'kernel.user': {
            'Meta': {'object_name': 'User'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.City']", 'null': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'fb_access_token': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'following': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kernel.Community']", 'through': "orm['kernel.User_following']", 'symmetrical': 'False'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'salt': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'})
        },
        'kernel.user_confirmation_code': {
            'Meta': {'object_name': 'User_confirmation_code'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kernel.User']", 'unique': 'True'})
        },
        'kernel.user_following': {
            'Meta': {'object_name': 'User_following'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Community']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"})
        },
        'kernel.user_reset_code': {
            'Meta': {'object_name': 'User_reset_code'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'expiration_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"})
        }
    }

    complete_apps = ['kernel']