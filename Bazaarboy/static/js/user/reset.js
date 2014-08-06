(function() {
  this.Bazaarboy.user.reset = {
    init: function() {
      $('form#reset-form').submit(function(event) {
        var params;
        event.preventDefault();
        $('input.submit-reset').val('Sending...');
        params = $('form#reset-form').serializeObject();
        Bazaarboy.post('user/reset/create/', params, function(response) {
          if (response.status === 'OK') {
            return $('form#reset-form div.reset-form-content').fadeOut(300, function() {
              $('form#reset-form div.reset-form-confirmation').fadeIn(300);
            });
          } else {
            alert(response.message);
            return $('input.submit-reset').val('Send Reset Request');
          }
        });
      });
      $('form#password-form').submit(function(event) {
        var params;
        event.preventDefault();
        $('input.submit-password').val('Changing Password...');
        params = $('form#password-form').serializeObject();
        Bazaarboy.post('user/password/change/', params, function(response) {
          if (response.status === 'OK') {
            return $('form#password-form div.password-form-content').fadeOut(300, function() {
              $('form#password-form div.password-form-confirmation').fadeIn(300);
            });
          } else {
            alert(response.message);
            return $('input.submit-password').val('Reset Password');
          }
        });
      });
    }
  };

  this.Bazaarboy.user.reset.init();

}).call(this);
