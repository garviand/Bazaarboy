(function() {
  Bazaarboy.reward["new"] = {
    attachment: void 0,
    gif: void 0,
    creating: false,
    init: function() {
      var scope;
      scope = this;
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
      $('a.create-reward').click(function() {
        var attachmentId, description, field, fields, formattedFields, name, num, useGif, value, _i, _len;
        if (!scope.creating) {
          scope.creating = true;
          $('a.create-reward').html('Creating...');
          if ($('input[name=name]').val().trim() === '') {
            swal('Name Cannot Be Blank');
            $('a.create-reward').html('Create Inventory Item');
            scope.creating = false;
            return;
          }
          name = $('input[name=name]').val();
          if ($('textarea[name=description]').val().trim() === '') {
            swal('Description Cannot Be Blank');
            $('a.create-reward').html('Create Inventory Item');
            scope.creating = false;
            return;
          }
          description = $('textarea[name=description]').val();
          if (!$.isNumeric($('input[name=value]').val()) || $('input[name=value]').val() <= 0) {
            swal('Value Must Be a Positive Number');
            $('a.create-reward').html('Create Inventory Item');
            scope.creating = false;
            return;
          }
          value = $('input[name=value]').val();
          useGif = false;
          if (scope.attachment != null) {
            attachmentId = scope.attachment.pk;
          } else if (scope.gif != null) {
            attachmentId = scope.gif;
            useGif = true;
          } else {
            swal('Must Include An Image for the Gift');
            $('a.create-reward').html('Create Inventory Item');
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
          }
          Bazaarboy.post('rewards/create/', {
            profile: profileId,
            name: name,
            description: description,
            value: value,
            attachment: attachmentId,
            gif: useGif,
            extra_fields: formattedFields
          }, function(response) {
            if (response.status === 'OK') {
              swal({
                type: "success",
                title: 'Inventory Created',
                text: 'You can now transfer this item to other organiztions for distribution to their audience, or you can add gifts to share with your own people.'
              }, function() {
                Bazaarboy.redirect('rewards/');
              });
            } else {
              $('a.create-reward').html('Create Inventory Item');
              scope.creating = false;
              swal(response.message);
            }
          });
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
    }
  };

  Bazaarboy.reward["new"].init();

}).call(this);
