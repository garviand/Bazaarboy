(function() {
  var _this = this;

  Bazaarboy.event.manage = {
    selectionStatus: 'all',
    checkinStatus: 'all',
    purchaseInProgress: false,
    add_purchase: function() {
      var params, ticketId,
        _this = this;
      this.purchaseInProgress = true;
      $('div#rsvp div.action a.confirm').css('display', 'none');
      $('div#rsvp div.action div.loading').removeClass('hide');
      params = {
        event: eventId,
        first_name: $('form[name=add-guest] input[name=first_name]').val().trim(),
        last_name: $('form[name=add-guest] input[name=last_name]').val().trim(),
        email: $('form[name=add-guest] input[name=email]').val().trim(),
        details: {}
      };
      ticketId = parseInt($('form[name=add-guest] select[name=ticket]').val());
      params.details[ticketId] = parseInt($('form[name=add-guest] input[name=quantity]').val());
      params.details = JSON.stringify(params.details);
      $('form[name=add-guest] input[name=submit]').val('Adding...');
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
          _this.purchaseInProgress = false;
        } else {
          alert(response.message);
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
      $("div.guest-add-invite a.start-guest-invite").click(function(e) {
        e.preventDefault();
        return $('div#invite-modal').foundation('reveal', 'open');
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
