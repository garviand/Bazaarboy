(function() {
  Bazaarboy.profile.channel = {
    image: imageId,
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('a.create-channel-btn').click(function() {
        var params;
        params = {};
        params.profile = profileId;
        if ($('input[name=tagline]').val().trim() === '') {
          swal('You Must Add a Tagline');
          return;
        }
        params.tagline = $('input[name=tagline]').val();
        if ($('input[name=hashtag]').val().trim() !== '') {
          params.hashtag = $('input[name=hashtag]').val();
        }
        if (scope.image == null) {
          swal('You Must Upload A Cover Image');
          return;
        }
        params.cover = scope.image;
        Bazaarboy.post('profile/channel/create/', params, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Success',
              text: 'Channel Created!'
            }, function() {
              return location.reload();
            });
          } else {
            swal(response.message);
          }
        });
      });
      $('a.save-channel-btn').click(function() {
        var params;
        params = {};
        params.profile = profileId;
        if ($('input[name=tagline]').val().trim() !== '') {
          params.tagline = $('input[name=tagline]').val();
        }
        if ($('input[name=hashtag]').val().trim() !== '') {
          params.hashtag = $('input[name=hashtag]').val();
        }
        if (scope.image != null) {
          params.cover = scope.image;
        }
        Bazaarboy.post('profile/channel/edit/', params, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Success',
              text: 'Channel Saved!'
            }, function() {
              return location.reload();
            });
          } else {
            swal(response.message);
          }
        });
      });
      $('div.input-container').click(function() {
        $(this).find('input, textarea').focus();
      });
      $('div.input-container input,div.input-container textarea').focus(function() {
        $(this).closest('div.input-container').addClass('active');
      });
      $('div.input-container input,div.input-container textarea').blur(function() {
        $(this).closest('div.input-container').removeClass('active');
      });
      scope.aviary = new Aviary.Feather({
        apiKey: 'ce3b87fb1edaa22c',
        apiVersion: 3,
        enableCORS: true,
        onSave: function(imageId, imageUrl) {
          $("img#cover-image").attr('src', imageUrl);
          scope.aviary.close();
          Bazaarboy.post('file/aviary/profile/', {
            url: imageUrl
          }, function(response) {
            $("img#cover-image").attr('src', response.image);
            $('a.upload-cover-btn').css('display', 'none');
            $('a.delete-cover-btn').css('display', 'block');
            $('a.upload-cover-btn').html('Upload Image');
            scope.image = response.image_id;
          });
        }
      });
      $('input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
          $('a.upload-cover-btn').html('Uploading...');
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            $('img#cover-image').attr('src', mediaUrl + response.image.source);
            scope.aviary.launch({
              image: 'cover-image',
              url: mediaUrl + response.image.source,
              maxSize: 1160,
              cropPresetsStrict: true,
              cropPresetDefault: ['Cover Photo Size', '1000x400'],
              initTool: 'crop'
            });
          } else {
            swal(response.message);
            $('a.upload-cover-btn').html('Upload Image');
          }
        }
      });
      $('a.upload-cover-btn').click(function() {
        $('input[name=image_file]').click();
      });
      $('a.delete-cover-btn').click(function() {
        scope.image = void 0;
        $('img#cover-image').attr('src', '');
        $('a.upload-cover-btn').css('display', 'block');
        $('a.delete-cover-btn').css('display', 'none');
      });
    }
  };

  Bazaarboy.profile.channel.init();

}).call(this);
