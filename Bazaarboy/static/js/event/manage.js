(function() {
  var _this = this;

  Bazaarboy.event.manage = {
    selectionStatus: 'all',
    checkinStatus: 'all',
    purchaseInProgress: false,
    add_purchase: function() {
      var params, quantity, ticketId,
        _this = this;
      this.purchaseInProgress = true;
      $('div#rsvp div.action a.confirm').css('display', 'none');
      $('div#rsvp div.action div.loading').removeClass('hide');
      params = {
        event: eventId,
        first_name: $('form[name=add-guest] input[name=first_name]').val().trim(),
        last_name: $('form[name=add-guest] input[name=last_name]').val().trim(),
        email: $('form[name=add-guest] input[name=email]').val().trim(),
        send_email: $('form[name=add-guest] input[name=send_email]').is(':checked'),
        details: {}
      };
      ticketId = parseInt($('form[name=add-guest] select[name=ticket]').val());
      quantity = parseInt($('form[name=add-guest] input[name=quantity]').val());
      params.details[ticketId] = {
        'quantity': quantity,
        'extra_fields': {}
      };
      if (!$('form[name=add-guest] div.address-field').hasClass('hide')) {
        params.address = $('form[name=add-guest] div.address-field input.custom-fields-address-input').val();
      }
      if ($('form[name=add-guest] div.custom-field-container').length > 0) {
        $.each($('form[name=add-guest] div.custom-field-container'), function() {
          return $.each($(this).find('select.custom-fields-option-input, input.custom-fields-text-input'), function() {
            return params.details[ticketId]['extra_fields'][$(this).data('field')] = String($(this).val()).trim();
          });
        });
      }
      params.details = JSON.stringify(params.details);
      $('form[name=add-guest] input[name=submit]').val('Adding...');
      Bazaarboy.post('event/purchase/add/', params, function(response) {
        var newGuest;
        if (response.status === 'WAIT') {
          if (confirm(response.message)) {
            params.force = true;
            Bazaarboy.post('event/purchase/add/', params, function(response) {
              var newGuest;
              if (response.status === 'OK') {
                $('form[name=add-guest] input[name=first_name]').val('');
                $('form[name=add-guest] input[name=last_name]').val('');
                $('form[name=add-guest] input[name=email]').val('');
                $('form[name=add-guest] input[name=quantity]').val('');
                $('form[name=add-guest] input[name=submit]').val('Add Guest(s)');
                newGuest = $('div.guest_template').clone();
                newGuest.find('div.confirmation').html(response.purchase.code + '&nbsp;');
                newGuest.find('div.ticket_name').html(response.tickets[ticketId]['name'] + ' (' + response.tickets[ticketId]['quantity'] + ')');
                newGuest.find('div.name').html(params.first_name + ' ' + params.last_name);
                newGuest.data('id', response.purchase.id);
                newGuest.data('ticket', ticketId);
                newGuest.removeClass('guest_template').removeClass('hidden');
                $('div.list_headers').after(newGuest);
                return _this.purchaseInProgress = false;
              } else {
                alert(response.message);
                $('form[name=add-guest] input[name=submit]').val('Add Guest(s)');
                return _this.purchaseInProgress = false;
              }
            });
          } else {
            alert('Add Guest Canceled');
            $('form[name=add-guest] input[name=submit]').val('Add Guest(s)');
            _this.purchaseInProgress = false;
          }
        } else if (response.status === 'OK') {
          $('form[name=add-guest] input[name=first_name]').val('');
          $('form[name=add-guest] input[name=last_name]').val('');
          $('form[name=add-guest] input[name=email]').val('');
          $('form[name=add-guest] input[name=quantity]').val('');
          $('form[name=add-guest] input[name=submit]').val('Add Guest(s)');
          newGuest = $('div.guest_template').clone();
          newGuest.find('div.confirmation').html(response.purchase.code + '&nbsp;');
          newGuest.find('div.ticket_name').html(response.tickets[ticketId]['name'] + ' (' + response.tickets[ticketId]['quantity'] + ')');
          newGuest.find('div.name').html(params.first_name + ' ' + params.last_name);
          newGuest.data('id', response.purchase.id);
          newGuest.data('ticket', ticketId);
          newGuest.removeClass('guest_template').removeClass('hidden');
          $('div.list_headers').after(newGuest);
          _this.purchaseInProgress = false;
        } else {
          alert(response.message);
          $('form[name=add-guest] input[name=submit]').val('Add Guest(s)');
          _this.purchaseInProgress = false;
        }
      });
    },
    checkin: function(guest_id) {
      Bazaarboy.post('event/checkin/', {
        id: guest_id
      }, function(response) {});
    },
    checkout: function(guest_id) {
      Bazaarboy.post('event/checkin/', {
        id: guest_id,
        cancel: true
      }, function(response) {});
    },
    filterGuests: function(param, value, ticketType, checkStatus, updateListLength) {
      var i, length, newLength, newLengthChecked, rsvp, targetValue, ticketCheck, _i, _ref;
      length = $('div.guest').length;
      for (i = _i = 0, _ref = length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        rsvp = $('div.guest:eq(' + i + ')');
        targetValue = $(rsvp).find('div.' + param).html();
        if (targetValue.toLowerCase().indexOf(value.toLowerCase()) !== -1) {
          if (String(rsvp.data('ticket')).indexOf(',') > -1) {
            ticketCheck = $.inArray(String(ticketType), String(rsvp.data('ticket')).split(',')) > -1;
          } else {
            ticketCheck = rsvp.data('ticket') === ticketType;
          }
          if (ticketCheck || ticketType === 'all') {
            $(rsvp).removeClass('hide');
          }
        }
        if (checkStatus === 'checked_in') {
          if (!$(rsvp).hasClass('checked_in')) {
            $(rsvp).addClass('hide');
          }
        }
        if (checkStatus === 'not_checked_in') {
          if ($(rsvp).hasClass('checked_in')) {
            $(rsvp).addClass('hide');
          }
        }
      }
      if (updateListLength) {
        newLength = $('div.guest').not('.hide').length;
        newLengthChecked = $('div.guest.checked_in').not('.hide').length;
        $('div.checkin_numbers span.total_guests').html(newLength);
        $('div.checkin_numbers span.checked_in').html(newLengthChecked);
      }
    },
    init: function() {
      var scope;
      scope = this;
      $("div.guest-add-invite a.raffle-btn").click(function(e) {
        var winner, winner_email, winner_id, winner_name;
        e.preventDefault();
        winner_id = Math.floor(Math.random() * ($("div.guest").length));
        winner = $("div.list_guests div.guest").eq(winner_id);
        winner_name = winner.find("div.name").html();
        winner_email = winner.attr('data-email');
        $('div#raffle-modal div.subtext-name').html(winner_name);
        $('div#raffle-modal div.subtext-email').html(winner_email);
        $('div#raffle-modal').foundation('reveal', 'open');
      });
      $("div.guest-add-invite a.start-guest-invite").click(function(e) {
        e.preventDefault();
        $('div#invite-modal').foundation('reveal', 'open');
      });
      $("div#raffle-modal a.back-to-list").click(function() {
        $('div#invite-modal').foundation('reveal', 'close');
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
        optionals = ['emails', 'events', 'message'];
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
      $('a.close-invite-modal').click(function() {
        $('div#invite-modal').foundation('reveal', 'close');
      });
      $("div.guest-add-invite a.start-guest-add").click(function(e) {
        e.preventDefault();
        $('div.add-guest-container').removeClass('hidden');
      });
      $('form[name=add-guest]').submit(function(e) {
        e.preventDefault();
        if (!scope.purchaseInProgress) {
          scope.add_purchase();
        }
      });
      $('form[name=add-guest] select[name=ticket]').change(function(e) {
        if ($(this).val() === '-1') {
          $('form[name=add-guest] div.custom-fields').addClass('hide');
        } else {
          Bazaarboy.get('event/ticket/', {
            id: $(this).val()
          }, function(response) {
            var allOptions, extra_fields, fieldName, fieldOptions, newInput, option, _i, _len;
            extra_fields = JSON.parse(response.ticket.extra_fields);
            $('form[name=add-guest] div.custom-fields-inputs div.row:not(.address-field)').remove();
            if ($.isEmptyObject(extra_fields) && response.ticket.request_address !== true) {
              $('form[name=add-guest] div.custom-fields').addClass('hide');
            } else {
              if (response.ticket.request_address === true) {
                $('form[name=add-guest] div.custom-fields div.address-field').removeClass('hide');
              } else {
                $('form[name=add-guest] div.custom-fields div.address-field').addClass('hide');
              }
              if (!$.isEmptyObject(extra_fields)) {
                for (fieldName in extra_fields) {
                  fieldOptions = extra_fields[fieldName];
                  if (fieldOptions.length === 0) {
                    newInput = "<div class='row custom-field-container'>";
                    newInput += "<div class='small-12 medium-6 columns custom-field-input-label'>";
                    newInput += fieldName;
                    newInput += "</div>";
                    newInput += "<div class='small-12 medium-6 end columns custom-fields-text-input-container'>";
                    newInput += "<input class='custom-fields-text-input' type='text' data-field='" + fieldName.trim() + "' />";
                    newInput += "</div>";
                    newInput += "</div>";
                    newInput = $(newInput);
                    $('form[name=add-guest] div.custom-fields-inputs').append(newInput);
                  } else {
                    newInput = "<div class='row custom-field-container'>";
                    newInput += "<div class='small-12 medium-6 columns custom-field-input-label'>";
                    newInput += fieldName;
                    newInput += "</div>";
                    newInput += "<div class='small-12 medium-6 end columns custom-fields-text-input-container'>";
                    newInput += "<select class='custom-fields-option-input' data-field='" + fieldName.trim() + "'>";
                    allOptions = fieldOptions.split(',');
                    for (_i = 0, _len = allOptions.length; _i < _len; _i++) {
                      option = allOptions[_i];
                      newInput += "<option value='" + option.trim() + "'>" + option.trim() + "</option>";
                    }
                    newInput += "</select>";
                    newInput += "</div>";
                    newInput += "</div>";
                    newInput = $(newInput);
                    $('form[name=add-guest] div.custom-fields-inputs').append(newInput);
                  }
                }
              }
              $('form[name=add-guest] div.custom-fields').removeClass('hide');
            }
          });
        }
      });
      $('a.show-refunds').click(function() {
        $('div.list_guests div.name').removeClass('medium-4').addClass('medium-2');
        $('div.refund').removeClass('hide');
      });
      $('div.refund a.refund-btn').click(function() {
        var container;
        container = $(this).parents('div.guest');
        if (confirm('Are you sure you want to refund this purchase?')) {
          $(this).html('refunding...');
          Bazaarboy.post('payment/refund/', {
            purchase: $(this).data('purchase')
          }, function(response) {
            if (response.status === 'OK') {
              container.fadeOut(300, function() {
                $(this).remove();
              });
            } else {
              alert(response.message);
            }
          });
        }
      });
      $('form input[name=guest_name]').keyup(function(e) {
        e.preventDefault();
        if ($(this).val() === '') {
          $('div.guest').removeClass('hide');
        } else {
          $('div.guest').addClass('hide');
          scope.filterGuests('name', $(this).val(), scope.selectionStatus, scope.checkinStatus, false);
        }
      });
      $('form input[name=guest_code]').keyup(function(e) {
        e.preventDefault();
        if ($(this).val() === '') {
          $('div.guest').removeClass('hide');
        } else {
          $('div.guest').addClass('hide');
          scope.filterGuests('confirmation', $(this).val(), scope.selectionStatus, scope.checkinStatus, false);
        }
      });
      $('form.list_search div.ticket_filters a').click(function(e) {
        e.preventDefault();
        $('form.list_search div.ticket_filters a').removeClass('active');
        $(this).addClass('active');
        $('form.list_search input[name=guest_name]').val('');
        $('form.list_search input[name=guest_code]').val('');
        $('div.guest').addClass('hide');
        scope.selectionStatus = $(this).data('id');
        scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true);
      });
      $('form.list_search div.checkin_filters a').click(function(e) {
        e.preventDefault();
        $('form.list_search div.checkin_filters a').removeClass('active');
        $(this).addClass('active');
        $('form.list_search input[name=guest_name]').val('');
        $('form.list_search input[name=guest_code]').val('');
        $('div.guest').addClass('hide');
        scope.checkinStatus = $(this).data('status');
        scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true);
      });
      $('div.list_guests').on('click', 'div.guest div.checkin a', function(e) {
        var checkCount, guest, guest_id, totalCount;
        e.preventDefault();
        guest = $(this).parents('div.guest');
        guest_id = guest.data('id');
        if (!guest.hasClass('checked_in')) {
          checkCount = parseInt($('div.checkin_numbers span.checked_in').html()) + 1;
          $('div.checkin_numbers span.checked_in').html(checkCount);
          guest.addClass('checked_in');
          $(this).html('Arrived');
          scope.checkin(guest_id);
          if (scope.checkinStatus === 'not_checked_in') {
            guest.addClass('hide');
            totalCount = parseInt($('div.checkin_numbers span.total_guests').html()) - 1;
            $('div.checkin_numbers span.total_guests').html(totalCount);
            $('div.checkin_numbers span.checked_in').html('0');
            return Bazaarboy.adjustBottomPosition();
          }
        } else {
          checkCount = parseInt($('div.checkin_numbers span.checked_in').html()) - 1;
          $('div.checkin_numbers span.checked_in').html(checkCount);
          guest.removeClass('checked_in');
          $(this).html('Check In');
          scope.checkout(guest_id);
          if (scope.checkinStatus === 'checked_in') {
            guest.addClass('hide');
            totalCount = parseInt($('div.checkin_numbers span.total_guests').html()) - 1;
            $('div.checkin_numbers span.total_guests').html(totalCount);
            $('div.checkin_numbers span.checked_in').html(totalCount);
            return Bazaarboy.adjustBottomPosition();
          }
        }
      });
    }
  };

  Bazaarboy.event.manage.init();

}).call(this);
