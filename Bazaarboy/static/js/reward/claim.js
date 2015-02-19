(function() {
  Bazaarboy.reward.claim = {
    init: function() {
      var scope;
      scope = this;
      $('form#claim-form').submit(function(e) {
        var params;
        e.preventDefault();
        params = $('form#claim-form').serializeObject();
        if (params.phone.trim() === '') {
          params.phone = void 0;
        }
        if (params.first_name === '') {
          swal('Must Enter A First Name');
          return;
        }
        if (params.last_name === '') {
          swal('Must Enter A Last Name');
          return;
        }
        if (params.email === '') {
          swal('Must Enter An Email');
          return;
        }
        return Bazaarboy.post('rewards/claim/complete/', params, function(response) {
          if (response.status === 'OK') {
            return console.log(response);
          } else {
            return console.log(response.message);
          }
        });
      });
    }
  };

  Bazaarboy.reward.claim.init();

}).call(this);
