(function() {
  Bazaarboy.profile.index = {
    description: void 0,
    image: void 0,
    cover: void 0,
    uploads: {
      image: void 0,
      cover: void 0
    },
    switchTab: function(tab) {
      $('div#profile div.tabs div.tab').each(function() {
        if ($(this).hasClass(tab)) {
          $(this).addClass('show');
        } else {
          $(this).removeClass('show');
        }
      });
      $('div#profile div.frame div.wrapper > div').each(function() {
        if ($(this).hasClass(tab)) {
          $(this).addClass('show');
        } else {
          $(this).removeClass('show');
        }
      });
    },
    save: function(params, cb) {
      params.id = profileId;
      Bazaarboy.post('profile/edit/', params, function(response) {
        var err;
        if (response.status === 'OK') {
          return cb(null, response.profile);
        } else {
          err = {
            error: response.error,
            message: response.message
          };
          return cb(err, null);
        }
      });
    },
    prepareUploadedCoverImage: function(coverUrl) {
      var scope;
      scope = this;
      $('<img>').attr('src', mediaUrl + coverUrl).addClass('editing').load(function() {
        var frame, frameHeight, frameWidth;
        scope.uploads.cover.width = this.width;
        scope.uploads.cover.height = this.height;
        frame = $('div#profile div.cover div.image');
        frameWidth = $(frame).width();
        frameHeight = $(frame).height();
        if (this.width / this.height > frameWidth / frameHeight) {
          $(this).height(frameHeight);
          $(this).width(this.width / this.height * frameHeight);
        } else {
          $(this).width(frameWidth);
          $(this).height(this.height / this.width * frameWidth);
        }
        $(frame).find('div.bounds').children().remove();
        $(frame).find('div.bounds').append(this);
        scope.startEditingCoverImage();
      });
    },
    startEditingCoverImage: function() {
      var bounds, coverImage, frame, height, left, maskZ, top, width;
      frame = $('div#profile div.cover div.image');
      coverImage = $('div#profile div.cover div.image img').css({
        top: 0,
        left: 0
      });
      width = coverImage.width() * 2 - frame.width();
      height = coverImage.height() * 2 - frame.height();
      left = 0 - (width - frame.width()) / 2;
      top = 0 - (height - frame.height()) / 2;
      bounds = $(frame).find('div.bounds').css({
        width: width,
        height: height,
        top: top,
        left: left
      });
      $(coverImage).draggable({
        containment: bounds,
        scroll: false
      });
      $('div#profile div.cover div.controls span').removeClass('hidden');
      $('div#profile div.cover div.controls a.edit').addClass('hidden').html('Edit Cover');
      $('div#profile div.cover div.controls a.delete').addClass('hidden');
      $('div#profile div.cover div.controls a.save').removeClass('hidden');
      $('div#profile div.cover div.controls a.cancel').removeClass('hidden');
      maskZ = parseInt($('div#wrapper_overlay').css('z-index'));
      $('div#profile div.cover').css({
        'z-index': maskZ + 1
      });
      $('div#profile > div.title').css({
        'z-index': maskZ + parseInt($('div#profile > div.title').css('z-index'))
      });
      $('div#profile div.right div.image').css({
        'z-index': maskZ + parseInt($('div#profile div.right div.image').css('z-index'))
      });
      $('div#profile div.right div.action').css({
        'z-index': maskZ + parseInt($('div#profile div.right div.action').css('z-index'))
      });
      $('div#wrapper_overlay').fadeIn(200);
      $('div#profile div.cover div.controls').addClass('stick');
    },
    stopEditingCoverImage: function(cover) {
      if (cover == null) {
        cover = null;
      }
      $('div#profile div.cover div.image div.bounds img').remove();
      $('div#profile div.cover div.image div.bounds').css({
        width: '',
        height: '',
        top: '',
        left: ''
      });
      if (cover != null) {
        if (cover) {
          $('div#profile div.cover div.image div.bounds').append(cover);
        } else {
          $('div#profile div.cover div.controls a.edit').html('Add Cover');
        }
      }
      $('div#profile div.cover').css('z-index', '');
      $('div#profile > div.title').css('z-index', '');
      $('div#profile div.right div.image').css('z-index', '');
      $('div#profile div.right div.action').css('z-index', '');
      $('div#wrapper_overlay').fadeOut(200);
      $('div#profile div.cover div.controls span').addClass('hidden');
      $('div#profile div.cover div.controls a.edit').removeClass('hidden');
      $('div#profile div.cover div.controls a.delete').removeClass('hidden');
      $('div#profile div.cover div.controls a.save').addClass('hidden');
      $('div#profile div.cover div.controls a.cancel').addClass('hidden');
      $('div#profile div.cover div.controls').removeClass('stick');
    },
    saveCoverImage: function() {
      var bounds, coverImage, frame, height, scale, viewport, width, x, y,
        _this = this;
      frame = $('div#profile div.cover div.image');
      bounds = $('div#profile div.cover div.image div.bounds');
      coverImage = $('div#profile div.cover div.image div.bounds img');
      x = 0;
      y = 0;
      width = 0;
      height = 0;
      if (coverImage.width() > frame.width()) {
        scale = this.uploads.cover.height / frame.height();
        x = (Math.abs(parseInt($(bounds).css('left'))) - parseInt(coverImage.css('left'))) * scale;
        y = 0;
        width = frame.width() * scale;
        height = this.uploads.cover.height;
      } else {
        scale = this.uploads.cover.width / frame.width();
        x = 0;
        y = (Math.abs(parseInt($(bounds).css('top'))) - parseInt(coverImage.css('top'))) * scale;
        width = this.uploads.cover.width;
        height = frame.height() * scale;
      }
      x = parseInt(x);
      y = parseInt(y);
      width = parseInt(width);
      height = parseInt(height);
      viewport = "" + x + "," + y + "," + width + "," + height;
      console.log(viewport);
      Bazaarboy.post('file/image/crop/', {
        id: this.uploads.cover.pk,
        viewport: viewport
      }, function(response) {
        if (response.status === 'OK') {
          _this.save({
            cover: response.image.pk
          }, function(err, profile) {
            var scope;
            if (!err) {
              _this.cover = response.image;
              _this.cover.width = width;
              _this.cover.height = height;
              _this.uploads.cover = null;
              scope = _this;
              $('<img>').attr('src', mediaUrl + response.image.source).addClass('normal').load(function() {
                scope.stopEditingCoverImage(this);
              });
            } else {
              alert(err.message);
            }
          });
        } else {
          alert(response.message);
        }
      });
    },
    deleteCoverImage: function() {
      var _this = this;
      return this.save({
        cover: 'delete'
      }, function(err, profile) {
        if (!err) {
          $('div#profile div.cover div.image div.bounds img').remove();
          $('div#profile div.cover div.controls a.edit').html('Add Cover');
          $('div#profile div.cover div.controls a.delete').addClass('hidden');
          _this.cover = null;
        } else {
          alert(err.message);
        }
      });
    },
    startEditingDescription: function() {
      $('div.overview div.description div.controls a.edit').html('Cancel');
      $('div.overview div.description div.controls a.save').show();
      $('div.overview div.description div.editor').addClass('editing');
      $('div.overview div.description div.editor div.inner').redactor({
        buttons: ['formatting', 'bold', 'italic', 'deleted', 'fontcolor', 'alignment', '|', 'unorderedlist', 'orderedlist', 'outdent', 'indent', '|', 'image', 'video', 'link'],
        imageUpload: rootUrl
      });
    },
    stopEditingDescription: function(description) {
      $('div.overview div.description div.controls a.edit').html('Edit');
      $('div.overview div.description div.controls a.save').hide();
      $('div.overview div.description div.editor').removeClass('editing');
      $('div.overview div.description div.editor div.inner').redactor('destroy');
      $('div.overview div.description div.editor div.inner').html(description);
    },
    saveDescription: function() {
      var description,
        _this = this;
      description = $('div.overview div.description div.editor div.inner').redactor('get');
      this.save({
        description: description
      }, function(err, profile) {
        if (!err) {
          _this.description = profile.description;
          _this.stopEditingDescription(_this.description);
        } else {
          alert(err.message);
        }
      });
    },
    startEditingLogoImage: function() {
      var scope;
      scope = this;
      $('<img>').attr('src', mediaUrl + this.uploads.image.source).load(function() {
        $('div#profile div.frame div.right div.logo div.image').html('');
        $('div#profile div.frame div.right div.logo div.image').append(this);
        $('div#profile div.frame div.right div.logo a.upload').addClass('hidden');
        $('div#profile div.frame div.right div.logo a.delete').addClass('hidden');
        $('div#profile div.frame div.right div.logo a.save').removeClass('hidden');
        $('div#profile div.frame div.right div.logo a.cancel').removeClass('hidden');
      });
    },
    saveLogoImage: function() {
      var _this = this;
      this.save({
        image: this.uploads.image.pk
      }, function(err, profile) {
        if (!err) {
          _this.uploads.image = null;
          _this.stopEditingLogoImage();
        } else {
          alert(err.message);
        }
      });
    },
    deleteLogoImage: function() {
      var _this = this;
      if (confirm('Are you sure you want to delete the logo?')) {
        this.save({
          image: 'delete'
        }, function(err, profile) {
          if (!err) {
            _this.image = null;
            $('div#profile div.frame div.right div.logo div.image').html('');
          } else {
            alert(err.message);
          }
        });
      }
    },
    stopEditingLogoImage: function() {
      $('div#profile div.frame div.right div.logo a.upload').removeClass('hidden');
      $('div#profile div.frame div.right div.logo a.delete').removeClass('hidden');
      $('div#profile div.frame div.right div.logo a.save').addClass('hidden');
      $('div#profile div.frame div.right div.logo a.cancel').addClass('hidden');
    },
    initEditing: function() {
      var _this = this;
      this.description = $('div.overview div.description div.inner').html();
      $('div.overview div.description div.controls a.save').hide().click(function() {
        return _this.saveDescription();
      });
      $('div.overview div.description div.controls a.edit').click(function() {
        if ($('div.overview div.description div.editor').hasClass('editing')) {
          _this.stopEditingDescription(_this.description);
        } else {
          _this.startEditingDescription();
        }
      });
      this.cover = $('div#profile div.cover div.image div.bounds img');
      if (this.cover.length > 0) {
        this.cover = this.cover.clone();
      }
      $('div#profile div.cover a.edit').click(function() {
        $('div#profile div.cover input[name=image_file]').click();
      });
      $('div#profile div.cover a.delete').click(function() {
        if (confirm('Are you sure you want to delete the cover image?')) {
          _this.deleteCoverImage();
        }
      });
      $('div#profile div.cover a.save').click(function() {
        _this.saveCoverImage();
      });
      $('div#profile div.cover a.cancel').click(function() {
        var original;
        original = _this.cover != null ? _this.cover : false;
        _this.stopEditingCoverImage(original);
        if (_this.uploads.cover != null) {
          Bazaarboy.post('file/image/delete/', {
            id: _this.uploads.cover.pk
          }, function(response) {
            return _this.uploads.cover = null;
          });
        }
      });
      $('div#profile div.cover input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            if (_this.uploads.cover != null) {
              Bazaarboy.post('file/image/delete/', {
                id: _this.uploads.cover.pk
              });
            }
            _this.uploads.cover = response.image;
            _this.prepareUploadedCoverImage(response.image.source);
          } else {
            alert(response.message);
          }
        }
      });
      $('div#profile div.frame div.right div.logo a.upload').click(function() {
        $('div#profile div.frame div.right input[name=image_file]').click();
      });
      $('div#profile div.frame div.right div.logo a.delete').click(function() {
        _this.deleteLogoImage();
      });
      $('div#profile div.frame div.right div.logo a.save').click(function() {
        _this.saveLogoImage();
      });
      $('div#profile div.frame div.right div.logo a.cancel').click(function() {});
      $('div#profile div.frame div.right input[name=image_file]').fileupload({
        url: rootUrl + 'file/image/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            if (_this.uploads.image != null) {
              Bazaarboy.post('file/image/delete/', {
                id: _this.uploads.image.pk
              });
            }
            _this.uploads.image = response.image;
            _this.startEditingLogoImage();
          } else {
            alert(response.message);
          }
        }
      });
    },
    init: function() {
      var _this = this;
      $.each(['overview', 'events', 'sponsorships'], function(index, tab) {
        $('div.tabs div.tab.' + tab).click(function() {
          _this.switchTab(tab);
        });
      });
      if (editable) {
        this.initEditing();
      }
    }
  };

  Bazaarboy.profile.index.init();

}).call(this);
