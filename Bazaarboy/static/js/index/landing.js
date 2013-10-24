(function() {
  this.Bazaarboy.landing = {
    init: function() {
      $('form[name=login] input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form[name=login]').submit();
        }
      });
      $('#landing .inner .login_content .bottom a.login_btn').click(function() {
        $('form[name=login]').submit();
      });
      $('form[name=login]').submit(function(event) {
        var params;
        console.log("log in now");
        event.preventDefault();
        params = $('form[name=login]').serialize();
        Bazaarboy.get('user/auth/', params, function(response) {
          if (response.status === 'OK') {
            return Bazaarboy.redirect('index');
          } else {
            return alert(response.message);
          }
        });
      });
      $('#landing .inner .starting_content .bottom .login_link_container .start_sign_in').click(function() {
        $('#landing .inner .starting_content').addClass('hidden');
        $('#landing .inner .login_content').removeClass('hidden');
      });
      $('#landing .inner .login_content .bottom a.back').click(function() {
        $('#landing .inner .login_content').addClass('hidden');
        $('#landing .inner .starting_content').removeClass('hidden');
      });
    }
  };

  Bazaarboy.landing.init();

}).call(this);
