(function() {
  Bazaarboy.reward.redeem = {
    redeeming: false,
    init: function() {
      var scope;
      scope = this;
      $('a.redeem-btn').click(function() {
        $('form#redeem-form').submit();
      });
      $('form#redeem-form').submit(function(e) {
        e.preventDefault();
        if (!scope.redeeming) {
          scope.redeeming = true;
          swal({
            type: 'warning',
            title: 'You Sure?',
            text: 'DO NOT REDEEM unless you are the gift provider.',
            showCancelButton: true,
            confirmButtonText: "Yes, Redeem",
            closeOnConfirm: true,
            animation: false
          }, function() {
            return Bazaarboy.post('rewards/redeem/', {
              claim_id: claim_id,
              token: claim_token
            }, function(response) {
              if (response.status === 'OK') {
                $('div.redemption-info').addClass('hide');
                $('div.redemption-success').removeClass('hide');
              } else {
                swal({
                  type: 'warning',
                  title: 'Oops',
                  text: response.message
                });
              }
            });
          });
          return scope.redeeming = false;
        }
      });
    }
  };

  Bazaarboy.reward.redeem.init();

}).call(this);
