(function() {
  Bazaarboy.event.modify.basics = {
    isEditing: false,
    map: void 0,
    marker: void 0,
    autoSaveTimer: void 0,
    save: function(params, cb) {
      if (typeof token !== "undefined" && token !== null) {
        params.token = token;
      }
      Bazaarboy.post('event/edit/', params, function(response) {
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
    saveBasics: function(autoSave) {
      var end_time, save_data, start_time,
        _this = this;
      save_data = $('form.event-modify').serializeObject();
      if (save_data.name.length > 150) {
        console.log('Name is too long.');
      }
      if (save_data.summary.length > 250) {
        console.log('Summary is too long.');
      }
      save_data.slug = save_data.slug.trim();
      if (save_data.slug.length > 0) {
        if (!/^[A-Za-z0-9-]{1,30}$/.test(save_data.slug)) {
          console.log('Invalid slug');
        }
      } else {
        save_data.slug = 'None';
      }
      if (save_data.start_date.trim().length !== 0 && save_data.start_time.trim().length !== 0 && moment(save_data.start_date, 'MM/DD/YYYY').isValid() && moment(save_data.start_time, 'h:mm A').isValid()) {
        start_time = moment(save_data.start_date + ' ' + save_data.start_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss');
      } else {
        start_time = '';
        $('div#event-modify-basics div.status').html('Start Time is Invalid');
        return;
      }
      if (save_data.end_date.trim().length === 0 || save_data.end_time.trim().length === 0) {
        end_time = false;
      } else {
        if (!moment(save_data.end_date, 'MM/DD/YYYY').isValid()) {
          $('div#event-modify-basics div.status').html('End Time is Invalid');
          return;
        }
        if (!moment(save_data.end_time, 'h:mm A').isValid()) {
          $('div#event-modify-basics div.status').html('End Time is Invalid');
          return;
        }
        end_time = moment(save_data.end_date + ' ' + save_data.end_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss');
      }
      $('div#event-modify-basics div.status').html('Saving...');
      this.save({
        id: eventId,
        start_time: start_time,
        end_time: end_time ? end_time : 'none',
        name: save_data.name,
        summary: save_data.summary,
        location: save_data.location,
        latitude: save_data.latitude,
        longitude: save_data.longitude,
        slug: save_data.slug
      }, function(err, event) {
        if (!err) {
          setTimeout((function() {
            $('div#event-modify-basics div.status').html('Saved');
          }), 1000);
          if (!autoSave) {
            window.location = '/event/' + eventId + '/tickets';
          }
        } else {
          if (err.error === 'DUPLICATE_SLUG' && !autoSave) {
            $('div#event-modify-basics span.optional').addClass('hide');
            $('div#event-modify-basics span.taken').removeClass('hide');
            $('html, body').animate({
              scrollTop: $('div#event-modify-basics span.taken').offset().top - 100
            }, 1000);
            setTimeout((function() {
              $('div#event-modify-basics span.taken').addClass('hide');
              $('div#event-modify-basics span.optional').removeClass('hide');
            }), 4000);
          } else {
            $('div#event-modify-basics div.status').html(err.message);
            console.log(err);
          }
        }
      });
    },
    autoSave: function() {
      if (!this.isEditing) {
        this.saveBasics(true);
      }
    },
    fetchCoordinates: function(reference) {
      var gmap, location, placesService,
        _this = this;
      gmap = $('div#map-canvas-hidden').get(0);
      location = $('form.event-modify input[name=location]').val();
      placesService = new google.maps.places.PlacesService(gmap);
      placesService.getDetails({
        reference: reference
      }, function(result, status) {
        var center;
        if (status === 'OK') {
          $('form.event-modify input[name=latitude]').val(result.geometry.location.lat());
          $('form.event-modify input[name=longitude]').val(result.geometry.location.lng());
          center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng());
          _this.map.panTo(center);
          _this.marker.setPosition(center);
        }
      });
    },
    init: function() {
      var googleAutocomplete, initial_lat, initial_lng, mapOptions, mapStyles, map_center, originalEndTime, originalStartTime,
        _this = this;
      $('div.input-container').click(function() {
        $(this).find('input, textarea').focus();
      });
      $('div.input-container input,div.input-container textarea').focus(function() {
        $(this).closest('div.input-container').addClass('active');
      });
      $('div.input-container input,div.input-container textarea').blur(function() {
        $(this).closest('div.input-container').removeClass('active');
      });
      $('form.event-modify').submit(function(e) {
        e.preventDefault();
        _this.saveBasics(false);
      });
      initial_lat = $('form.event-modify input[name=latitude]').val();
      initial_lng = $('form.event-modify input[name=longitude]').val();
      if (initial_lat !== 'None' && initial_lng !== 'None') {
        map_center = new google.maps.LatLng(initial_lat, initial_lng);
      } else {
        map_center = new google.maps.LatLng(38.650068, -90.259904);
      }
      mapStyles = [
        {
          featureType: "poi",
          elementType: "labels",
          stylers: [
            {
              visibility: "off"
            }
          ]
        }
      ];
      mapOptions = {
        zoom: 15,
        center: map_center,
        mapTypeControl: false,
        scaleControl: false,
        scrollWheel: false,
        streetViewControl: false,
        styles: mapStyles
      };
      this.map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
      this.marker = new google.maps.Marker({
        position: map_center,
        map: this.map,
        draggable: true
      });
      google.maps.event.addListener(this.marker, 'drag', function() {
        $('form.event-modify input[name=latitude]').val(_this.marker.position.lat());
        $('form.event-modify input[name=longitude]').val(_this.marker.position.lng());
      });
      $('form.event-modify').find('input, textarea').keyup(function() {
        _this.isEditing = true;
        clearTimeout(_this.autoSaveTimer);
        $('div#event-modify-basics div.status').html('Unsaved Changes');
        _this.autoSaveTimer = setTimeout((function() {
          _this.isEditing = false;
        }), 5000);
      });
      setInterval((function() {
        _this.autoSave();
      }), 10000);
      originalStartTime = $('form.event-modify input[name=start_time]').val();
      originalEndTime = $('form.event-modify input[name=end_time]').val();
      $('form.event-modify input[name=start_time], form.event-modify input[name=end_time]').timeAutocomplete({
        blur_empty_populate: false,
        appendTo: '#menu-container'
      });
      $('form.event-modify input[name=start_time]').val(originalStartTime);
      $('form.event-modify input[name=end_time]').val(originalEndTime);
      $('form.event-modify input[name=start_date]').pikaday({
        format: 'MM/DD/YYYY',
        onSelect: function() {
          $('form.event-modify input[name=end_date]').pikaday('gotoDate', this.getDate());
          $('form.event-modify input[name=end_date]').pikaday('setMinDate', this.getDate());
        }
      });
      $('form.event-modify input[name=end_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
      googleAutocomplete = new google.maps.places.AutocompleteService();
      $('form.event-modify input[name=location]').keypress(function() {
        var keyword;
        keyword = $('form.event-modify input[name=location]').val();
        if (keyword.trim() !== '') {
          googleAutocomplete.getQueryPredictions({
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
              $('form.event-modify input[name=location]').autocomplete({
                source: autocompleteSource,
                html: true,
                matchContains: true,
                minLength: 0
              });
              $('form.event-modify input[name=location]').autocomplete("search", "");
              $('form.event-modify input[name=location]').on('autocompleteselect', function(event, ui) {
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
