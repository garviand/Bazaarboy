(function() {
  Bazaarboy.event.index = {
    savingInProgress: false,
    unsavedProgress: false,
    toLaunch: false,
    overlayAnimationInProgress: false,
    redactorContent: void 0,
    saveDescription: function() {
      var description, scope;
      scope = this;
      description = $('div#event-description div.description div.inner').redactor('get');
      $('div.save-status').html('Saving...');
      this.savingInProgress = true;
      Bazaarboy.post('event/edit/', {
        id: eventId,
        description: description
      }, function(response) {
        if (response.status !== 'OK') {
          alert(response.message);
          $('div.event-launch a.launch-btn').html('Launch Event');
          $('div.save-status').html('Saved');
        } else {
          this.savingInProgress = false;
          setTimeout((function() {
            var _this = this;
            $('div.save-status').html('Saved');
            if (scope.toLaunch) {
              Bazaarboy.post('event/launch/', {
                id: eventId
              }, function(response) {
                if (response.status === 'OK') {
                  window.location = '/event/' + eventId + '#launch';
                } else {
                  alert(response.message);
                  $('div.event-launch a.launch-btn').html('Launch Event');
                }
              });
            }
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
      if (totalPrice !== 0) {
        $('div#tickets-subtotal span.fee').removeClass('hide');
      } else {
        $('div#tickets-subtotal span.fee').addClass('hide');
      }
      $('div#tickets-subtotal span.count').html(totalQuantity);
      if (totalQuantity === 1) {
        $('div#tickets-subtotal span.plural').addClass('hide');
      } else {
        $('div#tickets-subtotal span.plural').removeClass('hide');
      }
    },
    purchase: function() {
      var params, quantity, ticket, tickets, _i, _len,
        _this = this;
      $('a#tickets-confirm').html('Processing...');
      params = {
        event: eventId,
        first_name: $('input[name=first_name]').val().trim(),
        last_name: $('input[name=last_name]').val().trim(),
        email: $('input[name=email]').val().trim(),
        phone: $('input[name=phone]').val().trim(),
        details: {}
      };
      tickets = $('div#tickets-canvas div.ticket');
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        if ($(ticket).find('input.ticket-selected').is(':checked')) {
          quantity = parseInt($(ticket).find('input.ticket-quantity').val());
          params.details[$(ticket).attr('data-id')] = quantity;
        }
      }
      params.details = JSON.stringify(params.details);
      if (params.phone.length === 0) {
        delete params.phone;
      }
      Bazaarboy.post('event/purchase/', params, function(response) {
        var a, b, total;
        if (response.status !== 'OK') {
          alert(response.message);
          $('a#tickets-confirm').html('Confirm RSVP');
        } else {
          if (response.publishable_key == null) {
            _this.completePurchase(response.tickets);
          } else {
            total = response.purchase.amount * 100;
            a = (1 + 0.05) * total + 50;
            b = (1 + 0.029) * total + 30 + 1000;
            total = Math.round(Math.min(a, b));
            StripeCheckout.open({
              key: response.publishable_key,
              address: false,
              amount: total,
              currency: 'usd',
              name: response.purchase.event.name,
              description: 'Tickets for ' + response.purchase.event.name,
              panelLabel: 'Checkout',
              email: params.email,
              image: response.logo,
              token: function(token) {
                Bazaarboy.post('payment/charge/', {
                  checkout: response.purchase.checkout,
                  stripe_token: token.id
                }, function(response) {
                  if (response.status === 'OK') {
                    _this.completePurchase(response.tickets);
                  } else {
                    alert(response.message);
                  }
                });
              }
            });
          }
        }
      });
    },
    completePurchase: function(tickets) {
      var k, newTicket, scope, ticket, ticketHTML;
      scope = this;
      if (!this.overlayAnimationInProgress) {
        this.overlayAnimationInProgress = true;
        ticketHTML = $('div#confirmation-modal div.ticket-model').html();
        $('div#confirmation-modal div.ticket-model').remove();
        for (k in tickets) {
          ticket = tickets[k];
          newTicket = $(ticketHTML);
          newTicket.find('div.quantity').html('x' + ticket['quantity']);
          newTicket.find('div.name').html(ticket['name']);
          $('div#confirmation-modal').find('div.tickets').append(newTicket);
        }
        $('div#wrapper-overlay').animate({
          opacity: 0
        }, 300, function() {
          $(this).addClass('hide');
        });
        $('div#tickets').animate({
          opacity: 0
        }, 300, function() {
          $(this).addClass('hide');
          scope.overlayAnimationInProgress = false;
        });
      }
      $('div#confirmation-modal').foundation('reveal', 'open');
    },
    init: function() {
      var latitude, longitude, map, mapCenter, mapOptions, mapStyles, marker, scope,
        _this = this;
      scope = this;
      $(window).hashchange(function() {
        var hash;
        hash = location.hash;
        if (hash === '#launch') {
          $('div#launch-modal').foundation('reveal', 'open');
          window.history.pushState("", document.title, window.location.pathname);
          return;
        }
        if (hash === '#conf') {
          $('div#confirmation-modal').foundation('reveal', 'open');
        }
      });
      $(window).hashchange();
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
        $('div.event-launch a.launch-btn').click(function() {
          scope.toLaunch = true;
          $('div.event-launch a.launch-btn').html('Launching...');
          scope.saveDescription();
        });
        $('div#event-description div.description div.inner').keyup(function() {
          $('div.save-status').html('Editing');
        });
        scope.redactorContent = $('div#event-description div.description div.inner').redactor('get');
        setInterval((function() {
          if ($('div#event-description div.description div.inner').redactor('get') !== scope.redactorContent) {
            scope.redactorContent = $('div#event-description div.description div.inner').redactor('get');
            scope.saveDescription();
          }
        }), 5000);
      }
      $("div#event-actions a.share-btn").click(function() {
        $('div#event-actions').fadeOut(300, function() {
          $("div.share-canvas").fadeIn(300);
        });
      });
      $("span.close-share").click(function() {
        $("div.share-canvas").fadeOut(300, function() {
          $("div#event-actions").fadeIn(300);
        });
      });
      $('a#rsvp-button').click(function() {
        if (!_this.overlayAnimationInProgress) {
          $("html, body").animate({
            scrollTop: 0
          }, "fast");
          if ($('div#wrapper-overlay').hasClass('hide')) {
            _this.overlayAnimationInProgress = true;
            $('div#wrapper-overlay').css('opacity', 0).removeClass('hide');
            $('div#tickets').css('opacity', 0).removeClass('hide');
            $('div#wrapper-overlay').animate({
              opacity: 1
            }, 300);
            $('div#tickets').animate({
              opacity: 1
            }, 300, function() {
              _this.overlayAnimationInProgress = false;
            });
          }
        }
      });
      $('div#wrapper-overlay').click(function() {
        if (!_this.overlayAnimationInProgress) {
          _this.overlayAnimationInProgress = true;
          $('div#wrapper-overlay').animate({
            opacity: 0
          }, 300, function() {
            $(this).addClass('hide');
          });
          $('div#tickets').animate({
            opacity: 0
          }, 300, function() {
            $(this).addClass('hide');
            scope.overlayAnimationInProgress = false;
          });
        }
      });
      $('div#tickets-canvas div.ticket').click(function() {
        $(this).find('.ticket-selected').click();
      });
      $('input.ticket-quantity').click(function(e) {
        e.stopPropagation();
      });
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
      $('a#tickets-confirm').click(function() {
        _this.purchase();
      });
    }
  };

  Bazaarboy.event.index.init();

}).call(this);
