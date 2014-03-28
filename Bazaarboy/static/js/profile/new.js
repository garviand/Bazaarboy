(function() {
  Bazaarboy.profile["new"] = {
    map: void 0,
    marker: void 0,
    coordinates: new google.maps.LatLng(38.650068, -90.259904),
    image: void 0,
    uploads: {
      image: void 0
    },
    fetchCoordinates: function(reference) {
      var gmap, location, placesService,
        _this = this;
      gmap = $('div#map-canvas-hidden').get(0);
      location = $('form.profile-new input[name=location]').val();
      placesService = new google.maps.places.PlacesService(gmap);
      placesService.getDetails({
        reference: reference
      }, function(result, status) {
        var center;
        if (status === 'OK') {
          $('form.profile-new input[name=latitude]').val(result.geometry.location.lat());
          $('form.profile-new input[name=longitude]').val(result.geometry.location.lng());
          center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng());
          _this.coordinates = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng());
          _this.map.panTo(center);
          _this.marker.setPosition(center);
        }
      });
    },
    startEditingLogoImage: function() {
      var scope;
      scope = this;
      $('<img>').attr('src', mediaUrl + this.uploads.image.source).load(function() {
        $('div.profile-new-container div.logo div.logo_image').html('');
        $('div.profile-new-container div.logo div.logo_image').append(this);
        $('div.profile-new-container div.logo a.upload').addClass('hide');
        $('div.profile-new-container div.logo a.cancel').removeClass('hide');
      });
    },
    stopEditingLogoImage: function() {
      this.uploads.image = void 0;
      this.image = void 0;
      $('div.profile-new-container div.logo div.logo_image').html('');
      $('div.profile-new-container div.logo a.upload').removeClass('hide');
      $('div.profile-new-container div.logo a.cancel').addClass('hide');
    },
    init: function() {
      var googleAutocomplete, mapOptions, map_center, scope,
        _this = this;
      scope = this;
      $('div.profile-new-container div.logo a.upload').click(function() {
        $('div#wrapper-profile-new form.upload_logo input[name=image_file]').click();
      });
      $('div.profile-new-container div.logo a.cancel').click(function() {
        scope.stopEditingLogoImage();
      });
      $('div#wrapper-profile-new form.upload_logo input[name=image_file]').fileupload({
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
      $('div.profile-new-container div.profile-step-btn a').click(function() {
        var next_step;
        $('div.profile-new-container div.profile-step-btn a').removeClass('active');
        $(this).addClass('active');
        next_step = $(this).data('id');
        $('div.profile-new-container div.profile-step.active').fadeOut(300, function() {
          $('div.profile-new-container .title .step-title').html('');
          $(this).removeClass('active');
          $('div.profile-new-container div.profile-step-' + next_step).addClass('active');
          $('div.profile-new-container div.profile-step-' + next_step).fadeIn(300, function() {
            var step_title;
            google.maps.event.trigger(scope.map, 'resize');
            scope.map.setCenter(scope.coordinates);
            $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide');
            if (next_step === 1) {
              $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
            }
            if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
              $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
              $('div.profile-new-container div.next-prev a.finish-btn').removeClass('hide');
            } else {
              $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide');
            }
            step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title');
            $('div.profile-new-container .title .step-title').html(step_title);
          });
        });
      });
      $('div.profile-new-container div.next-prev a').not('.finish-btn').click(function() {
        var active_button_container, next_active_button, next_step;
        active_button_container = $('div.profile-new-container div.profile-step-btn a.active').parent();
        if ($(this).hasClass('prev-btn')) {
          next_active_button = active_button_container.prev().find('a');
        } else {
          next_active_button = active_button_container.next().find('a');
        }
        next_step = next_active_button.data('id');
        $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide');
        if (next_step === 1) {
          $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
        }
        if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
          $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
        } else {
          $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide');
        }
        next_active_button.addClass('active');
        $('div.profile-new-container div.profile-step-btn a').removeClass('active');
        next_active_button.addClass('active');
        $('div.profile-new-container div.profile-step.active').fadeOut(300, function() {
          $('div.profile-new-container .title .step-title').html('');
          $(this).removeClass('active');
          $('div.profile-new-container div.profile-step-' + next_step).addClass('active');
          $('div.profile-new-container div.profile-step-' + next_step).fadeIn(300, function() {
            var step_title;
            google.maps.event.trigger(scope.map, 'resize');
            scope.map.setCenter(scope.coordinates);
            $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide');
            if (next_step === 1) {
              $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
            }
            if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
              $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
              $('div.profile-new-container div.next-prev a.finish-btn').removeClass('hide');
            } else {
              $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide');
            }
            step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title');
            $('div.profile-new-container .title .step-title').html(step_title);
          });
        });
      });
      $('div.profile-new-container div.next-prev .finish-btn').click(function() {
        $('form.profile-new').submit();
      });
      $('div.profile-new-container input[name=is_non_profit]').change(function() {
        if ($(this).is(":checked")) {
          $('div.profile-new-container .ein').removeClass('hide');
        } else {
          $('div.profile-new-container .ein').addClass('hide');
        }
      });
      map_center = this.coordinates;
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
        $('form.profile-new input[name=latitude]').val(_this.marker.position.lat());
        $('form.profile-new input[name=longitude]').val(_this.marker.position.lng());
        _this.coordinates = new google.maps.LatLng(_this.marker.position.lat(), _this.marker.position.lng());
      });
      $('form.profile-new').submit(function(event) {
        var optionals, params;
        event.preventDefault();
        params = $(this).serializeObject();
        optionals = ['email', 'phone', 'link_website', 'link_facebook', 'EIN', 'latitude', 'longitude'];
        console.log(params);
        params = Bazaarboy.stripEmpty(params, optionals);
        if (typeof scope.uploads.image !== 'undefined') {
          params.image = scope.uploads.image.pk;
        }
        console.log(params);
      });
      googleAutocomplete = new google.maps.places.AutocompleteService();
      $('form.profile-new input[name=location]').keyup(function() {
        var keyword;
        keyword = $('form.profile-new input[name=location]').val();
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
              $('form.profile-new input[name=location]').autocomplete({
                source: autocompleteSource,
                html: true
              });
              $('form.profile-new input[name=location]').on('autocompleteselect', function(event, ui) {
                _this.fetchCoordinates(ui.item.id);
              });
            }
          });
        }
      });
    }
  };

  Bazaarboy.profile["new"].init();

}).call(this);
