(function() {
  Bazaarboy.reward.redeem = {
    redeeming: false,
    init: function() {
      var scope;
      scope = this;
      $('a.redeem-btn').click(function() {
        if (!scope.redeeming) {
          scope.redeeming = true;
          return Bazaarboy.post('rewards/redeem/', {
            claim_id: claim_id,
            token: claim_token
          }, function(response) {
            if (response.status === 'OK') {
              $('div.redemption-info').addClass('hide');
              $('div.redemption-success').removeClass('hide');
              swal({
                type: 'success',
                title: 'Redeemed!',
                text: 'The gift has been redeemed.'
              });
            } else {
              swal({
                type: 'warning',
                title: 'Oops',
                text: response.message
              });
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.redeem.init();

}).call(this);
