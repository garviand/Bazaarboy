(function() {
  Bazaarboy.reward.claim = {
    claiming: false,
    init: function() {
      var scope;
      scope = this;
      $('form#claim-form').submit(function(e) {
        var params;
        if (!scope.claiming) {
          scope.claiming = true;
          $('input.submit-claim').val('Claiming...');
          e.preventDefault();
          params = $('form#claim-form').serializeObject();
          if (params.phone.trim() === '') {
            params.phone = void 0;
          }
          if (params.first_name === '') {
            swal('Must Enter A First Name');
            $('input.submit-claim').val('Claim Reward!');
            scope.claiming = false;
            return;
          }
          if (params.last_name === '') {
            swal('Must Enter A Last Name');
            $('input.submit-claim').val('Claim Reward!');
            scope.claiming = false;
            return;
          }
          if (params.email === '') {
            swal('Must Enter An Email');
            $('input.submit-claim').val('Claim Reward!');
            scope.claiming = false;
            return;
          }
          Bazaarboy.post('rewards/claim/complete/', params, function(response) {
            scope.claiming = false;
            $('input.submit-claim').val('Claim Reward!');
            if (response.status === 'OK') {
              $('div.claim-success b.code').html(response.claim.code);
              $('div.claim-inputs').addClass('hide');
              return $('div.claim-success').removeClass('hide');
            } else {
              return swal(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.claim.init();

}).call(this);
