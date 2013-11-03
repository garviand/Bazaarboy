(function() {
  var _this = this;

  Bazaarboy.event.manage = {
    selectionStatus: 'all',
    checkin: function(guest_id) {
      Bazaarboy.post('event/checkin/', {
        id: guest_id
      }, function(response) {});
    },
    filterGuests: function(param, value, ticketType, updateListLength) {
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
      }
      if (updateListLength) {
        newLength = $('div.guest').not('.hidden').length;
        newLengthChecked = $('div.guest.checked_in').not('.hidden').length;
        $('div.checkin_count div.checkin_numbers span.total_guests').html(newLength);
        $('div.checkin_count div.checkin_numbers span.checked_in').html(newLengthChecked);
      }
      Bazaarboy.adjustBottomPosition();
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('form.list_search input[name=guest_name]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_name]').val() === '') {
          $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          _this.filterGuests('name', $('form.list_search input[name=guest_name]').val(), _this.selectionStatus, false);
        }
      });
      $('form.list_search input[name=guest_code]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_code]').val() === '') {
          $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          _this.filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), _this.selectionStatus, false);
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
        scope.filterGuests('name', '', scope.selectionStatus, true);
      });
      $('div.list_guests div.guest div.checkin a').click(function(e) {
        var checkCount, guest, guest_id;
        e.preventDefault();
        guest = $(this).parents('div.guest');
        guest_id = guest.data('id');
        if (!guest.hasClass('checked_in')) {
          checkCount = parseInt($('div.checkin_count div.checkin_numbers span.checked_in').html()) + 1;
          $('div.checkin_count div.checkin_numbers span.checked_in').html(checkCount);
          guest.addClass('checked_in');
          $(this).html('Arrived');
          return scope.checkin(guest_id);
        }
      });
    }
  };

  Bazaarboy.event.manage.init();

}).call(this);
