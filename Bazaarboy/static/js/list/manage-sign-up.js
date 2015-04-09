(function() {
  Bazaarboy.list.manage_sign_up = {
    init: function() {
      var scope;
      scope = this;
      $('a.reward-member').click(function() {
        $("div#rewards-modal").foundation('reveal', 'open');
        $("div#rewards-modal input[name=reward_email]").val($(this).data('email'));
        $("div#rewards-modal span.reward-reciever").html($(this).data('first') + ' ' + $(this).data('last'));
      });
      $('a.send-reward').click(function() {
        var button, quantityAmount, quantityElement, rewardEmail, rewardId, rewardMessage;
        button = $(this);
        button.html('Sending...');
        rewardId = $(this).data('id');
        rewardEmail = $("div#rewards-modal input[name=reward_email]").val();
        rewardMessage = $('div#rewards-modal textarea[name=message]').val();
        quantityElement = $(this).closest('.reward').find('span.quantity');
        quantityAmount = parseInt(quantityElement.html());
        return Bazaarboy.post('rewards/claim/add/', {
          item: rewardId,
          email: rewardEmail,
          message: rewardMessage
        }, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Reward Sent',
              text: 'The reward has been sent.'
            });
            quantityElement.html(quantityAmount - 1);
            $('div.gifted[data-email="' + rewardEmail + '"]').removeClass('hide');
            $("div#rewards-modal").foundation('reveal', 'close');
            button.html('Send Reward');
          } else {
            swal(response.message);
            button.html('Send Reward');
          }
        });
      });
      $("a.raffle-btn").click(function(e) {
        var winner, winner_email, winner_id, winner_name;
        e.preventDefault();
        winner_id = Math.floor(Math.random() * ($("div.sign-ups div.sign-up").length));
        winner = $('div.sign-ups div.sign-up').eq(winner_id);
        winner_name = winner.attr('data-name');
        winner_email = winner.attr('data-email');
        $('div#raffle-modal div.subtext-name').html(winner_name);
        $('div#raffle-modal div.subtext-email').html(winner_email);
        $('div#rewards-modal input[name=reward_email]').val(winner_email);
        $('div#rewards-modal span.reward-reciever').html(winner_name);
        $('div#raffle-modal').foundation('reveal', 'open');
      });
      $('a.show-rewards-btn').click(function() {
        $("div#rewards-modal").foundation('reveal', 'open');
      });
      $('a.add-to-list-btn').click(function(e) {
        $('div#add-list-modal').foundation('reveal', 'open');
      });
      $('div#add-list-modal a.add-cancel-btn').click(function(e) {
        $('div#add-list-modal').foundation('reveal', 'close');
      });
      $('a.add-to-list-single-btn').click(function(e) {
        $('div#add-list-single-modal input[name=email]').val($(this).data('email'));
        $('div#add-list-single-modal input[name=first_name]').val($(this).data('first'));
        $('div#add-list-single-modal input[name=last_name]').val($(this).data('last'));
        $('div#add-list-single-modal').foundation('reveal', 'open');
      });
      $('div#add-list-single-modal a.add-cancel-btn').click(function(e) {
        $('div#add-list-single-modal').foundation('reveal', 'close');
      });
      $('body').on('click', 'div#add-list-modal div.list, div#add-list-single-modal div.list', function(e) {
        $(this).toggleClass('active');
      });
      $('div#add-list-modal a.create-list').click(function() {
        var list_name, profileId, signupId;
        $('div#add-list-modal div.status').html('Creating...');
        $('div#add-list-modal div.submit-actions a').css('display', 'none');
        profileId = $('div#add-list-modal input[name=profile_id]').val();
        signupId = $('div#add-list-modal input[name=signup_id]').val();
        list_name = $('div#add-list-modal input[name=list_name]').val();
        if (list_name.trim() !== '') {
          Bazaarboy.post('lists/create/', {
            profile: profileId,
            name: list_name,
            is_hidden: 1
          }, function(response) {
            var listId;
            if (response.status === 'OK') {
              listId = response.list.pk;
              $('div#add-list-modal div.status').html('Successfully Created List! Adding Members...');
              Bazaarboy.post('lists/add/signup/', {
                id: listId,
                signup: signupId
              }, function(response) {
                var newList;
                if (response.status === 'OK') {
                  newList = $('div.list-template').clone();
                  newList.attr('data-id', response.list.pk);
                  newList.find('div.list-name').html(response.list.name);
                  newList.find('div.list-action').html(response.added + ' Members');
                  newList.removeClass('hide');
                  $('div#add-list-modal div.lists').prepend(newList);
                  $('div#add-list-modal div.status').html('Congrats! List was Created and ' + response.added + ' People were added.');
                } else {
                  swal('List Was Created, But there was an error: ' + response.message);
                }
                $('div#add-list-modal div.submit-actions a').css('display', 'block');
              });
            } else {
              swal('Could not create list');
              $('div#add-list-modal div.submit-actions a').css('display', 'block');
            }
            $('div#add-list-modal input[name=list_name]').val('');
          });
        } else {
          swal('List name can\'t be empty');
          $('div#add-list-modal div.submit-actions a').css('display', 'block');
        }
      });
      $('div#add-list-modal a.submit-add-btn').click(function() {
        var error_lists, num_finished, num_lists, selected_lists, signupId;
        $('div#add-list-modal div.status').html('Adding People to Lists...');
        $('div#add-list-modal div.submit-actions a').css('display', 'none');
        signupId = $('div#add-list-modal input[name=signup_id]').val();
        selected_lists = $('div#add-list-modal div.lists div.list.active');
        num_lists = selected_lists.length;
        error_lists = 0;
        num_finished = 0;
        if (num_lists > 0) {
          $.each(selected_lists, function(list) {
            Bazaarboy.post('lists/add/signup/', {
              id: $(this).data('id'),
              signup: signupId
            }, function(response) {
              if (response.status === 'OK') {
                $('div#add-list-modal div.status').html(num_finished + ' Lists Complete - ' + (num_lists - num_finished) + ' Lists Remaining');
              } else {
                error_lists++;
              }
              num_finished++;
              if ((num_lists - num_finished) === 0) {
                if (error_lists > 0) {
                  swal('Lists added, but some people may have been left out');
                } else {
                  swal({
                    title: "Success",
                    text: "The Sign Ups have been Added!",
                    type: "success"
                  }, function() {
                    $('div#add-list-modal').foundation('reveal', 'close');
                  });
                }
                $('div#add-list-modal div.status').html('&nbsp;');
                $('div#add-list-modal div.submit-actions a').css('display', 'block');
              }
            });
          });
        } else {
          swal('You Must Select at least One List!');
        }
      });
      $('div#add-list-single-modal a.submit-add-btn').click(function() {
        var error_lists, num_finished, num_lists, selected_lists, signupId, thisEmail, thisFirst, thisLast;
        $('div#add-list-single-modal div.status').html('Adding People to Lists...');
        $('div#add-list-single-modal div.submit-actions a').css('display', 'none');
        signupId = $('div#add-list-single-modal input[name=signup_id]').val();
        selected_lists = $('div#add-list-single-modal div.lists div.list.active');
        thisEmail = $('div#add-list-single-modal input[name=email]').val();
        thisFirst = $('div#add-list-single-modal input[name=first_name]').val();
        thisLast = $('div#add-list-single-modal input[name=last_name]').val();
        num_lists = selected_lists.length;
        error_lists = 0;
        num_finished = 0;
        if (num_lists > 0) {
          $.each(selected_lists, function(list) {
            Bazaarboy.post('lists/add/item/', {
              id: $(this).data('id'),
              email: thisEmail,
              first_name: thisFirst,
              last_name: thisLast
            }, function(response) {
              if (response.status === 'OK') {
                $('div#add-list-single-modal div.status').html(num_finished + ' Lists Complete - ' + (num_lists - num_finished) + ' Lists Remaining');
              } else {
                error_lists++;
              }
              num_finished++;
              if ((num_lists - num_finished) === 0) {
                if (error_lists > 0) {
                  swal('Lists added, but some errors may have occured');
                } else {
                  swal({
                    title: "Success",
                    text: "Added to lists!",
                    type: "success"
                  }, function() {
                    $('div#add-list-single-modal').foundation('reveal', 'close');
                  });
                }
                $('div#add-list-single-modal div.status').html('&nbsp;');
                $('div#add-list-single-modal div.submit-actions a').css('display', 'block');
              }
            });
          });
        } else {
          swal('You Must Select at least One List!');
        }
      });
    }
  };

  Bazaarboy.list.manage_sign_up.init();

}).call(this);
