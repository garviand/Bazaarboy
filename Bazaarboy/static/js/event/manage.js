(function() {
  Bazaarboy.event.manage = {
    filterGuests: function(param, value) {
      var i, length, rsvp, targetValue, _i, _ref;
      length = $('div.guest').length;
      for (i = _i = 0, _ref = length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        rsvp = $('div.guest:eq(' + i + ')');
        targetValue = $(rsvp).find('div.' + param).html();
        if (targetValue.toLowerCase().indexOf(value.toLowerCase()) !== -1) {
          $(rsvp).removeClass('hidden');
        }
      }
    },
    init: function() {
      var _this = this;
      $('form.list_search input[name=guest_name]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_name]').val() === '') {
          return $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          return _this.filterGuests('name', $('form.list_search input[name=guest_name]').val());
        }
      });
      $('form.list_search input[name=guest_code]').keyup(function(e) {
        e.preventDefault();
        if ($('form.list_search input[name=guest_code]').val() === '') {
          return $('div.guest').removeClass('hidden');
        } else {
          $('div.guest').addClass('hidden');
          return _this.filterGuests('confirmation', $('form.list_search input[name=guest_code]').val());
        }
      });
    }
  };

  Bazaarboy.event.manage.init();

}).call(this);
