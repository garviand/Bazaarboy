(function() {
  Bazaarboy.profile.channel = {
    image: void 0,
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('input[name=end_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
      $('a.create-sign-up-btn').click(function() {
        var params;
        params = {};
        if ($('input[name=name]').val().trim() === '') {
          swal('You Must Add a Name');
          return;
        }
        params.name = $('input[name=name]').val();
        if ($('textarea[name=description]').val().trim() === '') {
          swal('You Must Add a Description');
          return;
        }
        params.description = $('textarea[name=description]').val();
        if (!moment($('input[name=end_date]').val(), 'MM/DD/YYYY').isValid()) {
          swal('The End Date Format is Invalid (MM/DD/YYYY)');
          return;
        }
        params.end_time = moment($('input[name=end_date]').val(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
        if (scope.image) {
          params.image = scope.image;
        }
        Bazaarboy.post('lists/signup/create/', params, function(response) {
          if (response.status === 'OK') {
            swal({
              type: 'success',
              title: 'Success',
              text: 'Sign Up Form Created!'
            }, function() {
              return Bazaarboy.redirect('lists/');
            });
          } else {
            swal(response.message);
          }
        });
      });
      /*
      # edit channel
      $('a.save-channel-btn').click () ->
          params = {}
          params.profile = profileId
          if $('input[name=tagline]').val().trim() != ''
              params.tagline = $('input[name=tagline]').val()
          if $('input[name=hashtag]').val().trim() != ''
              params.hashtag = $('input[name=hashtag]').val()
          if scope.image?
              params.cover = scope.image
          Bazaarboy.post 'profile/channel/edit/', params, (response) ->
              if response.status is 'OK'
                  swal
                      type: 'success'
                      title: 'Success'
                      text: 'Channel Saved!'
                      () ->
                          location.reload()
              else
                  swal response.message
              return
          return
      */

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
            $('a.upload-image-btn').css('display', 'none');
            $('a.delete-image-btn').css('display', 'block');
            $('a.upload-image-btn').html('Upload Image');
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
              maxSize: 1260,
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
      $('a.upload-image-btn').click(function() {
        $('input[name=image_file]').click();
      });
      $('a.delete-image-btn').click(function() {
        scope.image = void 0;
        $('img#cover-image').attr('src', '');
        $('a.upload-cover-btn').css('display', 'block');
        $('a.delete-cover-btn').css('display', 'none');
      });
    }
  };

  Bazaarboy.profile.channel.init();

}).call(this);
