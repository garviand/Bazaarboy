(function() {
  Bazaarboy.profile.manage = {
    init: function() {
      $('form.create input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(e, data) {
          var lastImgId;
          lastImgId = $('form.create input[name=image]').val();
          if (lastImgId !== '') {
            Bazaarboy.post('file/image/delete/', {
              id: lastImgId
            });
          }
          data.submit();
        },
        done: function(e, data) {
          var imgUrl, result;
          result = jQuery.parseJSON(data.result);
          if (result.status === 'OK') {
            $('form.create input[name=image]').val(result.image.pk);
            imgUrl = mediaUrl + result.image.source;
            $('form.create img').attr('src', imgUrl);
          } else {
            console.log(result);
          }
        }
      });
    }
  };

  Bazaarboy.profile.manage.init();

}).call(this);
