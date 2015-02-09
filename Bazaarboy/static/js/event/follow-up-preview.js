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
      $('div.email-actions a.send-email').click(function() {
        var followUpId;
        if (!scope.sending) {
          $(this).html('Sending...');
          scope.sending = true;
          followUpId = $(this).data('id');
          scope.sendEmail(followUpId);
        }
      });
    }
  };

  Bazaarboy.event.follow_up_preview.init();

}).call(this);
