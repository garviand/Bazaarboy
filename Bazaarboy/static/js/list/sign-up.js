(function() {
  Bazaarboy.list.sign_up = {
    init: function() {
      var scope;
      scope = this;
      $('form#sign-up-form').submit(function(e) {
        var extra_fields, field_missing, field_missing_name, params;
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
        field_missing = false;
        extra_fields = {};
        field_missing_name = '';
        $('input.extra-field').each(function() {
          if ($(this).val().trim() === '') {
            field_missing = true;
            field_missing_name = $(this).data('field');
            console.log(field_missing_name);
          }
          extra_fields[$(this).data('field')] = $(this).val();
        });
        if (field_missing) {
          swal(field_missing_name + ' Cannot Be Blank');
          $('input.submit-claim').val('Claim Reward!');
          scope.claiming = false;
          return;
        }
        params.extra_fields = JSON.stringify(extra_fields);
        Bazaarboy.post('lists/signup/submit/', params, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Success!',
              text: 'Your info has been submitted. Thanks!'
            }, function() {
              $('input[type=text]').val('');
            });
          } else {
            swal({
              type: 'warning',
              title: 'Oops!',
              text: response.message
            });
          }
        });
      });
    }
  };

  Bazaarboy.list.sign_up.init();

}).call(this);
