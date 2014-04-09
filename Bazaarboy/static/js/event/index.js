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
    updateSubtotal: function() {
      var quantity, ticket, tickets, totalPrice, totalQuantity, _i, _len;
      tickets = $('div#tickets-canvas div.ticket');
      totalPrice = 0;
      totalQuantity = 0;
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        if ($(ticket).find('input.ticket-selected').is(':checked')) {
          quantity = parseInt($(ticket).find('input.ticket-quantity').val());
          totalQuantity += quantity;
          totalPrice += quantity * parseFloat($(ticket).attr('data-price'));
        }
      }
      $('div#tickets-subtotal span.total').html(totalPrice.toFixed(2));
      $('div#tickets-subtotal span.count').html(totalQuantity);
    },
    purchase: function() {
      var params, quantity, ticket, tickets, _i, _len,
        _this = this;
      params = {
        event: eventId,
        first_name: $('input[name=first_name]').val().trim(),
        last_name: $('input[name=last_name]').val().trim(),
        email: $('input[name=email]').val().trim(),
        phone: $('input[name=phone]').val().trim(),
        tickets: {}
      };
      tickets = $('div#tickets-canvas div.ticket');
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        if ($(ticket).find('input.ticket-selected').is(':checked')) {
          quantity = parseInt($(ticket).find('input.ticket-quantity').val());
          params.tickets[$(ticket).attr('data-id')] = quantity;
        }
      }
      Bazaarboy.post('event/purchase/', params, function(response) {
        if (response.status !== 'OK') {
          alert(response.message);
        } else {
          if (response.publishable_key == null) {
            _this.completePurchase();
          } else {
            StripeCheckout.open({
              key: response.publishable_key,
              address: false,
              amount: response.purchase.amount,
              currency: 'usd',
              name: response.purchase.event.name,
              description: 'Tickets for ' + response.purchase.event.name,
              panelLabel: 'Checkout',
              token: function(token) {}
            });
          }
        }
      });
    },
    completePurchase: function() {},
    init: function() {
      var latitude, longitude, map, mapCenter, mapOptions, mapStyles, marker, scope,
        _this = this;
      scope = this;
      latitude = parseFloat($('div.map-canvas').attr('data-latitude'));
      longitude = parseFloat($('div.map-canvas').attr('data-longitude'));
      if (latitude !== NaN && longitude !== NaN) {
        $('div.map-canvas').removeClass('hide');
        mapCenter = new google.maps.LatLng(latitude, longitude);
        mapStyles = [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [
              {
                visibility: 'off'
              }
            ]
          }
        ];
        mapOptions = {
          zoom: 15,
          center: mapCenter,
          draggable: false,
          mapTypeControl: false,
          scaleControl: false,
          panControl: false,
          scrollwheel: false,
          streetViewControl: false,
          zoomControl: false,
          styles: mapStyles
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
      $('input.ticket-selected').click(function() {
        var wrapper;
        wrapper = $(this).closest('div.wrapper');
        if ($(this).is(':checked')) {
          if (parseInt($(wrapper).find('input.ticket-quantity').val()) === 0) {
            $(wrapper).find('input.ticket-quantity').val(1);
          }
        } else {
          $(wrapper).find('input.ticket-quantity').val(0);
        }
        scope.updateSubtotal();
      });
      $('input.ticket-quantity').keyup(function() {
        var wrapper;
        wrapper = $(this).closest('div.wrapper');
        if ($(this).val().trim() === '' || parseInt($(this).val()) === 0) {
          $(wrapper).find('input.ticket-selected').prop('checked', false);
        } else {
          $(wrapper).find('input.ticket-selected').prop('checked', true);
        }
        scope.updateSubtotal();
      });
      $('input.ticket-quantity').blur(function() {
        if ($(this).val().trim() === '') {
          $(this).val(0);
        }
        scope.updateSubtotal();
      });
    }
  };

  Bazaarboy.event.index.init();

}).call(this);
