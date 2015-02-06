(function() {
  Bazaarboy.event.follow_up = {
    saving: false,
    image: void 0,
    pdf: void 0,
    init: function() {
      var scope,
        _this = this;
      scope = this;
      if (typeof imgId !== "undefined" && imgId !== null) {
        scope.image = {
          pk: imgId
        };
      }
      if (typeof pdfId !== "undefined" && pdfId !== null) {
        scope.pdf = {
          pk: pdfId
        };
      }
      $('div.lists div.list').click(function() {
        $(this).toggleClass('active');
      });
      $('div#event-follow-up a.upload-attachment-btn').click(function() {
        $('div#event-follow-up input[name=attachment_file]').click();
      });
      $('div#event-follow-up a.delete-attachment-btn').click(function() {
        scope.pdf = void 0;
        $('div.pdf-preview').addClass('hide');
        $('div#event-follow-up a.upload-attachment-btn').css('display', 'block');
        $('div#event-follow-up a.delete-attachment-btn').css('display', 'none');
      });
      $('div#event-follow-up input[name=attachment_file]').fileupload({
        url: rootUrl + 'event/followup/attachment/',
        type: 'POST',
        add: function(event, data) {
          var csrfmiddlewaretoken;
          csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
          data.formData = {
            name: data.files[0].name,
            csrfmiddlewaretoken: csrfmiddlewaretoken
          };
          if (data.files[0].type !== 'application/pdf') {
            swal('Must Be A PDF File');
          } else {
            data.submit();
          }
        },
        done: function(event, data) {
          var pdfName, response;
          pdfName = data.files[0].name;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            scope.pdf = response.pdf;
            $('div.pdf-preview span.filename').html(pdfName);
            $('div.pdf-preview').removeClass('hide');
            $('div#event-follow-up a.upload-attachment-btn').css('display', 'none');
            $('div#event-follow-up a.delete-attachment-btn').css('display', 'block');
          } else {
            swal(response.message);
          }
        }
      });
      $('div#event-follow-up a.upload-image-btn').click(function() {
        $('div#event-follow-up input[name=image_file]').click();
      });
      $('div#event-follow-up a.delete-image-btn').click(function() {
        scope.image = void 0;
        $('div#event-follow-up div.image-preview img').attr('src', '');
        $('div#event-follow-up div.image-preview').addClass('hide');
        $('div#event-follow-up a.upload-image-btn').css('display', 'block');
        $('div#event-follow-up a.delete-image-btn').css('display', 'none');
      });
      $('div#event-follow-up input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
          $('div#event-follow-up a.upload-image-btn').html('Uploading...');
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            if (scope.image != null) {
              Bazaarboy.post('file/image/delete/', {
                id: scope.image.pk
              });
            }
            scope.image = response.image;
            $('div#event-follow-up a.upload-image-btn').html('Upload Image');
            $('div#event-follow-up div.image-preview').removeClass('hide');
            $('div#event-follow-up a.upload-image-btn').css('display', 'none');
            $('div#event-follow-up a.delete-image-btn').css('display', 'block');
            $('div#event-follow-up div.image-preview img').attr('src', mediaUrl + response.image.source);
          } else {
            alert(response.message);
            $('div#event-follow-up a.upload-image-btn').html('Upload Image');
          }
        }
      });
      $('input[name=colorpicker]').spectrum({
        preferredFormat: "hex",
        showInput: true,
        showButtons: true
      });
      $('a.save-follow-up').click(function() {
        var activeLists, color, deleteImg, deletePdf, heading, imageId, list, lists, message, pdfId, targetId, targetUrl, _i, _len;
        if (!scope.saving) {
          $('a.save-follow-up').html('Saving...');
          scope.saving = true;
          if (!followUpEdit) {
            targetId = $('div.email input[name=event]').val();
            targetUrl = 'event/followup/new/';
          } else {
            targetId = $('div.email input[name=follow_up]').val();
            targetUrl = 'event/followup/save/';
          }
          heading = $('div.email textarea[name=heading]').val();
          if (heading.trim() === '') {
            swal("Wait!", "Email Header Cannot Be Empty", "warning");
            scope.saving = false;
            $('a.save-follow-up').html('Save &amp; Preview');
            return;
          }
          message = $('div.email textarea[name=message]').val();
          if (message.trim() === '') {
            swal("Wait!", "Email Message Cannot Be Empty", "warning");
            scope.saving = false;
            $('a.save-follow-up').html('Save &amp; Preview');
            return;
          }
          activeLists = $('div.lists div.list.active');
          if (activeLists.length === 0) {
            swal("Wait!", "You Must Select At Least 1 Ticket", "warning");
            scope.saving = false;
            $('a.save-follow-up').html('Save &amp; Preview');
            return;
          }
          lists = '';
          for (_i = 0, _len = activeLists.length; _i < _len; _i++) {
            list = activeLists[_i];
            if (lists !== '') {
              lists += ', ';
            }
            lists += $(list).data('id');
          }
          imageId = '';
          deleteImg = true;
          if (scope.image != null) {
            imageId = scope.image.pk;
            deleteImg = false;
          }
          deletePdf = true;
          if (scope.pdf != null) {
            pdfId = scope.pdf.pk;
            deletePdf = false;
          }
          color = $('input[name=colorpicker]').spectrum("get").toHexString();
          scope.saving = false;
          Bazaarboy.post(targetUrl, {
            id: targetId,
            heading: heading,
            message: message,
            tickets: lists,
            color: color,
            image: imageId,
            deleteImg: deleteImg,
            pdf: pdfId,
            deletePdf: deletePdf
          }, function(response) {
            var followUpId;
            if (response.status === 'OK') {
              followUpId = response.follow_up.pk;
              return;
            } else {
              swal(response.message);
            }
            scope.saving = false;
            $('a.save-invite').html('Save &amp; Preview');
          });
        }
      });
    }
  };

  Bazaarboy.event.follow_up.init();

}).call(this);
