(function() {
  Bazaarboy.reward.request = {
    isSubmitting: false,
    attachment: void 0,
    gif: void 0,
    init: function() {
      var scope;
      scope = this;
      $('div.choose-type a.choose-type-btn').click(function() {
        $('div.choose-type a.choose-type-btn').addClass('primary-btn-inverse');
        $('div.choose-type a.choose-type-btn').removeClass('primary-btn');
        $('div.choose-type a.choose-type-btn').removeClass('active');
        $(this).removeClass('primary-btn-inverse');
        $(this).addClass('primary-btn');
        $(this).addClass('active');
        if ($(this).data('type') === 'message') {
          $('div.reward-template').addClass('hide');
        } else {
          $('div.reward-template').removeClass('hide');
        }
        $('html, body').animate({
          scrollTop: $("div.reward-message").offset().top
        }, 500);
      });
      $('a.remove-image-btn').click(function() {
        scope.attachment = void 0;
        scope.gif = void 0;
        $('div.listing-image-container').addClass('hide');
        $('div.listing-image-input-container').removeClass('hide');
      });
      $('input[name=gif_search]').keypress(function(e) {
        if (e.which === 13) {
          $('a.gif-search-start').click();
        }
      });
      $('a.gif-search-start').click(function() {
        swal({
          title: 'Search For Gif',
          html: '<input type="text" name="gif_search" placeholder="GIF Search (pizza, coffee, etc)" />',
          showCancelButton: true,
          closeOnConfirm: true,
          confirmButtonText: 'Search'
        }, function() {
          var searchTerm;
          $('a.gif-search-start').html('Searching...');
          searchTerm = $('input[name=gif_search]').val();
          if (searchTerm.trim() === '') {
            swal('You Must Type a Search Term');
            $('a.gif-search-start').html('Search with GIPHY');
            return;
          }
          Bazaarboy.get('rewards/search/gif/', {
            q: searchTerm
          }, function(response) {
            var col, count, gif, gifLength, newGif, _i, _len;
            response = jQuery.parseJSON(response['gifs']);
            $('div#gif-modal div.gifs .gif-column').empty();
            count = 0;
            gifLength = Math.floor(response.length / 3);
            for (_i = 0, _len = response.length; _i < _len; _i++) {
              gif = response[_i];
              count += 1;
              col = Math.ceil(count / gifLength);
              newGif = $('div#gif-modal .gif-template').clone();
              newGif.find('img').attr('src', gif.fixed_width.url);
              newGif.attr('data-url', gif.original.url);
              newGif.removeClass('gif-template');
              newGif.removeClass('hide');
              $('div#gif-modal div.gifs .gifs-' + col).append(newGif);
            }
            $('div#gif-modal').foundation('reveal', 'open');
            $('a.gif-search-start').html('Search with GIPHY');
          });
        });
      });
      $('div#gif-modal div.gifs').on('click', '.gif', function() {
        $('input[name=gif_search]').val('');
        scope.gif = $(this).attr('data-url');
        $('div#gif-modal').foundation('reveal', 'close');
        $('div.listing-image-container img').attr('src', $(this).attr('data-url'));
        $('div.listing-image-input-container').addClass('hide');
        $('div.listing-image-container').removeClass('hide');
        scope.attachment = void 0;
      });
      $('input[name=search_name]').autocomplete({
        html: true,
        source: function(request, response) {
          Bazaarboy.get('profile/search/', {
            keyword: request.term
          }, function(results) {
            var profile, profiles, thisLabel, _i, _len, _ref;
            profiles = [];
            _ref = results.profiles;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              profile = _ref[_i];
              thisLabel = '<div class="autocomplete_result row" data-id="' + profile.pk + '">';
              if (profile.image_url != null) {
                thisLabel += '<div class="small-1 columns autocomplete_image" style="background-image:url(' + profile.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />';
              }
              thisLabel += '<div class="small-11 columns autocomplete_name">' + profile.name + '</div>';
              thisLabel += '</div>';
              profiles.push({
                label: thisLabel,
                value: profile.name
              });
            }
            return response(profiles);
          });
        },
        select: function(event, ui) {
          var requestProfile;
          requestProfile = $(event.currentTarget).find('.autocomplete_result').data('id');
          $('input[name=profile]').val(requestProfile);
        }
      });
      $('a.add-attachment').click(function() {
        $('input[name=attachment_file]').click();
      });
      $('input[name=attachment_file]').fileupload({
        url: rootUrl + 'event/followup/attachment/',
        type: 'POST',
        add: function(event, data) {
          var csrfmiddlewaretoken, _ref;
          $('a.add-attachment').html('loading...');
          csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
          data.formData = {
            name: data.files[0].name,
            csrfmiddlewaretoken: csrfmiddlewaretoken
          };
          if ((_ref = data.files[0].type) !== 'image/jpeg' && _ref !== 'image/jpg' && _ref !== 'image/png' && _ref !== 'image/gif') {
            swal('Must Be A PNG, JPG or GIF');
            $('a.add-attachment').html('Upload Image');
          } else {
            data.submit();
          }
        },
        done: function(event, data) {
          var pdfName, response;
          pdfName = data.files[0].name;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            scope.attachment = response.pdf;
            scope.gif = void 0;
            $('div.listing-image-container img').attr('src', response.url);
            $('div.listing-image-input-container').addClass('hide');
            $('div.listing-image-container').removeClass('hide');
            $('a.add-attachment').html('Upload Image');
          } else {
            swal(response.message);
            $('a.add-attachment').html('Upload Image');
          }
        }
      });
      $('a.create-request').click(function() {
        var button, params;
        if (!scope.isSubmitting) {
          button = $(this);
          button.html('Submitting...');
          scope.isSubmitting = true;
          params = $('form#request-reward-form').serializeObject();
          if ($('div.choose-type a.choose-type-btn.active').length === 0) {
            swal('You must select a request type (Message or Template).');
            button.html('Send Request');
            scope.isSubmitting = false;
            return;
          }
          if (params.message.trim() === '') {
            swal('The message cannot be empty');
            button.html('Send Request');
            scope.isSubmitting = false;
            return;
          }
          if (params.event_url.trim() === '') {
            params.event_url = void 0;
          }
          if ($('div.choose-type a.choose-type-btn.active').data('type') === 'message') {
            params.template = false;
          } else if ($('div.choose-type a.choose-type-btn.active').data('type') === 'template') {
            params.template = true;
            params.gif = false;
            if (scope.attachment != null) {
              params.attachment = scope.attachment.pk;
            } else if (scope.gif != null) {
              params.attachment = scope.gif;
              params.gif = true;
            } else {
              params.attachment = void 0;
            }
            if ($('input[name=value]').val().trim() === '') {
              params.value = void 0;
            } else if (!$.isNumeric($('input[name=value]').val()) || $('input[name=value]').val() <= 0) {
              swal('Item Value Must Be a Positive Number');
              button.html('Send Request');
              scope.isSubmitting = false;
            }
          }
          params.sender = profileId;
          console.log(params);
          Bazaarboy.post('rewards/request/create/', params, function(response) {
            if (response.status === 'OK') {
              return swal({
                type: 'success',
                title: 'Request Sent',
                text: 'Your gift request has been sent. You will be notified with the reply!'
              }, function() {
                Bazaarboy.redirect('rewards/');
              });
            } else {
              return swal({
                type: 'warning',
                title: 'Hold On!',
                text: response.message
              }, function() {
                scope.isSubmitting = false;
                button.html('Send Request');
              });
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.request.init();

}).call(this);
