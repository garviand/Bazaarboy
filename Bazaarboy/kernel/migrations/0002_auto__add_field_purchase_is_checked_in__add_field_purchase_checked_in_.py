# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Purchase.is_checked_in'
        db.add_column('kernel_purchase', 'is_checked_in',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Purchase.checked_in_time'
        db.add_column('kernel_purchase', 'checked_in_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=None, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Purchase.is_checked_in'
        db.delete_column('kernel_purchase', 'is_checked_in')

        # Deleting field 'Purchase.checked_in_time'
        db.delete_column('kernel_purchase', 'checked_in_time')


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