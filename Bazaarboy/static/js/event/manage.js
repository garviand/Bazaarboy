(function() {
  Bazaarboy.event.manage = {
    selectionStatus: 'all',
    filterGuests: function(param, value, ticketType) {
      var i, length, rsvp, targetValue, _i, _ref;
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
          _this.filterGuests('name', $('form.list_search input[name=guest_name]').val(), _this.selectionStatus);
        }
      });
      $('form.list_search input[name=guest_code]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_code]').val() === '') {
          $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          _this.filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), _this.selectionStatus);
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
        return scope.filterGuests('name', '', scope.selectionStatus);
      });
    }
  };

  Bazaarboy.event.manage.init();

}).call(this);
