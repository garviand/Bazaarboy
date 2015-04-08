(function() {
  Bazaarboy.reward.index = {
    sendingGift: false,
    search_organizers: function() {
      var organizerModel, value,
        _this = this;
      value = $('input[name=profile_search]').val();
      $('form.add-organizer-form div.organizer').remove();
      organizerModel = $('div.organizer-model');
      return Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var i, newProfile, profiles, _i, _ref, _results;
        if (response.status === 'OK') {
          profiles = response.profiles;
          if (profiles.length > 0) {
            _results = [];
            for (i = _i = 0, _ref = profiles.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
              newProfile = organizerModel;
              newProfile.find('div.organizer-name').html(profiles[i].name);
              if (profiles[i].image_url != null) {
                newProfile.find('div.organizer-image').html('<img src=' + profiles[i].image_url + ' />');
              } else {
                newProfile.find('div.organizer-image').html('&nbsp;');
              }
              newProfile.find('a.add-reward-submit').attr('data-profile', profiles[i].pk);
              _results.push($('form.add-organizer-form').append(newProfile.html()));
            }
            return _results;
          }
        }
      });
    },
    init: function() {
      var add_organizer_debounce, scope;
      scope = this;
      /*
      if totalSent > 9 or hasSubscription
        $('span.free_gifts').addClass('hide')
      # SUBSCRIPTION
      $('a.cancel-subscription').click () ->
        $('div#add-subscription-modal').foundation('reveal', 'close')
        return
      $('div#add-subscription-modal a.create-subscription').click () ->
        StripeCheckout.open
          key: publishableKey
          address: false
          amount: 0
          currency: 'usd'
          name: 'Bazaarboy Gifts Account'
          description: 'Create Account'
          panelLabel: 'Subscribe'
          closed: () ->
            $('div#add-subscription-modal').foundation('reveal', 'close')
            return
          token: (token) =>
            Bazaarboy.post 'rewards/subscribe/',
              stripe_token: token.id
              email: token.email
              profile: profileId
            , (response) =>
              if response.status is 'OK'
                swal
                  type: "success"
                  title: 'Subscribed!'
                  text: 'You have successfully subscribed for a Bazaarboy account!'
                  , () ->
                    location.reload()
                    return
              else
                alert response.message
              return
            return
        return
      */

      $('div.reward a.send-gift-item').click(function() {
        var rewardItemId, rewardItemName;
        rewardItemId = $(this).data('id');
        rewardItemName = $(this).data('name');
        $('div#distribute-reward-modal input[name=reward_item_id]').val(rewardItemId);
        $('div#distribute-reward-modal span.reward-name').html(rewardItemName);
        $('div#distribute-reward-modal').foundation('reveal', 'open');
      });
      $('div#distribute-reward-modal a.send-gift-btn').click(function() {
        var button, rewardEmail, rewardItem, rewardMessage;
        if (!scope.sendingGift) {
          button = $(this);
          button.html('Sending...');
          scope.sendingGift = true;
          rewardEmail = $('div#distribute-reward-modal input[name=email_distribute]').val();
          rewardMessage = $('div#distribute-reward-modal textarea[name=email_message]').val();
          rewardItem = $('div#distribute-reward-modal input[name=reward_item_id]').val();
          if (rewardEmail.trim() === '') {
            swal('Must Enter an Email');
            scope.sendingGift = false;
            return;
          }
          Bazaarboy.post('rewards/claim/add/', {
            item: rewardItem,
            email: rewardEmail,
            message: rewardMessage
          }, function(response) {
            if (response.status === 'OK') {
              swal({
                type: 'success',
                title: 'Gift Sent',
                text: 'The gift has been sent.'
              });
              $('div#distribute-reward-modal').foundation('reveal', 'close');
              button.html('Send Gift');
              scope.sendingGift = false;
              $('div.rewards div.reward[data-id=' + rewardItem + '] span.quantity').html(response.reward_item.quantity);
              $('div#distribute-reward-modal input[name=email_distribute]').val('');
            } else {
              swal(response.message);
              button.html('Send Gift');
              scope.sendingGift = false;
            }
          });
        }
      });
      $('div#send-reward-modal a.add-reward-profile').click(function() {
        $('div#send-reward-modal div.profile-search').removeClass('hide');
        $('div#send-reward-modal div.email-send').addClass('hide');
        $(this).addClass('primary-btn');
        $(this).removeClass('primary-btn-inverse');
        $('div#send-reward-modal a.add-reward-email').removeClass('primary-btn');
        $('div#send-reward-modal a.add-reward-email').addClass('primary-btn-inverse');
      });
      $('div#send-reward-modal a.add-reward-email').click(function() {
        $('div#send-reward-modal form.add-organizer-form').empty();
        $('div#send-reward-modal div.email-send').removeClass('hide');
        $('div#send-reward-modal div.profile-search').addClass('hide');
        $(this).addClass('primary-btn');
        $(this).removeClass('primary-btn-inverse');
        $('div#send-reward-modal a.add-reward-profile').removeClass('primary-btn');
        $('div#send-reward-modal a.add-reward-profile').addClass('primary-btn-inverse');
      });
      $('body').on('click', 'a.send-reward-btn', function() {
        $('input[name=reward_id]').val($(this).data('id'));
        $('div#send-reward-modal span.reward-name').html($(this).data('name'));
        $('div#send-reward-modal').foundation('reveal', 'open');
      });
      $('input[name=expiration]').pikaday({
        format: 'MM/DD/YYYY'
      });
      add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers);
      $('input[name=profile_search]').bind('keypress', add_organizer_debounce);
      $('div#send-reward-modal a.send-via-email').click(function() {
        var email, expiration, expirationTime, quantity, rewardId;
        if (!$.isNumeric($('input[name=quantity]').val()) || $('input[name=quantity]').val() <= 0) {
          swal('Quantity Must Be a Positive Number');
          return;
        }
        quantity = Math.floor($('input[name=quantity]').val());
        /*
        if (10 - totalSent) < quantity and not hasSubscription
          swal
            type: "warning"
            title: "Trial Exceeded"
            text: "You do not have enough free gifts left to send this much inventory. Subscribe to a Bazaarboy account now?"
            showCancelButton: true
            confirmButtonText: 'Subscribe'
            cancelButtonText: 'Cancel'
            , (isConfirm) ->
              if isConfirm
                $('div#add-subscription-modal').foundation('reveal', 'open')
              return
          return
        */

        expiration = $('input[name=expiration]').val();
        if (!moment(expiration, 'MM/DD/YYYY').isValid()) {
          swal('Expiration Date is Not Valid');
          return;
        }
        expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
        rewardId = $('input[name=reward_id]').val();
        email = $('div#send-reward-modal input[name=email_send]').val();
        if (email.trim() === '') {
          swal('Must Enter An Email');
          return;
        }
        Bazaarboy.post('rewards/item/add/', {
          reward: rewardId,
          email: email,
          quantity: quantity,
          expiration_time: expirationTime
        }, function(response) {
          if (response.status === 'OK') {
            return swal({
              type: "success",
              title: 'Reward Sent',
              text: 'You sent ' + response.reward_send.quantity + ' \'' + response.reward_send.reward.name + '\' rewards to ' + response.reward_send.email
            }, function() {
              location.reload();
            });
          }
        });
      });
      $('body').on('click', 'a.add-reward-submit', function() {
        var expiration, expirationTime, profileId, quantity, rewardId;
        if (!$.isNumeric($('input[name=quantity]').val()) || $('input[name=quantity]').val() <= 0) {
          swal('Quantity Must Be a Positive Number');
          return;
        }
        quantity = Math.floor($('input[name=quantity]').val());
        /*
        if (10 - totalSent) < quantity and not hasSubscription
          swal
            type: "warning"
            title: "Trial Exceeded"
            text: "You do not have enough free gifts left to send this much inventory. Subscribe to a Bazaarboy account now?"
            showCancelButton: true
            confirmButtonText: 'Subscribe'
            cancelButtonText: 'Cancel'
            , (isConfirm) ->
              if isConfirm
                $('div#add-subscription-modal').foundation('reveal', 'open')
              return
          return
        */

        expiration = $('input[name=expiration]').val();
        if (!moment(expiration, 'MM/DD/YYYY').isValid()) {
          swal('Expiration Date is Not Valid');
          return;
        }
        expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
        rewardId = $('input[name=reward_id]').val();
        profileId = $(this).data('profile');
        Bazaarboy.post('rewards/item/add/', {
          reward: rewardId,
          owner: profileId,
          quantity: quantity,
          expiration_time: expirationTime
        }, function(response) {
          if (response.status === 'OK') {
            swal({
              type: "success",
              title: 'Reward Sent',
              text: 'You sent ' + response.reward_item.quantity + ' \'' + response.reward_item.reward.name + '\' rewards to ' + response.reward_item.owner.name
            }, function() {
              location.reload();
            });
          }
        });
      });
    }
  };

  Bazaarboy.reward.index.init();

}).call(this);
