(function() {
  Bazaarboy.event.index = {
    aviary: void 0,
    savingInProgress: false,
    unsavedProgress: false,
    toLaunch: false,
    overlayAnimationInProgress: false,
    redactorContent: void 0,
    emailSending: false,
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
          scope.toLaunch = false;
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
                  window.location = eventUrl + '#launch';
                } else {
                  alert(response.message);
                  $('div.event-launch a.launch-btn').html('Launch Event');
                  scope.toLaunch = false;
                }
              });
            }
          }), 500);
        }
      });
    },
    updateSubtotal: function() {
      var quantity, ticket, tickets, totalPrice, totalQuantity, _i, _len;
      tickets = $('div#tickets-canvas div.ticket.active');
      totalPrice = 0;
      totalQuantity = 0;
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        quantity = parseInt($(ticket).find('input.ticket-quantity').val());
        totalQuantity += quantity;
        totalPrice += quantity * parseFloat($(ticket).attr('data-price'));
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
      var params, quantity, ticket, ticketSelected, tickets, _i, _len,
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
      if ($('input[name=promos]').length > 0) {
        if ($('input[name=promos]').val().trim() !== '') {
          params['promos'] = $('input[name=promos]').val().trim();
        }
      }
      tickets = $('div#tickets-canvas div.ticket');
      ticketSelected = false;
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        if ($(ticket).hasClass('active')) {
          ticketSelected = true;
          quantity = parseInt($(ticket).find('input.ticket-quantity').val());
          params.details[$(ticket).attr('data-id')] = quantity;
        }
      }
      params.details = JSON.stringify(params.details);
      if (params.phone.length === 0) {
        delete params.phone;
      }
      if (!ticketSelected) {
        alert('You Must Select A Ticket');
        $('a#tickets-confirm').html('Confirm RSVP');
      } else if (params.first_name === '') {
        alert('Please Add a First Name');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else if (params.last_name === '') {
        alert('Please Add a Last Name');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else if (params.email === '') {
        alert('Please Add an Email');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else {
        Bazaarboy.post('event/purchase/', params, function(response) {
          var a, b, total;
          if (response.status !== 'OK') {
            alert(response.message);
            return $('a#tickets-confirm').html('Confirm RSVP');
          } else {
            if (response.publishable_key == null) {
              return _this.completePurchase(response.tickets);
            } else {
              total = response.purchase.amount * 100;
              a = (1 + 0.05) * total + 50;
              b = (1 + 0.029) * total + 30 + 1000;
              total = Math.round(Math.min(a, b));
              return StripeCheckout.open({
                key: response.publishable_key,
                address: false,
                amount: total,
                currency: 'usd',
                name: response.purchase.event.name,
                description: 'Tickets for ' + response.purchase.event.name,
                panelLabel: 'Checkout',
                email: params.email,
                image: response.logo,
                closed: function() {
                  $('a#tickets-confirm').html('Confirm RSVP');
                },
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
        return;
      }
    },
    completePurchase: function(tickets) {
      var k, newTicket, scope, ticket, ticketHTML;
      scope = this;
      if (!this.overlayAnimationInProgress) {
        this.overlayAnimationInProgress = true;
        $('div#confirmation-modal div.ticket').hide();
        ticketHTML = $('div#confirmation-modal div.ticket-model').html();
        for (k in tickets) {
          ticket = tickets[k];
          newTicket = $(ticketHTML);
          newTicket.find('div.quantity').html('x' + ticket['quantity']);
          newTicket.find('div.name').html(ticket['name']);
          $('div#confirmation-modal').find('div.tickets').append(newTicket);
          newTicket.show();
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
        $('.ticket').find('div.ticket-middle').slideUp(100);
        $('.ticket.active').removeClass('active');
        $('a#tickets-confirm').html('Confirm RSVP');
        $('input[name=quantity]').val(0);
        $('input[name=first_name]').val('');
        $('input[name=last_name]').val('');
        $('input[name=email]').val('');
        $('input[name=phone]').val('');
        $('input.ticket-selected').prop('checked', false);
        $('div#confirmation-modal').foundation('reveal', 'open');
      }
    },
    search_organizers: function() {
      var organizerModel, value,
        _this = this;
      $('form.add-organizer-form div.organizer').remove();
      organizerModel = $('div.organizer-model');
      value = $('form.add-organizer-form input#organizer-name').val();
      Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var i, newProfile, profiles, _i, _ref;
        if (response.status === 'OK') {
          profiles = response.profiles;
          if (profiles.length > 0) {
            $('.profile_login .profile_choices').empty();
            for (i = _i = 0, _ref = profiles.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
              newProfile = organizerModel;
              newProfile.find('div.organizer-name').html(profiles[i].name);
              if (profiles[i].image_url != null) {
                newProfile.find('div.organizer-image').html('<img src=' + profiles[i].image_url + ' />');
              } else {
                newProfile.find('div.organizer-image').html('&nbsp;');
              }
              newProfile.find('a.add-organizer-submit').attr('data-profile', profiles[i].pk);
              $('form.add-organizer-form').append(newProfile.html());
            }
          }
        }
      });
    },
    init: function() {
      var add_organizer_debounce, geocoder, iconImage, latitude, latlng, longitude, map, mapCenter, mapOptions, mapStyles, marker, postData, scope,
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
        if (hash === '#invite') {
          $('div#invite-modal').foundation('reveal', 'open');
          window.history.pushState("", document.title, window.location.pathname);
          return;
        }
        if (hash === '#conf') {
          $('div#confirmation-modal').foundation('reveal', 'open');
        }
      });
      $(window).hashchange();
      if ($('div#event-header').height() > 66) {
        $('div#event-header').css('position', 'absolute');
        $('div#event').css('padding-top', $('div#event-header').height() + 'px');
        $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px');
      }
      $(window).resize(function() {
        if ($('div#event-header').height() > 66) {
          $('div#event-header').css('position', 'absolute');
          $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px');
        } else {
          $('div#event-header').css('position', 'fixed');
          $('div#tickets').css('top', '100px');
        }
        $('div#event').css('padding-top', $('div#event-header').height() + 'px');
      });
      $('div#launch-modal a.start-invite').click(function() {
        $('div#invite-modal').foundation('reveal', 'open');
      });
      $('div#invite-modal form.invite-form div.event-list').click(function() {
        $(this).toggleClass('selected');
      });
      $('div#invite-modal form.invite-form a.send-invitation').click(function() {
        var events, optionals, params;
        $(this).html('Sending...');
        params = $('form.invite-form').serializeObject();
        events = '';
        $('div#invite-modal form.invite-form div.event-list.selected').each(function() {
          if (events !== '') {
            events += ',';
          }
          events += $(this).data('id');
        });
        params['events'] = events;
        optionals = ['emails', 'events'];
        params = Bazaarboy.stripEmpty(params, optionals);
        if (!scope.emailSending) {
          scope.emailSending = true;
          Bazaarboy.post('event/' + eventId + '/invite/', params, function(response) {
            if (response.status === 'OK') {
              $('div.invite-success span.invite-count').html(response.count);
              $('form.invite-form').fadeOut(300, function() {
                scope.emailSending = false;
                $('div.invite-success').fadeIn(300);
              });
            } else {
              scope.emailSending = false;
              alert(response.message);
              $(this).html('Send Invitations');
            }
          });
        }
      });
      $('div.invite-success a.close-invite-modal').click(function() {
        $('div#invite-modal').foundation('reveal', 'close');
      });
      $('div#tickets-details a.start-promo-btn').click(function() {
        return $('div.start-promo').fadeOut(300, function() {
          $('div.enter-promo').fadeIn(300);
        });
      });
      addthisevent.settings({
        outlook: {
          show: true,
          text: "Outlook Calendar"
        },
        google: {
          show: true,
          text: "Google Calendar"
        },
        yahoo: {
          show: true,
          text: "Yahoo Calendar"
        },
        hotmail: {
          show: false,
          text: "Hotmail Calendar"
        },
        ical: {
          show: true,
          text: "iCal Calendar"
        },
        facebook: {
          show: true,
          text: "Facebook Event"
        },
        dropdown: {
          order: "google,ical,outlook,yahoo,hotmail"
        }
      });
      latitude = parseFloat($('div.map-canvas').attr('data-latitude'));
      longitude = parseFloat($('div.map-canvas').attr('data-longitude'));
      if (!isNaN(latitude) && !isNaN(longitude)) {
        geocoder = new google.maps.Geocoder();
        latlng = new google.maps.LatLng(latitude, longitude);
        geocoder.geocode({
          'latLng': latlng
        }, function(results, status) {
          var city_zip, loc, street;
          if (results[0]) {
            loc = results[0]['formatted_address'].split(",");
            street = loc[0];
            city_zip = loc[1] + ", " + loc[2];
            $("div#event-location div.address span.street-address").html(street);
            $("div#event-location div.address span.city-zip").html(city_zip);
            $("div#event-location div.address").removeClass("hide");
          }
        });
        $('div.map-canvas').removeClass('hide');
        mapCenter = new google.maps.LatLng(latitude, longitude);
        mapStyles = [
          {
            featureType: "administrative",
            elementType: "all",
            stylers: [
              {
                visibility: "on"
              }, {
                saturation: -100
              }, {
                lightness: 20
              }
            ]
          }, {
            featureType: "road",
            elementType: "all",
            stylers: [
              {
                visibility: "on"
              }, {
                saturation: -100
              }, {
                lightness: 40
              }
            ]
          }, {
            featureType: "water",
            elementType: "all",
            stylers: [
              {
                visibility: "on"
              }, {
                saturation: -10
              }, {
                lightness: 30
              }
            ]
          }, {
            featureType: "landscape.man_made",
            elementType: "all",
            stylers: [
              {
                visibility: "simplified"
              }, {
                saturation: -60
              }, {
                lightness: 10
              }
            ]
          }, {
            featureType: "landscape.natural",
            elementType: "all",
            stylers: [
              {
                visibility: "simplified"
              }, {
                saturation: -60
              }, {
                lightness: 60
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
        iconImage = {
          url: staticUrl + "images/map_icon.png",
          size: new google.maps.Size(200, 111),
          origin: new google.maps.Point(0, 15),
          anchor: new google.maps.Point(100, 55)
        };
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
          imageUpload: rootUrl + 'file/image/upload/',
          toolbarFixedBox: true,
          placeholder: 'Add Your Event Description Here...'
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
          $('div.save-status').html('Unsaved Changes');
        });
        scope.redactorContent = $('div#event-description div.description div.inner').redactor('get');
        $('div#event-cover form.upload_cover a.upload_cover_btn').click(function() {
          $('div#event-cover form.upload_cover input[name=image_file]').click();
        });
        $('div#event-cover form.upload_cover a.edit_cover_btn').click(function() {
          scope.aviary.launch({
            image: 'cover-image',
            url: $("#cover-image").attr('src')
          });
        });
        $('div#event-cover form.upload_cover a.delete_cover_btn').click(function() {
          if (confirm('Are you sure you want to delete your cover image?')) {
            Bazaarboy.post('event/edit/', {
              id: eventId,
              cover: 'delete'
            }, function(response) {
              if (response.status === 'OK') {
                $('img#cover-image').attr('src', '');
                $('div#event-cover form.upload_cover a.delete_cover_btn').addClass('hidden');
                $('div#event-cover form.upload_cover a.edit_cover_btn').addClass('hidden');
                $('div#event-cover form.upload_cover a.upload_cover_btn').removeClass('hidden');
              } else {
                alert(response.message);
              }
            });
          }
        });
        postData = {
          event: eventId
        };
        this.aviary = new Aviary.Feather({
          apiKey: 'ce3b87fb1edaa22c',
          apiVersion: 3,
          enableCORS: true,
          onSave: function(imageId, imageUrl) {
            $("img#" + imageId).attr('src', imageUrl);
            _this.aviary.close();
            $('div#event-cover form.upload_cover a.delete_cover_btn').removeClass('hidden');
            $('div#event-cover form.upload_cover a.edit_cover_btn').removeClass('hidden');
            $('div#event-cover form.upload_cover a.upload_cover_btn').addClass('hidden');
            Bazaarboy.post('file/aviary/', {
              event: eventId,
              url: imageUrl
            }, function(response) {
              $('img#cover-image').attr('src', response.image);
            });
          }
        });
        $('div#event-cover form.upload_cover input[name=image_file]').fileupload({
          url: rootUrl + 'file/image/upload/',
          type: 'POST',
          add: function(event, data) {
            data.submit();
          },
          done: function(event, data) {
            var response;
            response = jQuery.parseJSON(data.result);
            if (response.status === 'OK') {
              $('img#cover-image-placeholder').attr('src', mediaUrl + response.image.source);
              $('img#cover-image').attr('src', mediaUrl + response.image.source);
              _this.aviary.launch({
                image: 'cover-image-placeholder',
                url: mediaUrl + response.image.source
              });
            } else {
              alert(response.message);
            }
          }
        });
      }
      $("div.event-share a.share-btn").click(function() {
        $('div.event-rsvp, div.event-share, div.event-price').fadeOut(300, function() {
          $("div.event-share-canvas").fadeIn(300);
        });
      });
      $("span.close-share").click(function() {
        $("div.event-share-canvas").fadeOut(300, function() {
          $('div.event-rsvp, div.event-share, div.event-price').fadeIn(300);
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
      $('div#tickets-canvas div.ticket div.ticket-top').hover(function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').addClass('hover');
        }
      }, function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').removeClass('hover');
        }
      });
      $('div#tickets-canvas div.ticket-top').click(function() {
        var quant;
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('.ticket').toggleClass('active');
          if ($(this).parents('.ticket').hasClass('active')) {
            $(this).parents('.ticket').find('div.ticket-middle').slideDown(100);
            quant = $(this).parents('.ticket').find('input.ticket-quantity');
            if (quant.val().trim() === '' || parseInt(quant.val()) === 0) {
              quant.val(1);
            }
          } else {
            $(this).parents('.ticket').find('div.ticket-middle').slideUp(100);
          }
          scope.updateSubtotal();
        }
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
        if ($(this).val().trim() === '' || parseInt($(this).val()) === 0) {
          $(this).val(0);
          $(this).parents('.ticket').removeClass('active');
          $(this).parents('.ticket').find('div.ticket-middle').slideUp(100);
        }
        scope.updateSubtotal();
      });
      $('a#tickets-confirm').click(function() {
        _this.purchase();
      });
      $('a.issue-btn').click(function() {
        $('div#issue-modal').foundation('reveal', 'open');
      });
      $('a.issue-close').click(function() {
        $('div#issue-modal').foundation('reveal', 'close');
      });
      $('div.send-issue a.send-issue-btn').click(function() {
        $(this).html('Sending...');
        $('form.issue-form').submit();
      });
      $('form.issue-form').submit(function(event) {
        event.preventDefault();
      });
      $('form.issue-form').on('valid', function() {
        var optionals, params;
        params = $(this).serializeObject();
        optionals = [];
        params = Bazaarboy.stripEmpty(params, optionals);
        console.log(params);
        Bazaarboy.post('event/issue/', params, function(response) {
          if (response.status === 'OK') {
            return $('form.issue-form').fadeOut(300, function() {
              $('div.row.issue-success').fadeIn(300);
            });
          } else {
            alert(response.message);
            return $('div.send-issue a.send-message').html('Send Message');
          }
        });
      });
      $('a.contact-organizer-btn').click(function() {
        $('div#contact-organizer-modal').foundation('reveal', 'open');
      });
      $('a.contact-organizer-close').click(function() {
        $('div#contact-organizer-modal').foundation('reveal', 'close');
      });
      $('div.send-contact-organizer a.send-message').click(function() {
        $(this).html('Sending...');
        $('form.contact-organizer-form').submit();
      });
      $('form.contact-organizer-form').submit(function(event) {
        event.preventDefault();
      });
      $('form.contact-organizer-form').on('valid', function() {
        var optionals, params;
        params = $(this).serializeObject();
        optionals = [];
        params = Bazaarboy.stripEmpty(params, optionals);
        console.log(params);
        Bazaarboy.post('profile/message/', params, function(response) {
          if (response.status === 'OK') {
            return $('form.contact-organizer-form').fadeOut(300, function() {
              $('div.row.contact-organizer-success').fadeIn(300);
            });
          } else {
            alert(response.message);
            return $('div.send-contact-organizer a.send-message').html('Send Message');
          }
        });
      });
      $('a.add-organizer-btn').click(function() {
        $('div#add-organizer-modal').foundation('reveal', 'open');
      });
      $('a.add-organizer-close').click(function() {
        $('div#add-organizer-modal').foundation('reveal', 'close');
      });
      $('a.add-organizer-another').click(function() {
        $('div.row.add-organizer-success').fadeOut(300, function() {
          $('form.add-organizer-form').fadeIn(300);
        });
      });
      add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers);
      $('form.add-organizer-form input#organizer-name').bind('keypress', add_organizer_debounce);
      $('form.add-organizer-form').on('click', 'a.add-organizer-submit', function() {
        var profileId,
          _this = this;
        profileId = $(this).data('profile');
        Bazaarboy.post('event/organizer/add/', {
          id: eventId,
          profile: profileId
        }, function(response) {
          var newOrganizer;
          if (response.status === 'OK') {
            newOrganizer = $('div#event-organizers div.organizer').eq(0).clone();
            if (response.profile['image_url'] != null) {
              newOrganizer.find('div.organizer-icon').css("background-image", "url(" + response.profile.image_url + ")");
            } else {
              newOrganizer.find('div.organizer-icon').css("background-image", "none");
            }
            newOrganizer.find('div.organizer-name').html("<span>" + response.profile.name + "</span>");
            $('div#event-organizers div.organizer-list').append(newOrganizer);
            return $('form.add-organizer-form').fadeOut(300, function() {
              $('form.add-organizer-form input#organizer-name').val('');
              $('form.add-organizer-form div.organizer').remove();
              $('div.row.add-organizer-success').fadeIn(300);
            });
          } else {
            return alert(response.message);
          }
        });
      });
    }
  };

  Bazaarboy.event.index.init();

}).call(this);
