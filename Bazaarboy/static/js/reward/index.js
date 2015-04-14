(function() {
  Bazaarboy.reward.index = {
    sendingGift: false,
    search_organizers: function() {
      var organizerModel, value,
        _this = this;
      value = $('input[name=profile_search]').val();
      $('form.add-organizer-form div.organizer').remove();
      organizerModel = $('div.organizer-model');
      Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var i, newProfile, profiles, _i, _ref, _results;
        $('form.add-organizer-form div.searching').addClass('hide');
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
      $('a.transfer-inventory-start').click(function() {
        $('html, body').animate({
          scrollTop: $("div.catalog-rewards").offset().top
        }, 500);
      });
      $('a.discard-reward-item').click(function() {
        var discardItem, itemContainer, itemId;
        itemId = $(this).data('id');
        itemContainer = $(this).closest('div.reward-inventory');
        discardItem = false;
        if ($(this).data('type') === 'inventory') {
          swal({
            type: 'warning',
            title: 'Discard Inventory',
            text: 'Are you sure? If you discard this inventory, you will no longer be able to distribute it.',
            showCancelButton: true,
            confirmButtonText: "Discard",
            closeOnConfirm: false
          }, function() {
            return Bazaarboy.post('rewards/item/delete/', {
              item: itemId
            }, function(response) {
              if (response.status === 'OK') {
                swal({
                  title: 'Discarded',
                  text: 'The item has been discarded.'
                });
                itemContainer.remove();
              }
            });
          });
        }
        if ($(this).data('type') === 'giveaway') {
          swal({
            type: 'warning',
            title: 'End Giveaway',
            text: 'Are you sure? Note: all gifts already claimed will still be valid.',
            showCancelButton: true,
            confirmButtonText: "End Giveaway",
            closeOnConfirm: false
          }, function() {
            return Bazaarboy.post('rewards/item/delete/', {
              item: itemId
            }, function(response) {
              if (response.status === 'OK') {
                swal({
                  title: 'Discarded',
                  text: 'The item has been discarded.'
                });
                itemContainer.remove();
              }
            });
          });
        }
      });
      $('a.delete-reward').click(function() {
        var rewardContainer, rewardId;
        rewardId = $(this).data('id');
        rewardContainer = $(this).closest('.reward-catalog');
        swal({
          type: 'warning',
          title: 'Delete Listing',
          text: 'If you delete the listing, the items you have already sent will still be redeemable. You can manage the redemptions by clicking the \'Deleted Listings\' button.',
          showCancelButton: true,
          confirmButtonText: "Delete",
          closeOnConfirm: true
        }, function() {
          Bazaarboy.post('rewards/delete/', {
            reward: rewardId
          }, function(response) {
            if (response.status === 'OK') {
              swal({
                title: 'Deleted',
                text: 'The Listing has been deleted.'
              });
              rewardContainer.remove();
            }
          });
        });
      });
      $('a.show-deleted-rewards').click(function() {
        $('div.reward-catalog').removeClass('is-deleted');
        $(this).remove();
      });
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
            var newSent;
            if (response.status === 'OK') {
              swal({
                type: 'success',
                title: 'Gift Sent',
                text: 'The gift has been sent.'
              });
              $('div#distribute-reward-modal').foundation('reveal', 'close');
              button.html('Send Gift');
              scope.sendingGift = false;
              newSent = parseInt($('div.rewards div.reward-inventory[data-id=' + rewardItem + '] span.sent-number').html()) + 1;
              $('div.rewards div.reward-inventory[data-id=' + rewardItem + '] span.sent-number').html(newSent);
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
        $('div#send-reward-modal div.email-send').removeClass('hide');
        $('form.add-organizer-form div.organizer').remove();
        $(this).addClass('primary-btn');
        $(this).removeClass('primary-btn-inverse');
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
      $('input[name=profile_search]').bind('keypress', function() {
        $('form.add-organizer-form div.searching').removeClass('hide');
        $('form.add-organizer-form div.organizer').remove();
      });
      $('div#send-reward-modal a.send-via-email').click(function() {
        var email, expiration, expirationTime, quantity, rewardId;
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
              text: 'You sent ' + response.reward_send.quantity + ' \'' + response.reward_send.reward.name + '\' inventory to ' + response.reward_send.email
            }, function() {
              location.reload();
            });
          }
        });
      });
      $('body').on('click', 'a.add-reward-submit', function() {
        var expiration, expirationTime, ownerId, quantity, rewardId;
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
        ownerId = $(this).data('profile');
        Bazaarboy.post('rewards/item/add/', {
          reward: rewardId,
          owner: ownerId,
          quantity: quantity,
          expiration_time: expirationTime
        }, function(response) {
          var responseText;
          if (response.status === 'OK') {
            if (profileId === response.reward_item.owner.id) {
              responseText = 'You added ' + response.reward_item.quantity + ' \'' + response.reward_item.reward.name + '\' to your inventory';
            } else {
              responseText = 'You sent ' + response.reward_item.quantity + ' \'' + response.reward_item.reward.name + '\' inventory to ' + response.reward_item.owner.name;
            }
            swal({
              type: "success",
              title: 'Reward Sent',
              text: responseText
            }, function() {
              location.reload();
            });
          }
        });
      });
      $('body').on('click', 'a.add-giveaway', function() {
        var expiration, expirationTime, quantity, rewardId;
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
        swal({
          type: 'warning',
          title: 'Confirm Giveaway',
          text: 'Are you sure you want to give away ' + String(quantity) + ' items?',
          showCancelButton: true,
          confirmButtonText: "Create Giveaway",
          closeOnConfirm: false
        }, function() {
          return Bazaarboy.post('rewards/giveaway/create/', {
            reward: rewardId,
            quantity: quantity,
            expiration_time: expirationTime
          }, function(response) {
            if (response.status === 'OK') {
              swal({
                type: 'success',
                title: 'Giveaway Created',
                text: 'Your giveaway link: https://bazaarboy.com/giveaway/' + response.giveaway.token + ' - Would you like to view the giveaway now?',
                showCancelButton: true,
                confirmButtonText: "View Giveaway",
                cancelButtonText: "Close",
                closeOnConfirm: true
              }, function(isConfirm) {
                if (isConfirm) {
                  Bazaarboy.redirect('giveaway/' + response.giveaway.token);
                } else {
                  location.reload();
                }
              });
            } else {
              swal({
                type: 'warning',
                title: 'Giveaway Creation Error',
                text: response.message
              });
            }
          });
        });
      });
    }
  };

  Bazaarboy.reward.index.init();

}).call(this);
