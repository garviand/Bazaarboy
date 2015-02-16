(function() {
  Bazaarboy.reward["new"] = {
    attachment: void 0,
    init: function() {
      var scope;
      scope = this;
      $('a.create-reward').click(function() {
        var attachmentId, description, details, name;
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
        if ($('textarea[name=details]').val().trim() === '') {
          swal('Details Cannot Be Blank');
          return;
        }
        details = $('textarea[name=details]').val();
        if (scope.attachment != null) {
          attachmentId = scope.attachment.pk;
        } else {
          attachmentId = '';
        }
        Bazaarboy.post('reward/create/', {
          profile: profileId,
          name: name,
          description: description,
          details: details,
          attachment: attachmentId
        }, function(response) {
          if (response.status === 'OK') {
            console.log(response);
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
          if ((_ref = data.files[0].type) !== 'application/pdf' && _ref !== 'image/jpeg' && _ref !== 'image/jpg' && _ref !== 'image/png' && _ref !== 'image/gif') {
            swal('Must Be A PDF, PNG, JPG or GIF');
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
