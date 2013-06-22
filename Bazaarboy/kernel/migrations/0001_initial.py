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
            ('email', self.gf('django.db.models.fields.CharField')(default=None, max_length=50, unique=True, null=True)),
            ('password', self.gf('django.db.models.fields.CharField')(default=None, max_length=128, null=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(default=None, max_length=128, null=True)),
            ('fb_id', self.gf('django.db.models.fields.CharField')(default=None, max_length=50, unique=True, null=True)),
            ('fb_token', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.City'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('kernel', ['User'])

        # Adding model 'Wepay_account'
        db.create_table('kernel_wepay_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('account_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.User'])),
        ))
        db.send_create_signal('kernel', ['Wepay_account'])

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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.City'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('kernel', ['Community'])

        # Adding model 'Profile'
        db.create_table('kernel_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='profile', to=orm['kernel.Community'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.City'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('wepay_account', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['kernel.Wepay_account'], null=True)),
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

        # Adding model 'Event_base'
        db.create_table('kernel_event_base', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=None, null=True)),
            ('is_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_launched', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Profile'])),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_base_community', to=orm['kernel.Community'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_base_city', to=orm['kernel.City'])),
        ))
        db.send_create_signal('kernel', ['Event_base'])

        # Adding model 'Event'
        db.create_table('kernel_event', (
            ('event_base_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kernel.Event_base'], unique=True, primary_key=True)),
            ('is_repeated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('kernel', ['Event'])

        # Adding model 'Initiative'
        db.create_table('kernel_initiative', (
            ('event_base_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kernel.Event_base'], unique=True, primary_key=True)),
            ('goal', self.gf('django.db.models.fields.FloatField')()),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_reached', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('kernel', ['Initiative'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('kernel_user')

        # Deleting model 'Wepay_account'
        db.delete_table('kernel_wepay_account')

        # Deleting model 'City'
        db.delete_table('kernel_city')

        # Deleting model 'Community'
        db.delete_table('kernel_community')

        # Deleting model 'Profile'
        db.delete_table('kernel_profile')

        # Deleting model 'Profile_manager'
        db.delete_table('kernel_profile_manager')

        # Deleting model 'Event_base'
        db.delete_table('kernel_event_base')

        # Deleting model 'Event'
        db.delete_table('kernel_event')

        # Deleting model 'Initiative'
        db.delete_table('kernel_initiative')


    models = {
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kernel.event': {
            'Meta': {'object_name': 'Event', '_ormbases': ['kernel.Event_base']},
            'event_base_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kernel.Event_base']", 'unique': 'True', 'primary_key': 'True'}),
            'is_repeated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'kernel.event_base': {
            'Meta': {'object_name': 'Event_base'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_base_city'", 'to': "orm['kernel.City']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_base_community'", 'to': "orm['kernel.Community']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_launched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Profile']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'kernel.initiative': {
            'Meta': {'object_name': 'Initiative', '_ormbases': ['kernel.Event_base']},
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'event_base_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kernel.Event_base']", 'unique': 'True', 'primary_key': 'True'}),
            'goal': ('django.db.models.fields.FloatField', [], {}),
            'is_reached': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'kernel.profile': {
            'Meta': {'object_name': 'Profile'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.City']"}),
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile'", 'to': "orm['kernel.Community']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kernel.User']", 'through': "orm['kernel.Profile_manager']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'wepay_account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['kernel.Wepay_account']", 'null': 'True'})
        },
        'kernel.profile_manager': {
            'Meta': {'object_name': 'Profile_manager'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_creator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.Profile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"})
        },
        'kernel.user': {
            'Meta': {'object_name': 'User'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.City']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'fb_token': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'})
        },
        'kernel.wepay_account': {
            'Meta': {'object_name': 'Wepay_account'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'account_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kernel.User']"}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['kernel']