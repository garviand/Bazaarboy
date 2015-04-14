(function() {
  this.Bazaarboy.login = {
    aviary: void 0,
    timer: void 0,
    rotateLogo: function(degree) {
      var _this = this;
      $('div.logo-small').css({
        WebkitTransform: 'rotate(' + degree + 'deg)'
      });
      $('div.logo-small').css({
        '-moz-transform': 'rotate(' + degree + 'deg)'
      });
      this.timer = setTimeout((function() {
        _this.rotateLogo(++degree);
      }), 5);
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('form#login-form input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form#login-form').submit();
        }
      });
      $('form#login-form').submit(function(event) {
        var params;
        event.preventDefault();
        scope.rotateLogo(0);
        params = $('form#login-form').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0) {
          Bazaarboy.post('user/auth/', params, function(response) {
            if (response.status === 'OK') {
              if (redirect) {
                if (redirect === 'designs') {
                  if (code) {
                    window.location.href = "/designs/finalize?code=" + code;
                  } else {
                    window.location.href = "/designs?auth=true";
                  }
                }
              } else {
                Bazaarboy.redirect('index');
              }
            } else if (response.status === 'REWARD') {
              swal({
                type: 'success',
                title: 'Gift Claimed!',
                text: 'You can now send this gift out to your audience.'
              }, function() {
                return Bazaarboy.redirect('rewards/');
              });
            } else if (response.status === 'REWARD_REQUEST') {
              Bazaarboy.redirect('rewards/');
            } else {
              alert(response.message);
              window.clearTimeout(scope.timer);
              $('div.logo-small').css({
                WebkitTransform: 'none'
              });
              $('div.logo-small').css({
                '-moz-transform': 'none'
              });
            }
          });
        }
      });
      scope.aviary = new Aviary.Feather({
        apiKey: 'ce3b87fb1edaa22c',
        apiVersion: 3,
        enableCORS: true,
        onSave: function(imageId, imageUrl) {
          $("img#organization-logo").attr('src', imageUrl);
          scope.aviary.close();
          $('a.upload-logo-btn').html('Uploading...');
          Bazaarboy.post('file/aviary/profile/', {
            url: imageUrl
          }, function(response) {
            $("img#organization-logo").attr('src', response.image);
            $("input[name=logo_id]").val(response.image_id);
            $('a.upload-logo-btn').html('Change');
          });
        }
      });
      $('a.upload-logo-btn').click(function() {
        $('input[name=image_file]').click();
      });
      $('form.upload-logo input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            $('img#organization-logo').attr('src', mediaUrl + response.image.source);
            scope.aviary.launch({
              image: 'organization-logo',
              url: mediaUrl + response.image.source,
              cropPresets: ['400x400'],
              cropPresetsStrict: true,
              forceCropPreset: ['Logo Size', '1:1']
            });
          } else {
            swal(response.message);
          }
        }
      });
      $('form#register-form input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form#register-form').submit();
        }
      });
      $('form#register-form').submit(function(event) {
        var params;
        event.preventDefault();
        scope.rotateLogo(0);
        params = $('form#register-form').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0 && params.password === params.confirm && params.first_name.length !== 0 && params.last_name.length !== 0) {
          Bazaarboy.post('user/create/', params, function(response) {
            console.log(response);
            if (response.status === 'OK') {
              if (redirect) {
                if (redirect === 'designs') {
                  if (code) {
                    window.location.href = "/designs/finalize?code=" + code;
                  } else {
                    window.location.href = "/designs?auth=true";
                  }
                }
              } else {
                Bazaarboy.redirect('index');
              }
            } else if (response.status === 'REWARD') {
              swal({
                type: 'success',
                title: 'Gift Claimed!',
                text: 'You can now send this gift out to your audience.'
              }, function() {
                return Bazaarboy.redirect('rewards/');
              });
            } else if (response.status === 'REWARD_REQUEST') {
              Bazaarboy.redirect('rewards/');
            } else {
              console.log(response);
              console.log('not rewarded');
              alert(response.message);
              window.clearTimeout(scope.timer);
              $('div.logo-small').css({
                WebkitTransform: 'none'
              });
              $('div.logo-small').css({
                '-moz-transform': 'none'
              });
            }
          });
        } else if (params.password !== params.confirm) {
          alert("Passwords do not match");
          window.clearTimeout(scope.timer);
          $('div.logo-small').css({
            WebkitTransform: 'none'
          });
          $('div.logo-small').css({
            '-moz-transform': 'none'
          });
        } else {
          alert("All fields must be filled out");
          window.clearTimeout(scope.timer);
          $('div.logo-small').css({
            WebkitTransform: 'none'
          });
          $('div.logo-small').css({
            '-moz-transform': 'none'
          });
        }
      });
    }
  };

  Bazaarboy.login.init();

}).call(this);
