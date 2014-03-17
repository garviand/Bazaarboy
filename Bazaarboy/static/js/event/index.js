(function() {
  Bazaarboy.event.index = {
    savingInProgress: false,
    saveDescription: function() {
      var description;
      description = $('div#event-description div.description div.inner').redactor('get');
      $('div.save-status').html('Saving...');
      this.savingInProgress = true;
      Bazaarboy.post('event/edit/', {
        id: eventId,
        description: description
      }, function(response) {
        if (response.status !== 'OK') {
          alert(response.message);
        } else {
          this.savingInProgress = false;
          setTimeout((function() {
            $('div.save-status').html('Saved');
          }), 500);
        }
      });
    },
    init: function() {
      var latitude, longitude, map, mapCenter, mapOptions, marker,
        _this = this;
      latitude = parseFloat($('div.map-canvas').attr('data-latitude'));
      longitude = parseFloat($('div.map-canvas').attr('data-longitude'));
      if (latitude !== NaN && longitude !== NaN) {
        $('div.map-canvas').removeClass('hide');
        mapCenter = new google.maps.LatLng(latitude, longitude);
        mapOptions = {
          zoom: 15,
          center: mapCenter,
          draggable: false,
          mapTypeControl: false,
          scaleControl: false,
          panControl: false,
          scrollwheel: false,
          streetViewControl: false,
          zoomControl: true
        };
        map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
        marker = new google.maps.Marker({
          position: mapCenter,
          map: map,
          url: "https://maps.google.com/?saddr=" + latitude + "," + longitude
        });
        google.maps.event.addListener(marker, 'click', function() {
          window.open(this.url, '_blank');
        });
      }
      if (design) {
        $('div#event-description div.description div.inner').redactor({
          buttons: ['formatting', 'bold', 'italic', 'deleted', 'fontcolor', 'alignment', '|', 'unorderedlist', 'orderedlist', 'outdent', 'indent', '|', 'horizontalrule', 'table', 'image', 'video', 'link', '|', 'html'],
          boldTag: 'b',
          italicTag: 'i',
          imageUpload: rootUrl + 'file/image/upload/'
        });
        $('a.save.primary-btn').click(function() {
          _this.saveDescription();
        });
      }
    }
  };

  Bazaarboy.event.index.init();

}).call(this);
