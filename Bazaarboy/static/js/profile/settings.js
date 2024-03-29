(function() {
  Bazaarboy.event.modify.basics = {
    isEditing: false,
    map: void 0,
    marker: void 0,
    image: void 0,
    uploads: {
      image: void 0
    },
    save: function(params, cb) {
      if (typeof token !== "undefined" && token !== null) {
        params.token = token;
      }
      Bazaarboy.post('profile/edit/', params, function(response) {
        var err;
        if (response.status === 'OK') {
          return cb(null, response.event);
        } else {
          err = {
            error: response.error,
            message: response.message
          };
          return cb(err, null);
        }
      });
    },
    saveSettings: function(autoSave) {
      var save_data,
        _this = this;
      save_data = $('form.profile-settings').serializeObject();
      if (save_data.name.length > 100) {
        console.log('Name is too long.');
      }
      $('div#profile-settings div.status').html('Saving...');
      this.save({
        id: profileId,
        name: save_data.name,
        description: save_data.description,
        location: save_data.location,
        latitude: save_data.latitude,
        longitude: save_data.longitude
      }, function(err, event) {
        if (!err) {
          setTimeout((function() {
            $('div#profile-settings div.status').html('Saved');
          }), 1000);
        } else {
          $('div#profile-settings div.status').html('Failed to save');
          console.log(err);
        }
      });
    },
    autoSave: function() {
      if (!this.isEditing) {
        this.saveSettings(true);
      }
    },
    fetchCoordinates: function(reference) {
      var gmap, location, placesService,
        _this = this;
      gmap = $('div#map-canvas-hidden').get(0);
      location = $('form.profile-settings input[name=location]').val();
      placesService = new google.maps.places.PlacesService(gmap);
      placesService.getDetails({
        reference: reference
      }, function(result, status) {
        var center;
        if (status === 'OK') {
          $('form.profile-settings input[name=latitude]').val(result.geometry.location.lat());
          $('form.profile-settings input[name=longitude]').val(result.geometry.location.lng());
          center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng());
          _this.map.panTo(center);
          _this.marker.setPosition(center);
        }
      });
    },
    startEditingLogoImage: function() {
      var scope;
      scope = this;
      $('<img>').attr('src', mediaUrl + this.uploads.image.source).load(function() {
        $('div#profile-settings div.logo div.logo_image').html('');
        $('div#profile-settings div.logo div.logo_image').append(this);
        $('div#profile-settings div.logo a.upload').addClass('hide');
        $('div#profile-settings div.logo a.delete').addClass('hide');
        $('div#profile-settings div.logo a.save').removeClass('hide');
        $('div#profile-settings div.logo a.cancel').removeClass('hide');
      });
    },
    stopEditingLogoImage: function() {
      $('div#profile-settings div.logo a.upload').removeClass('hide');
      $('div#profile-settings div.logo a.delete').removeClass('hide');
      $('div#profile-settings div.logo a.save').addClass('hide');
      $('div#profile-settings div.logo a.cancel').addClass('hide');
    },
    saveLogoImage: function() {
      var _this = this;
      this.save({
        image: this.uploads.image.pk,
        id: profileId
      }, function(err, profile) {
        if (!err) {
          _this.uploads.image = null;
          _this.stopEditingLogoImage();
        } else {
          alert(err.message);
        }
      });
    },
    deleteLogoImage: function() {
      var _this = this;
      if (confirm('Are you sure you want to delete the logo?')) {
        this.save({
          image: 'delete',
          id: profileId
        }, function(err, profile) {
          if (!err) {
            _this.image = null;
            $('div#profile-settings div.logo div.logo_image').html('');
          } else {
            alert(err.message);
          }
        });
      }
    },
    init: function() {
      var googleAutocomplete, initial_lat, initial_lng, mapOptions, map_center,
        _this = this;
      $('div#profile-settings div.logo a.upload').click(function() {
        $('div#profile-settings form.upload_logo input[name=image_file]').click();
      });
      $('div#profile-settings div.logo a.delete').click(function() {
        _this.deleteLogoImage();
      });
      $('div#profile-settings div.logo a.save').click(function() {
        _this.saveLogoImage();
      });
      $('div#profile-settings div.logo div.logo a.cancel').click(function() {});
      $('div#profile-settings form.upload_logo input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            if (_this.uploads.image != null) {
              Bazaarboy.post('file/image/delete/', {
                id: _this.uploads.image.pk
              });
            }
            _this.uploads.image = response.image;
            _this.startEditingLogoImage();
          } else {
            alert(response.message);
          }
        }
      });
      $('form.profile-settings').submit(function(e) {
        e.preventDefault();
        _this.saveSettings(false);
      });
      initial_lat = $('form.profile-settings input[name=latitude]').val();
      initial_lng = $('form.profile-settings input[name=longitude]').val();
      if (initial_lat !== 'None' && initial_lng !== 'None') {
        map_center = new google.maps.LatLng(initial_lat, initial_lng);
      } else {
        map_center = new google.maps.LatLng(38.650068, -90.259904);
      }
      mapOptions = {
        zoom: 15,
        center: map_center
      };
      this.map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
      this.marker = new google.maps.Marker({
        position: map_center,
        map: this.map,
        draggable: true
      });
      google.maps.event.addListener(this.marker, 'drag', function() {
        $('form.profile-settings input[name=latitude]').val(_this.marker.position.lat());
        $('form.profile-settings input[name=longitude]').val(_this.marker.position.lng());
        $('div#profile-settings div.status').html('Editing');
      });
      $('form.profile-settings').find('input, textarea').keyup(function() {
        _this.isEditing = true;
        $('div#profile-settings div.status').html('Editing');
        setTimeout((function() {
          _this.isEditing = false;
        }), 5000);
      });
      setInterval((function() {
        _this.autoSave();
      }), 10000);
      googleAutocomplete = new google.maps.places.AutocompleteService();
      $('form.profile-settings input[name=location]').keyup(function() {
        var keyword;
        keyword = $('form.profile-settings input[name=location]').val();
        if (keyword.trim() !== '') {
          googleAutocomplete.getQueryPredictions({
            types: ['establishment'],
            input: keyword
          }, function(predictions, status) {
            var autocompleteSource, labelExtenstion, prediction, _i, _len;
            autocompleteSource = [];
            if (predictions && predictions.length > 0) {
              for (_i = 0, _len = predictions.length; _i < _len; _i++) {
                prediction = predictions[_i];
                if (prediction['terms'].length > 2) {
                  labelExtenstion = ' - <i>' + prediction['terms'][2]['value'] + '</i>';
                } else {
                  labelExtenstion = '';
                }
                autocompleteSource.push({
                  id: prediction['reference'],
                  value: prediction['terms'][0]['value'],
                  label: prediction['terms'][0]['value'] + labelExtenstion
                });
              }
              $('form.profile-settings input[name=location]').autocomplete({
                source: autocompleteSource,
                html: true
              });
              $('form.profile-settings input[name=location]').on('autocompleteselect', function(event, ui) {
                _this.fetchCoordinates(ui.item.id);
              });
            }
          });
        }
      });
    }
  };

  Bazaarboy.event.modify.basics.init();

}).call(this);
