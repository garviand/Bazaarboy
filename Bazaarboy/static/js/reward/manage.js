(function() {
  Bazaarboy.reward.manage = {
    init: function() {
      var scope;
      scope = this;
      $('input[name=reward_name], input[name=reward_email], input[name=reward_code]').keyup(function() {
        var searchType, searchVal;
        searchType = $(this).data('type');
        $('input[data-type!=' + searchType + ']').val('');
        searchVal = $(this).val().toLowerCase();
        console.log(searchType, searchVal);
        if (searchVal.trim() !== '') {
          $('div.rewards div.reward').addClass('hide');
          $('div.rewards div.reward[data-' + searchType + '*="' + searchVal + '"]').removeClass('hide');
        } else {
          $('div.rewards div.reward').removeClass('hide');
        }
      });
      $('div.reward div.redeem a').click(function() {
        var button, claimId;
        button = $(this);
        button.html('Redeeming');
        claimId = $(this).closest('div.reward').data('id');
        Bazaarboy.post('rewards/redeem/', {
          claim_id: claimId
        }, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Reward Redeemed!',
              text: 'The reward has been redeemed. It is not longer valid.'
            });
            button.html('Redeemed');
            button.removeClass('secondary-btn');
            return button.addClass('disabled-btn');
          } else {
            swal(response.message);
            return button.html('Redeem');
          }
        });
        return;
      });
    }
  };

  Bazaarboy.reward.manage.init();

}).call(this);
