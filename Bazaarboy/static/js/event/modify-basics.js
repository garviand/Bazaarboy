(function() {
  Bazaarboy.event.modify.basics = {
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
    auto_save: function() {
      var endDate, endTime, latitude, location, longitude, name, startDate, startTime, summary,
        _this = this;
      name = $("form.event-modify input[name=name]").val();
      summary = $("form.event-modify input[name=summary]").val();
      location = $("form.event-modify input[name=location]").val();
      latitude = $("form.event-modify input[name=latitude]").val();
      longitude = $("form.event-modify input[name=longitude]").val();
      startDate = $("form.event-modify input[name=start_date]").val();
      startTime = $("form.event-modify input[name=start_time]").val();
      if (moment(startDate, 'MM/DD/YYYY').isValid() && moment(startTime, 'h:mm a').isValid()) {
        startTime = moment(startDate + ' ' + startTime, 'MM/DD/YYYY h:mm A');
      } else {
        startTime = '';
      }
      endDate = $("form.event-modify input[name=end_date]").val();
      endTime = $("form.event-modify input[name=end_time]").val();
      if (endDate.trim().length === 0 && endTime.trim().length === 0) {
        endTime = false;
      } else {
        if (!moment(endDate, 'MM/DD/YYYY').isValid()) {
          return;
        }
        if (!moment(endTime, 'h:mm a').isValid()) {
          return;
        }
        endTime = moment(endDate + ' ' + endTime, 'MM/DD/YYYY h:mm A');
      }
      Bazaarboy.event.modify.basics.save({
        id: eventId,
        start_time: startTime.utc().format('YYYY-MM-DD HH:mm:ss'),
        end_time: endTime ? endTime.utc().format('YYYY-MM-DD HH:mm:ss') : 'none',
        name: name,
        summary: summary,
        location: location,
        latitude: latitude,
        longitude: longitude
      }, function(err, event) {
        if (!err) {
          console.log(event);
        } else {
          console.log(err);
        }
      });
    },
    fetchCoordinates: function(reference) {
      var location, placesService;
      location = $('form.event-modify input[name=location]').get(0);
      placesService = new google.maps.places.PlacesService(location);
      placesService.getDetails({
        reference: reference
      }, function(result, status) {
        if (status === 'OK') {
          $('form.event-modify input[name=latitude]').val(result.geometry.location.lat());
          $('form.event-modify input[name=longitude]').val(result.geometry.location.lng());
        }
      });
    },
    init: function() {
      var googleAutocomplete, originalEndTime, originalStartTime,
        _this = this;
      setInterval(this.auto_save, 10000);
      originalStartTime = $("form.event-modify input[name=start_time]").val();
      originalEndTime = $("form.event-modify input[name=end_time]").val();
      $("form.event-modify input[name=start_time], form.event-modify input[name=end_time]").timeAutocomplete({
        blur_empty_populate: false
      });
      $("form.event-modify input[name=start_time]").val(originalStartTime);
      $("form.event-modify input[name=end_time]").val(originalEndTime);
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
      $('form.event-modify input[name=location]').keyup(function() {
        var keyword;
        keyword = $('form.event-modify input[name=location]').val();
        if (keyword.trim() !== '') {
          googleAutocomplete.getQueryPredictions({
            types: ['establishment'],
            input: keyword
          }, function(predictions, status) {
            var autocompleteSource, labelExtenstion, prediction, _i, _len;
            autocompleteSource = [];
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
              html: true
            });
            $('form.event-modify input[name=location]').on('autocompleteselect', function(event, ui) {
              _this.fetchCoordinates(ui.item.id);
            });
          });
        }
      });
    }
  };

  Bazaarboy.event.modify.basics.init();

}).call(this);
