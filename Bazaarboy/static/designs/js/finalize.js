(function() {
  Bazaarboy.designs.finalize = {
    init: function() {
      var scope;
      scope = this;
      $("div.payment a.payment-btn").click(function() {
        var projectCode, projectId, userEmail;
        projectId = $(this).data('id');
        projectCode = $(this).data('code');
        userEmail = $(this).data('email');
        return Bazaarboy.post('designs/project/finalize/', {
          project: projectId,
          code: projectCode
        }, function(response) {
          var _this = this;
          if (response.status === 'OK') {
            StripeCheckout.open({
              key: response.publishable_key,
              address: false,
              amount: response.price,
              currency: 'usd',
              name: 'Bazaarboy Designs',
              panelLabel: 'Checkout',
              email: userEmail,
              image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png',
              token: function(token) {
                Bazaarboy.post('designs/project/charge/', {
                  checkout: response.project.checkout,
                  stripe_token: token.id
                }, function(response) {
                  console.log(response);
                  if (response.status === 'OK') {
                    swal({
                      title: "Congrats!",
                      text: "Your Design Project has Started. Check your dashboard for updates from your designer. You will also recieve email updates when new submissions are sent from the artist.",
                      type: "success"
                    }, function() {
                      window.location.href = '/designs';
                    });
                  } else {
                    alert(response.message);
                  }
                });
              }
            });
          }
        });
      });
    }
  };

  Bazaarboy.designs.finalize.init();

}).call(this);
