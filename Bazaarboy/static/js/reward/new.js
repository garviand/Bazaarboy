(function() {
  Bazaarboy.reward["new"] = {
    attachment: void 0,
    init: function() {
      var scope;
      scope = this;
      $('a.create-reward').click(function() {
        var attachmentId, description, name, value;
        if ($('input[name=name]').val().trim() === '') {
          swal('Name Cannot Be Blank');
          return;
        }
        name = $('input[name=name]').val();
        if ($('textarea[name=description]').val().trim() === '') {
          swal('Description Cannot Be Blank');
          return;
        }
        description = $('textarea[name=description]').val();
        if (!$.isNumeric($('input[name=value]').val()) || $('input[name=value]').val() <= 0) {
          swal('Value Must Be a Positive Number');
          return;
        }
        value = $('input[name=value]').val();
        if (scope.attachment != null) {
          attachmentId = scope.attachment.pk;
        } else {
          swal('Must Include An Image for the Reward');
          return;
        }
        Bazaarboy.post('rewards/create/', {
          profile: profileId,
          name: name,
          description: description,
          value: value,
          attachment: attachmentId
        }, function(response) {
          if (response.status === 'OK') {
            swal({
              type: "success",
              title: 'Reward Created',
              text: 'You can now send it to your own attendees, or allow other organizations to share your reward.'
            }, function() {
              Bazaarboy.redirect('rewards/');
            });
          } else {
            swal(response.message);
          }
        });
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
            $('a.attachment-name').html(pdfName);
            $('a.attachment-name').attr('href', response.url);
            $('a.attachment-name').removeClass('hide');
            $('a.add-attachment').html('Change Attachment');
          } else {
            swal(response.message);
            $('a.add-attachment').html('Add Attachment');
          }
        }
      });
    }
  };

  Bazaarboy.reward["new"].init();

}).call(this);
