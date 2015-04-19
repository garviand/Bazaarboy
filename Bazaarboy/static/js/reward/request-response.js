(function() {
  Bazaarboy.reward.request = {
    isSubmitting: false,
    attachment: void 0,
    gif: void 0,
    sending: false,
    init: function() {
      var scope;
      scope = this;
      if (typeof attachmentId !== "undefined" && attachmentId !== null) {
        scope.attachment = {
          pk: attachmentId
        };
      }
      $('div.choose-type a.choose-type-btn').click(function() {
        $('div.choose-type a.choose-type-btn').addClass('primary-btn-inverse');
        $('div.choose-type a.choose-type-btn').removeClass('primary-btn');
        $('div.choose-type a.choose-type-btn').removeClass('active');
        $(this).removeClass('primary-btn-inverse');
        $(this).addClass('primary-btn');
        $(this).addClass('active');
        if ($(this).data('type') === 'current') {
          $('div.current-reward').removeClass('hide');
          $('div.new-reward').addClass('hide');
          $('html, body').animate({
            scrollTop: $("div.current-reward").offset().top
          }, 500);
        } else {
          $('div.new-reward').removeClass('hide');
          $('div.current-reward').addClass('hide');
          $('html, body').animate({
            scrollTop: $("div.new-reward").offset().top
          }, 500);
        }
      });
      $('div.dropdown-container a.select-reward').click(function() {
        $('div.dropdown-container ul#drop').css('left', '-99999px');
        $('div.dropdown-container ul#drop').removeClass('open');
        $('input[name=reward_id]').val($(this).data('id'));
        $('div.dropdown-container a.choose-gift-btn').html($(this).html());
      });
      $('input[name=reward_expiration]').pikaday({
        format: 'MM/DD/YYYY'
      });
      $('form#current-reward-form a.send-gift-btn').click(function() {
        var button, expiration, expirationTime, ownerId, quantity, rewardId;
        button = $('form#current-reward-form a.send-gift-btn');
        button.html('Sending...');
        if (!scope.sending) {
          scope.sending = true;
          quantity = parseInt($('input[name=reward_quantity]').val());
          if (!$.isNumeric(quantity) || quantity <= 0) {
            swal('Quantity Must Be a Positive Number');
            scope.sending = false;
            button.html('Send Gifts');
            return;
          }
          expiration = $('input[name=reward_expiration]').val();
          if (!moment(expiration, 'MM/DD/YYYY').isValid()) {
            swal('Expiration Date is Not Valid');
            scope.sending = false;
            button.html('Send Gifts');
            return;
          }
          expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
          rewardId = $('input[name=reward_id]').val();
          if (rewardId === '') {
            swal('You must select a gift');
            scope.sending = false;
            button.html('Send Gifts');
            return;
          }
          ownerId = requesterId;
          Bazaarboy.post('rewards/item/add/', {
            reward: rewardId,
            owner: ownerId,
            quantity: quantity,
            expiration_time: expirationTime,
            reward_request: requestId
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
                Bazaarboy.redirect('rewards/');
              });
            }
          });
        }
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
      $('a.create-reward').click(function() {
        var field, fields, formattedFields, num, params, _i, _len;
        if (!scope.creating) {
          scope.creating = true;
          $('a.create-reward').html('Creating...');
          params = $('form#new-reward-form').serializeObject();
          if (params.name.trim() === '') {
            swal('Name Cannot Be Blank');
            $('a.create-reward').html('Create and Send');
            scope.creating = false;
            return;
          }
          if (params.description.trim() === '') {
            swal('Description Cannot Be Blank');
            $('a.create-reward').html('Create and Send');
            scope.creating = false;
            return;
          }
          if (!$.isNumeric(params.value) || params.value <= 0) {
            swal('Value Must Be a Positive Number');
            $('a.create-reward').html('Create and Send');
            scope.creating = false;
            return;
          }
          params.gif = false;
          if (scope.attachment != null) {
            params.attachment = scope.attachment.pk;
          } else if (scope.gif != null) {
            params.attachment = scope.gif;
            params.gif = true;
          } else {
            swal('Must Include An Image for the Gift');
            $('a.create-reward').html('Create and Send');
            scope.creating = false;
            return;
          }
          formattedFields = {};
          if ($('input[name=extra_fields]').val().trim() !== '') {
            fields = $('input[name=extra_fields]').val().split(",");
            num = 0;
            for (_i = 0, _len = fields.length; _i < _len; _i++) {
              field = fields[_i];
              formattedFields[num] = field.trim();
              num++;
            }
            formattedFields = JSON.stringify(formattedFields);
            params.extra_fields = formattedFields;
          }
          params.profile = profileId;
          params.request_id = requestId;
          Bazaarboy.post('rewards/create/', params, function(response) {
            if (response.status === 'OK') {
              swal({
                type: "success",
                title: 'Gift Created',
                html: '<div class="text-left"><label class="quant-info">How many would you like to send to ' + requesterName + '?<input type="text" name="send_quantity" placeholder="Quantity" /><br /><label class="exp-info">Expiration Date</label><input type="text" name="expiration_time" placeholder="MM/DD/YYYY" /></div>',
                closeOnConfirm: false
              }, function() {
                var expiration, expirationTime, quantity;
                quantity = $('input[name=send_quantity]').val();
                expiration = $('input[name=expiration_time]').val();
                if (!$.isNumeric(quantity) || quantity <= 0) {
                  $('div.quant-info').html('Must be a positive integer, try again:');
                  $('input[name=send_quantity]').val('');
                }
                if (!moment(expiration, 'MM/DD/YYYY').isValid()) {
                  $('div.quant-info').html('Must be a positive integer, try again:');
                  $('input[name=send_quantity]').val('');
                } else {
                  expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
                  Bazaarboy.post('rewards/item/add/', {
                    reward: response.reward.pk,
                    owner: requesterId,
                    quantity: quantity,
                    expiration_time: expirationTime
                  }, function(response) {
                    if (response.status === 'OK') {
                      return swal({
                        type: "success",
                        title: "Gift Sent",
                        text: requesterName + ' will recieve your gift for distribution. Thanks!'
                      }, function() {
                        return Bazaarboy.redirect('rewards/');
                      });
                    } else {
                      return swal({
                        type: "warning",
                        title: "Gift Not Sent",
                        text: 'Your gift was created, but there was an error sending it. Please try to send to ' + requesterName + ' again from your dashboard.'
                      });
                    }
                  });
                }
              });
            } else {
              $('a.create-reward').html('Create and Send');
              scope.creating = false;
              swal(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.request.init();

}).call(this);
