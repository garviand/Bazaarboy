(function() {
  Bazaarboy.event.invite_preview = {
    sending: false,
    sendEmail: function(inviteId) {
      Bazaarboy.post('event/invite/send/', {
        id: inviteId
      }, function(response) {
        var _this = this;
        if (response.status === 'OK') {
          Bazaarboy.redirect('event/invite/' + response.invite.pk + '/details/');
        } else if (response.status === 'PAYMENT') {
          StripeCheckout.open({
            key: response.publishable_key,
            address: false,
            amount: response.cost,
            currency: 'usd',
            name: 'Send Invitations',
            description: response.sent + ' Invitations - ' + response.invite.event.name,
            panelLabel: 'Send Now',
            image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png',
            closed: function() {
              Bazaarboy.event.invite_preview.sending = false;
              $('div.email-actions a.send-email').html('Send Email');
            },
            token: function(token) {
              Bazaarboy.post('payment/charge/invite/', {
                invite: response.invite.pk,
                stripe_token: token.id,
                amount: response.cost
              }, function(response) {
                if (response.status === 'OK') {
                  Bazaarboy.event.invite_preview.sending = true;
                  $('div.email-actions a.send-email').html('Sending...');
                  Bazaarboy.event.invite_preview.sendEmail(response.invite.pk);
                } else {
                  swal(response.message);
                  Bazaarboy.event.invite_preview.sending = false;
                  $('div.email-actions a.send-email').html('Send Email');
                }
              });
            }
          });
        } else {
          swal(response.message);
          Bazaarboy.event.invite_preview.sending = false;
          $('div.email-actions a.send-email').html('Send Email');
        }
      });
    },
    init: function() {
      var scope;
      scope = this;
      $('div.email-actions a.send-email').click(function() {
        var _this = this;
        if (!scope.sending) {
          swal({
            title: "Confirm Details",
            html: "Title: " + eventName + "<br /><br />Date: " + eventDate + "<br /><br />Recipients: " + sentNumber,
            type: "success",
            showCancelButton: true,
            confirmButtonText: "Send Email",
            closeOnConfirm: true
          }, function(isConfirm) {
            var inviteId;
            if (isConfirm) {
              $(_this).html('Sending...');
              scope.sending = true;
              inviteId = $(_this).data('id');
              return scope.sendEmail(inviteId);
            }
          });
        }
      });
    }
  };

  Bazaarboy.event.invite_preview.init();

}).call(this);
