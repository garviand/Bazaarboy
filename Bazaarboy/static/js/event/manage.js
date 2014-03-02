(function() {
  var _this = this,
    __slice = [].slice;

  Bazaarboy.event.manage = {
    selectionStatus: 'all',
    checkinStatus: 'all',
    add_purchase: function(ticket, email, fullName, phone) {
      var params,
        _this = this;
      if (email == null) {
        email = null;
      }
      if (fullName == null) {
        fullName = null;
      }
      if (phone == null) {
        phone = null;
      }
      this.purchaseInProgress = true;
      $('div#rsvp div.action a.confirm').css('display', 'none');
      $('div#rsvp div.action div.loading').removeClass('hidden');
      params = {
        ticket: ticket
      };
      if ((email != null) && (fullName != null)) {
        params.email = email;
        params.full_name = fullName;
      }
      if (phone != null) {
        params.phone = phone;
      }
      Bazaarboy.post('event/purchase/add/', params, function(response) {
        if (response.status === 'OK') {
          $('form.add_purchase_form div.ticket_types a').removeClass('active');
          $('div.list_content div.inner div.add_purchase').fadeOut(400, function(e) {
            var guest_div, totalCount;
            $('form.add_purchase_form input[name=guest_email]').val('');
            $('form.add_purchase_form input[name=guest_name]').val('');
            $('form.add_purchase_form input[name=guest_phone]').val('');
            guest_div = $('<div class="guest" data-ticket="' + response.purchase.ticket + '" data-id="' + response.purchase.pk + '"></div>');
            guest_div.append('<div class="name">' + fullName + '</div>');
            guest_div.append('<div class="ticket_name">' + response.purchase.ticket.name + '</div>');
            guest_div.append('<div class="confirmation">' + response.purchase.code + '</div>');
            guest_div.append('<div class="checkin"><a href="javascript:;">Check In</a></div>');
            guest_div.append('<div class="clear">&nbsp;</div>');
            $('div.list_content div.list_guests div.list_headers').after(guest_div);
            totalCount = parseInt($('div.checkin_count div.checkin_numbers span.total_guests').html()) + 1;
            $('div.checkin_count div.checkin_numbers span.total_guests').html(totalCount);
            $('div.list_content div.inner div.add_purchase').fadeIn();
          });
        } else {
          alert(response.message);
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
      var i, length, newLength, newLengthChecked, rsvp, targetValue, _i, _ref;
      length = $('div.guest').length;
      for (i = _i = 0, _ref = length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        rsvp = $('div.guest:eq(' + i + ')');
        targetValue = $(rsvp).find('div.' + param).html();
        if (targetValue.toLowerCase().indexOf(value.toLowerCase()) !== -1) {
          if (rsvp.data('ticket') === ticketType || ticketType === 'all') {
            $(rsvp).removeClass('hidden');
          }
        }
        if (checkStatus === 'checked_in') {
          if (!$(rsvp).hasClass('checked_in')) {
            $(rsvp).addClass('hidden');
          }
        }
        if (checkStatus === 'not_checked_in') {
          if ($(rsvp).hasClass('checked_in')) {
            $(rsvp).addClass('hidden');
          }
        }
      }
      if (updateListLength) {
        newLength = $('div.guest').not('.hidden').length;
        newLengthChecked = $('div.guest.checked_in').not('.hidden').length;
        $('div.checkin_count div.checkin_numbers span.total_guests').html(newLength);
        $('div.checkin_count div.checkin_numbers span.checked_in').html(newLengthChecked);
      }
      Bazaarboy.adjustBottomPosition();
    },
    debounce: function(func, threshold, execAsap) {
      var timeout;
      timeout = null;
      (function() {
        var args, delayed, obj;
        args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
        obj = this;
        delayed = function() {
          if (!execAsap) {
            func.apply(obj, args);
          }
          return timeout = null;
        };
        if (timeout) {
          clearTimeout(timeout);
        } else if (execAsap) {
          func.apply(obj, args);
        }
        return timeout = setTimeout(delayed, threshold || 100);
      });
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $("div.list_filters a.add_purchase_start").click(function(e) {
        e.preventDefault();
        $(this).fadeOut(300, function(e) {
          $("div.list_filters div.add_purchase").removeClass('hide');
        });
      });
      $('form.add_purchase_form a.add_purchase_submit').click(function(e) {
        var email, fullName, phone, ticket;
        if ($('form.add_purchase_form div.ticket_types a.active').length > 0) {
          ticket = $('form.add_purchase_form div.ticket_types a.active').attr('data-id');
          email = $('form.add_purchase_form input[name=guest_email]').val();
          fullName = $('form.add_purchase_form input[name=guest_name]').val();
          phone = $('form.add_purchase_form input[name=guest_phone]').val();
          if (email.trim() === '') {
            alert('You must enter a valid email address.');
            return;
          }
          if (fullName.trim() === '') {
            alert('You must enter your full name,');
            return;
          }
          if (phone.trim() === '') {
            phone = null;
          }
          scope.add_purchase(ticket, email, fullName, phone);
        } else {
          alert('No ticket selected.');
        }
      });
      $('form.add_purchase_form div.ticket_types a').click(function(e) {
        e.preventDefault();
        $('form.add_purchase_form div.ticket_types a').removeClass('active');
        $(this).addClass('active');
      });
      $('form.list_search input[name=guest_name]').keyup(function(e) {
        e.preventDefault();
        _this.debounce(console.log('bouncing herere'), 1000);
      });
      $('form.list_search input[name=guest_code]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_code]').val() === '') {
          $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          _this.filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), _this.selectionStatus, _this.checkinStatus, false);
        }
      });
      $('form.list_search div.ticket_filters a').click(function(e) {
        e.preventDefault();
        $('form.list_search div.ticket_filters a').removeClass('active');
        $(this).addClass('active');
        $('form.list_search input[name=guest_name]').val('');
        $('form.list_search input[name=guest_code]').val('');
        $('div.guest').addClass('hidden');
        scope.selectionStatus = $(this).data('id');
        scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true);
      });
      $('form.list_search div.checkin_filters a').click(function(e) {
        e.preventDefault();
        $('form.list_search div.checkin_filters a').removeClass('active');
        $(this).addClass('active');
        $('form.list_search input[name=guest_name]').val('');
        $('form.list_search input[name=guest_code]').val('');
        $('div.guest').addClass('hidden');
        scope.checkinStatus = $(this).data('status');
        scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true);
      });
      $('div.list_guests').on('click', 'div.guest div.checkin a', function(e) {
        var checkCount, guest, guest_id, totalCount;
        e.preventDefault();
        guest = $(this).parents('div.guest');
        guest_id = guest.data('id');
        if (!guest.hasClass('checked_in')) {
          checkCount = parseInt($('div.checkin_count div.checkin_numbers span.checked_in').html()) + 1;
          $('div.checkin_count div.checkin_numbers span.checked_in').html(checkCount);
          guest.addClass('checked_in');
          $(this).html('Arrived');
          scope.checkin(guest_id);
          if (scope.checkinStatus === 'not_checked_in') {
            guest.addClass('hidden');
            totalCount = parseInt($('div.checkin_count div.checkin_numbers span.total_guests').html()) - 1;
            $('div.checkin_count div.checkin_numbers span.total_guests').html(totalCount);
            $('div.checkin_count div.checkin_numbers span.checked_in').html('0');
            return Bazaarboy.adjustBottomPosition();
          }
        } else {
          checkCount = parseInt($('div.checkin_count div.checkin_numbers span.checked_in').html()) - 1;
          $('div.checkin_count div.checkin_numbers span.checked_in').html(checkCount);
          guest.removeClass('checked_in');
          $(this).html('Check In');
          scope.checkout(guest_id);
          if (scope.checkinStatus === 'checked_in') {
            guest.addClass('hidden');
            totalCount = parseInt($('div.checkin_count div.checkin_numbers span.total_guests').html()) - 1;
            $('div.checkin_count div.checkin_numbers span.total_guests').html(totalCount);
            $('div.checkin_count div.checkin_numbers span.checked_in').html(totalCount);
            return Bazaarboy.adjustBottomPosition();
          }
        }
      });
    }
  };

  Bazaarboy.event.manage.init();

}).call(this);
