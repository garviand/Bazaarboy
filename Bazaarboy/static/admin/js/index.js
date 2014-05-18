(function() {
  Bazaarboy.admin.login = {
    searchProfiles: function(value) {
      Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var i, profiles, _i, _ref;
        if (response.status === 'OK') {
          profiles = response.profiles;
          console.log(profiles);
          if (profiles.length > 0) {
            $('.profile_login .profile_choices').empty();
            for (i = _i = 0, _ref = profiles.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
              $('.profile_login .profile_choices').append('<a href="javascript:;" data-id="' + profiles[i].pk + '">' + profiles[i].name + '</a>');
            }
          } else {
            $('.profile_login .profile_choices').empty();
          }
        }
      });
    },
    searchEvents: function(value) {
      Bazaarboy.get('event/search/', {
        keyword: value
      }, function(response) {
        var events, i, _i, _ref;
        if (response.status === 'OK') {
          events = response.events;
          if (events.length > 0) {
            $('.event_export .event_choices').empty();
            for (i = _i = 0, _ref = events.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
              $('.event_export .event_choices').append('<a href="/event/export/csv?id=' + events[i].pk + '">' + events[i].name + '</a>');
            }
          }
        }
      });
    },
    init: function() {
      var _this = this;
      $('.profile_login').on('click', '.profile_choices a', function(event) {
        var id;
        id = $(this).data('id');
        Bazaarboy.get('admin/login/profile/', {
          id: id
        }, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('index');
          } else {
            alert(response.message);
          }
        });
      });
      $('.profile_login .input_container input[name=profile_name]').keyup(function(event) {
        var value;
        value = $('.profile_login .input_container input[name=profile_name]').val();
        if (value) {
          _this.searchProfiles(value);
        } else {
          $('.profile_login .profile_choices').empty();
        }
      });
      $('div.event_export .input_container input[name=event_name]').keyup(function(event) {
        var value;
        value = $('div.event_export .input_container input[name=event_name]').val();
        if (value) {
          _this.searchEvents(value);
        } else {
          $('div.event_export .event_choices').empty();
        }
      });
    }
  };

  Bazaarboy.admin.login.init();

}).call(this);
