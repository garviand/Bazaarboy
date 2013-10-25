(function() {
  this.Bazaarboy.landing = {
    init: function() {
      $('form[name=login] input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form[name=login]').submit();
        }
      });
      $('#landing div.login_content a.login_btn').click(function() {
        $('form[name=login]').submit();
      });
      $('form[name=login]').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form[name=login]').serializeObject();
        if (params.email.trim().length !== 0 && params.password.trim().length !== 0) {
          Bazaarboy.get('user/auth/', params, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('index');
            } else {
              alert(response.message);
            }
          });
        }
      });
      $('#landing div.starting_content a.start_sign_in').click(function() {
        $('#landing div.starting_content').addClass('hidden');
        $('#landing div.login_content').removeClass('hidden');
      });
      $('#landing div.login_content a.back').click(function() {
        $('#landing div.login_content').addClass('hidden');
        $('#landing div.starting_content').removeClass('hidden');
      });
    }
  };

  Bazaarboy.landing.init();

}).call(this);
