(function() {
  Bazaarboy.event.follow_up = {
    saving: false,
    image: {},
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
          var csrfmiddlewaretoken, _ref;
          csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
          console.log(data);
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
      scope.aviary = new Aviary.Feather({
        apiKey: 'ce3b87fb1edaa22c',
        apiVersion: 3,
        enableCORS: true,
        onSave: function(imageId, imageUrl) {
          $("img#header-image").attr('src', imageUrl);
          scope.aviary.close();
          console.log(imageUrl);
          $('a.upload-logo-btn').html('Uploading...');
          Bazaarboy.post('file/aviary/profile/', {
            url: imageUrl
          }, function(response) {
            console.log(response);
            $("img#header-image").attr('src', response.image);
            scope.image.pk = response.image_id;
            $('div#event-follow-up a.upload-image-btn').html('Upload Image');
            $('div#event-follow-up div.image-preview').removeClass('hide');
            $('div#event-follow-up a.upload-image-btn').css('display', 'none');
            $('div#event-follow-up a.delete-image-btn').css('display', 'block');
          });
        }
      });
      $('div#event-follow-up a.upload-image-btn').click(function() {
        $('div#event-follow-up input[name=image_file]').click();
      });
      $('div#event-follow-up a.delete-image-btn').click(function() {
        scope.image = {};
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
            $('img#header-image').attr('src', mediaUrl + response.image.source);
            scope.aviary.launch({
              image: 'header-image',
              url: mediaUrl + response.image.source
            });
          } else {
            swal(response.message);
            $('div#event-follow-up a.upload-image-btn').html('Upload Image');
          }
        }
      });
      $('a.button-type-btn').click(function() {
        $('a.button-type-btn').removeClass('primary-btn');
        $('a.button-type-btn').addClass('primary-btn-inverse');
        $('a.button-type-btn').removeClass('active');
        $(this).addClass('active');
        $(this).addClass('primary-btn');
        $(this).removeClass('primary-btn-inverse');
        $('div.custom-link').addClass('hide');
        if ($(this).data('type') === 'link') {
          $('div.custom-link').removeClass('hide');
        }
      });
      $('input[name=colorpicker]').spectrum({
        preferredFormat: "hex",
        showInput: true,
        showButtons: true
      });
      $('a.save-follow-up').click(function() {
        var activeLists, button_text, button_type, color, custom_url, deleteImg, deletePdf, heading, imageId, list, lists, message, pdfId, targetId, targetUrl, _i, _len;
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
          button_text = $('div.email input[name=button_text]').val();
          if (button_text.trim() === '') {
            swal("Wait!", "Email Button Text Cannot Be Empty", "warning");
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
          if (scope.image.pk != null) {
            imageId = scope.image.pk;
            deleteImg = false;
          }
          deletePdf = true;
          if (scope.pdf != null) {
            pdfId = scope.pdf.pk;
            deletePdf = false;
          }
          color = $('input[name=colorpicker]').spectrum("get").toHexString();
          button_type = $('a.button-type-btn.active').data('type');
          custom_url = $('input[name=button_link]').val();
          if (button_type === 'link' && !(/^([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(custom_url))) {
            scope.saving = false;
            $('a.save-follow-up').html('Save &amp; Preview');
            swal("Custom Link is not valid. Remember, you must include http:// or https://.");
            return;
          }
          Bazaarboy.post(targetUrl, {
            id: targetId,
            heading: heading,
            message: message,
            button_text: button_text,
            button_type: button_type,
            custom_link: custom_url,
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
              Bazaarboy.redirect('event/followup/' + followUpId + '/preview');
              return;
            } else {
              swal(response.message);
            }
            scope.saving = false;
            $('a.save-follow-up').html('Save &amp; Preview');
          });
        }
      });
    }
  };

  Bazaarboy.event.follow_up.init();

}).call(this);
