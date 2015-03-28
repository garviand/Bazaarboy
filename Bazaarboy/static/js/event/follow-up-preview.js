(function() {
  Bazaarboy.event.follow_up_preview = {
    sending: false,
    sendEmail: function(followUpId) {
      Bazaarboy.post('event/followup/send/', {
        id: followUpId
      }, function(response) {
        var _this = this;
        if (response.status === 'OK') {
          console.log(response);
          Bazaarboy.redirect('event/followup/' + response.follow_up.pk + '/details/');
        } else if (response.status === 'SUBSCRIBE') {
          $('div#add-subscription-modal').foundation('reveal', 'open');
        } else if (response.status === 'PAYMENT') {
          StripeCheckout.open({
            key: response.publishable_key,
            address: false,
            amount: response.cost,
            currency: 'usd',
            name: 'Send Follow Ups',
            description: response.sent + ' Follow Ups - ' + response.event.name,
            panelLabel: 'Send Now',
            image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png',
            closed: function() {
              Bazaarboy.event.follow_up_preview.sending = false;
              $('div.email-actions a.send-email').html('Send Email');
            },
            token: function(token) {
              Bazaarboy.post('payment/charge/followup/', {
                follow_up: response.follow_up.pk,
                stripe_token: token.id,
                amount: response.cost
              }, function(response) {
                if (response.status === 'OK') {
                  Bazaarboy.event.follow_up_preview.sending = true;
                  $('div.email-actions a.send-email').html('Sending...');
                  Bazaarboy.event.follow_up_preview.sendEmail(response.follow_up.pk);
                } else {
                  swal(response.message);
                  Bazaarboy.event.follow_up_preview.sending = false;
                  $('div.email-actions a.send-email').html('Send Email');
                }
              });
            }
          });
        } else {
          swal(response.message);
          Bazaarboy.event.follow_up_preview.sending = false;
          $('div.email-actions a.send-email').html('Send Email');
        }
      });
    },
    init: function() {
      var scope;
      scope = this;
      $('a.cancel-subscription').click(function() {
        $('div#add-subscription-modal').foundation('reveal', 'close');
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
            return Bazaarboy.post('rewards/subscribe/', {
              stripe_token: token.id,
              email: token.email,
              profile: profileId
            }, function(response) {
              if (response.status === 'OK') {
                swal({
                  type: "success",
                  title: 'Subscribed!',
                  text: 'You have successfully subscribed for a Bazaarboy account!'
                }, function() {
                  location.reload();
                });
              } else {
                alert(response.message);
              }
            });
          }
        });
      });
      $('div.email-actions a.send-email').click(function() {
        var followUpId;
        if (!scope.sending) {
          $(this).html('Sending...');
          scope.sending = true;
          followUpId = $(this).data('id');
          scope.sendEmail(followUpId);
        }
      });
      $(document).on('closed.fndtn.reveal', 'div#add-subscription-modal', function() {
        Bazaarboy.event.follow_up_preview.sending = false;
        $('div.email-actions a.send-email').html('Send Email');
      });
    }
  };

  Bazaarboy.event.follow_up_preview.init();

}).call(this);
