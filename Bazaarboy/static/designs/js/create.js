(function() {
  Bazaarboy.designs.create = {
    createProject: function(user_email, services, description, assets, register) {
      Bazaarboy.post('designs/project/create/', {
        services: services,
        description: description,
        assets: assets
      }, function(response) {
        var _this = this;
        if (loggedIn) {
          StripeCheckout.open({
            key: response.publishable_key,
            address: false,
            amount: response.price,
            currency: 'usd',
            name: 'Bazaarboy Designs',
            panelLabel: 'Checkout',
            email: user_email,
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
        } else {
          if (register) {
            window.location.href = '/register/?next=designs&code=' + response.project.code;
          } else {
            window.location.href = '/login/?next=designs&code=' + response.project.code;
          }
        }
      });
    },
    init: function() {
      var scope;
      scope = this;
      $("div.services a.service-option").click(function() {
        var total;
        $(this).toggleClass('active');
        total = 0;
        $("div.services a.service-option.active").each(function() {
          return total += parseInt($(this).data('price'));
        });
        if (total > 0) {
          $("div.payment div.cost").html('$' + total);
        } else {
          $("div.payment span.cost").html('');
        }
      });
      $("div.payment a.payment-btn").click(function() {
        var assets, description, nextPage, services, user_email;
        user_email = $(this).data('email');
        nextPage = $(this).data('next');
        if ($("div.services a.service-option.active").length === 0) {
          swal("", "You must select at least one service", "error");
        } else if ($("div.description textarea[name=description]").val().trim() === '') {
          swal("", "You must write a description of your project", "error");
        } else {
          if ($("form#new-project input[name=assets]").val().trim() === '') {
            swal({
              title: "No Assets Attached",
              text: "Are you sure you want to continue without attaching any images for the designer?",
              type: "warning",
              showCancelButton: true,
              confirmButtonText: "Yes",
              closeOnConfirm: true
            }, function() {
              var assets, description, services;
              description = $("div.description textarea[name=description]").val();
              services = '';
              assets = $("form#new-project input[name=assets]").val();
              return $("div.services a.service-option.active").each(function() {
                if (services === '') {
                  services += $(this).data('id');
                } else {
                  services += ', ' + $(this).data('id');
                }
                if (nextPage === 'register') {
                  return scope.createProject(user_email, services, description, assets, true);
                } else {
                  return scope.createProject(user_email, services, description, assets, false);
                }
              });
            });
          } else {
            description = $("div.description textarea[name=description]").val();
            services = '';
            assets = $("form#new-project input[name=assets]").val();
            $("div.services a.service-option.active").each(function() {
              if (services === '') {
                return services += $(this).data('id');
              } else {
                return services += ', ' + $(this).data('id');
              }
            });
            if (nextPage === 'register') {
              scope.createProject(user_email, services, description, assets, true);
            } else {
              scope.createProject(user_email, services, description, assets, false);
            }
          }
        }
      });
      $("div.dropzone").dropzone({
        url: "/designs/asset/upload/",
        paramName: "image_file",
        init: function() {
          this.on('success', function(file) {
            var image, image_id, oldVal;
            image = $.parseJSON(file.xhr.response);
            image_id = image.image.pk;
            if ($("form#new-project input[name=assets]").val().trim() === '') {
              $("form#new-project input[name=assets]").val(image_id);
            } else {
              oldVal = $("form#new-project input[name=assets]").val();
              $("form#new-project input[name=assets]").val(oldVal + ', ' + image_id);
            }
          });
          return;
          this.on('error', function(file) {
            swal("Error", "The file could not be uploaded", "error");
          });
        }
      });
    }
  };

  Bazaarboy.designs.create.init();

}).call(this);
