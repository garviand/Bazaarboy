(function() {
  Bazaarboy.admin.login = {
    filterProfiles: function(value) {
      var i, length, profile, targetValue, _i, _ref;
      length = $('.profile_login .profile_choices a').length;
      for (i = _i = 0, _ref = length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        profile = $('.profile_login .profile_choices a:eq(' + i + ')');
        targetValue = $(profile).html();
        if (targetValue.toLowerCase().indexOf(value.toLowerCase()) !== -1) {
          $(profile).removeClass('hidden');
        }
      }
    },
    init: function() {
      var _this = this;
      $('.profile_login .profile_choices a').click(function(event) {
        var id;
        id = $(this).data('id');
        Bazaarboy.get('admin/login/profile', {
          id: id
        }, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('index');
          } else {
            alert(response.message);
          }
        });
      });
      $('.profile_login .input_container input[name=profile_name').keyup(function(event) {
        event.preventDefault();
        if ($('.profile_login .input_container input[name=profile_name').val() === '') {
          $('.profile_login .profile_choices a').removeClass('hidden');
        } else {
          $('.profile_login .profile_choices a').addClass('hidden');
          _this.filterProfiles($('.profile_login .input_container input[name=profile_name').val());
        }
      });
    }
  };

  Bazaarboy.admin.login.init();

}).call(this);
