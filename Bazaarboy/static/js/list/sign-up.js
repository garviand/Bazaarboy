(function() {
  Bazaarboy.list.sign_up = {
    init: function() {
      var scope;
      scope = this;
      $('form#sign-up-form').submit(function(e) {
        var params;
        e.preventDefault();
        params = {};
        params.sign_up = signup;
        if ($('input[name=first_name]').val().trim() === '') {
          swal('You Must Add a First Name');
          return;
        }
        params.first_name = $('input[name=first_name]').val();
        if ($('input[name=last_name]').val().trim() === '') {
          swal('You Must Add a Last Name');
          return;
        }
        params.last_name = $('input[name=last_name]').val();
        if ($('input[name=email]').val().trim() === '') {
          swal('You Must Add an Email');
          return;
        }
        params.email = $('input[name=email]').val();
        Bazaarboy.post('lists/signup/submit/', params, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Success!',
              text: 'Your info has been submitted. Thanks!'
            }, function() {
              $('input[type=text]').val('');
            });
          }
        });
      });
    }
  };

  Bazaarboy.list.sign_up.init();

}).call(this);
