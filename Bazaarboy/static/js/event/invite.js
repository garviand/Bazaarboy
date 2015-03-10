(function() {
  Bazaarboy.event.invite = {
    saving: false,
    image: {},
    saveInvite: function(toPreview) {
      var activeLists, color, deleteImg, details, force, imageId, list, list_name, lists, message, targetId, targetUrl, _i, _len,
        _this = this;
      if (!this.saving) {
        $('a.save-invite').html('Saving...');
        this.saving = true;
        if (!toPreview) {
          list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val();
          if (list_name.trim() === '') {
            swal("Wait!", "List Name Cannot Be Empty", "warning");
            this.saving = false;
            $('div#new-list-modal div.new-list-inputs a.create-list').html('+ Add New List');
            $('a.save-invite').html('Save &amp; Preview');
          }
        }
        if (!inviteEdit) {
          targetId = $('div.email input[name=event]').val();
          targetUrl = 'event/invite/new/';
        } else {
          targetId = $('div.email input[name=invite]').val();
          targetUrl = 'event/invite/save/';
        }
        message = $('div.email textarea[name=message]').val();
        if (message.trim() === '') {
          if (toPreview) {
            swal("Wait!", "Email Message Cannot Be Empty", "warning");
            this.saving = false;
            $('a.save-invite').html('Save &amp; Preview');
            $('div#new-list-modal div.new-list-inputs a.create-list').html('+ Add New List');
            return;
          } else {
            message = 'Draft';
          }
        }
        details = $('div.email textarea[name=details]').val();
        activeLists = $('div.lists div.list.active');
        if (activeLists.length === 0 && toPreview) {
          swal("Wait!", "You Must Select At Least 1 List", "warning");
          this.saving = false;
          $('a.save-invite').html('Save &amp; Preview');
          $('div#new-list-modal div.new-list-inputs a.create-list').html('+ Add New List');
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
        if (lists === '') {
          lists = ' ';
        }
        imageId = '';
        deleteImg = true;
        if (this.image.pk != null) {
          imageId = this.image.pk;
          deleteImg = false;
        }
        force = true;
        if (toPreview) {
          force = false;
        }
        color = $('input[name=colorpicker]').spectrum("get").toHexString();
        Bazaarboy.post(targetUrl, {
          id: targetId,
          message: message,
          details: details,
          lists: lists,
          image: imageId,
          color: color,
          deleteImg: deleteImg,
          force: force
        }, function(response) {
          var inviteId;
          if (toPreview) {
            if (response.status === 'OK') {
              inviteId = response.invite.pk;
              Bazaarboy.redirect('event/invite/' + inviteId + '/preview');
              return;
            }
            _this.saving = false;
            $('a.save-invite').html('Save &amp; Preview');
            $('div#new-list-modal div.new-list-inputs a.create-list').html('+ Add New List');
          } else {
            Bazaarboy.post('lists/create/', {
              profile: profileId,
              name: list_name,
              is_hidden: 1
            }, function(response) {
              if (response.status === 'OK') {
                Bazaarboy.redirect('lists/' + response.list.pk + '/?eid=' + String(eventId));
              } else {
                swal(response.message);
                $('div#new-list-modal div.new-list-inputs a.create-list').html('+ Add New List');
              }
            });
          }
        });
      }
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      if (typeof imgId !== "undefined" && imgId !== null) {
        scope.image = {
          pk: imgId
        };
      }
      $(".new-list-btn").click(function() {
        $("div#new-list-modal").foundation('reveal', 'open');
      });
      $("a.close-list-modal").click(function() {
        $("div#new-list-modal").foundation('reveal', 'close');
      });
      $("div#new-list-modal div.new-list-inputs a.create-list").click(function() {
        $(this).html('Creating...');
        scope.saveInvite(false);
      });
      $('div.lists div.list').click(function() {
        $(this).toggleClass('active');
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
            $('div#event-invite a.upload-image-btn').html('Upload Image');
            $('div#event-invite div.image-preview').removeClass('hide');
            $('div#event-invite a.upload-image-btn').css('display', 'none');
            $('div#event-invite a.delete-image-btn').css('display', 'block');
          });
        }
      });
      $('div#event-invite a.upload-image-btn').click(function() {
        $('div#event-invite input[name=image_file]').click();
      });
      $('div#event-invite a.delete-image-btn').click(function() {
        scope.image = {};
        $('div#event-invite div.image-preview img').attr('src', '');
        $('div#event-invite div.image-preview').addClass('hide');
        $('div#event-invite a.upload-image-btn').css('display', 'block');
        $('div#event-invite a.delete-image-btn').css('display', 'none');
      });
      $('div#event-invite input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
          $('div#event-invite a.upload-image-btn').html('Uploading...');
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
            $('div#event-invite a.upload-image-btn').html('Upload Image');
          }
        }
      });
      $('input[name=colorpicker]').spectrum({
        preferredFormat: "hex",
        showInput: true,
        showButtons: true
      });
      $('a.save-invite').click(function() {
        return scope.saveInvite(true);
      });
    }
  };

  Bazaarboy.event.invite.init();

}).call(this);
