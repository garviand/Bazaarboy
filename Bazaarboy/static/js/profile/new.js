(function() {
  Bazaarboy.profile["new"] = {
    map: void 0,
    marker: void 0,
    coordinates: new google.maps.LatLng(38.650068, -90.259904),
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
    init: function() {
      var googleAutocomplete, mapOptions, map_center, scope,
        _this = this;
      scope = this;
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
            $('div.profile-new-container div.next-prev a').removeClass('hide');
            if (next_step === 1) {
              $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
            }
            if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
              $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
            }
            step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title');
            $('div.profile-new-container .title .step-title').html(step_title);
          });
        });
      });
      $('div.profile-new-container div.next-prev a').click(function() {
        var active_button_container, next_active_button, next_step;
        active_button_container = $('div.profile-new-container div.profile-step-btn a.active').parent();
        if ($(this).hasClass('prev-btn')) {
          next_active_button = active_button_container.prev().find('a');
        } else {
          next_active_button = active_button_container.next().find('a');
        }
        next_step = next_active_button.data('id');
        $('div.profile-new-container div.next-prev a').removeClass('hide');
        if (next_step === 1) {
          $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
        }
        if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
          $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
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
            $('div.profile-new-container div.next-prev a').removeClass('hide');
            if (next_step === 1) {
              $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide');
            }
            if (next_step === $('div.profile-new-container div.profile-step-btn a').length) {
              $('div.profile-new-container div.next-prev a.next-btn').addClass('hide');
            }
            step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title');
            $('div.profile-new-container .title .step-title').html(step_title);
          });
        });
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
        optionals = ['email', 'phone', 'link_website', 'link_facebook', 'EIN'];
        params = Bazaarboy.stripEmpty(params, optionals);
        Bazaarboy.post('profile/create/', params, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('index');
          } else {
            alert(response.message);
          }
        });
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
