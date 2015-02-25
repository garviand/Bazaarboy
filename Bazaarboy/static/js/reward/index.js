(function() {
  Bazaarboy.reward.index = {
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
      $('body').on('click', 'a.create-subscription', function() {
        $('div#add-subscription-modal').foundation('reveal', 'open');
      });
      $('div#add-subscription-modal a.create-subscription').click(function() {
        var _this = this;
        StripeCheckout.open({
          key: publishableKey,
          address: false,
          amount: 0,
          currency: 'usd',
          name: 'Bazaarboy Gifts Account',
          description: 'Create Account',
          panelLabel: 'Subscribe',
          closed: function() {
            $('div#add-subscription-modal').foundation('reveal', 'close');
          },
          token: function(token) {
            Bazaarboy.post('rewards/subscribe/', {
              stripe_token: token.id,
              email: token.email,
              profile: profileId
            }, function(response) {
              if (response.status === 'OK') {
                swal({
                  type: "success",
                  title: 'Subscribed!',
                  text: 'You have successfully subscribed for a Bazaarboy Gifts account. You will not be charged for the first 10 claimed items, so gift away!'
                }, function() {
                  $('a.create-subscription').addClass('send-reward-btn');
                  $('a.create-subscription').removeClass('create-subscription');
                  $('div#add-subscription-modal').foundation('reveal', 'close');
                });
              } else {
                alert(response.message);
              }
            });
          }
        });
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
      $('body').on('click', 'a.add-reward-submit', function() {
        var expiration, expirationTime, profileId, quantity, rewardId;
        if (!$.isNumeric($('input[name=quantity]').val()) || $('input[name=quantity]').val() <= 0) {
          swal('Quantity Must Be a Positive Number');
          return;
        }
        quantity = Math.floor($('input[name=quantity]').val());
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
              $('form.add-organizer-form div.organizer').remove();
              $('input[name=profile_search]').val('');
              $('input[name=expiration]').val('');
              $('input[name=quantity]').val('');
            });
          }
        });
      });
    }
  };

  Bazaarboy.reward.index.init();

}).call(this);
