(function() {
  Bazaarboy.event.index = {
    description: void 0,
    map: void 0,
    cover: void 0,
    uploads: {
      cover: void 0
    },
    coverEditInProgress: false,
    drawMapWithCenter: function(latitude, longitude) {
      var canvas, center, mapOpts, marker, markerPos;
      center = new google.maps.LatLng(latitude + 0.0015, longitude);
      mapOpts = {
        center: center,
        zoom: 14,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        draggable: false,
        mapTypeControl: false,
        overviewMapControl: false,
        streetViewControl: false,
        scaleControl: false,
        zoomControl: false
      };
      canvas = document.getElementById('map_canvas');
      this.map = new google.maps.Map(canvas, mapOpts);
      markerPos = new google.maps.LatLng(latitude, longitude);
      marker = new google.maps.Marker({
        position: markerPos
      });
      marker.setMap(this.map);
    },
    initTransaction: function() {
      $('div#rsvp form.login').submit(function(event) {
        event.preventDefault();
        Bazaarboy.get('user/auth/', $(this).serializeObject(), function(response) {
          if (response.status === 'OK') {
            window.location.hash = '#rsvp';
            window.location.reload();
          } else {
            console.log(response);
          }
        });
      });
      $('div#rsvp form.register').submit(function(event) {
        event.preventDefault();
        Bazaarboy.post('user/create/', $(this).serializeObject(), function(response) {
          if (response.status === 'OK') {
            window.location.hash = '#rsvp';
            window.location.reload();
          } else {
            console.log(response);
          }
        });
      });
      $('div#rsvp form.register').submit(function(event) {
        event.preventDefault();
      });
      if ((window.location.hash != null) && window.location.hash === '#rsvp' && editable) {
        $('div#event div.action').click();
      }
    },
    save: function(params, cb) {
      params.id = eventId;
      if (typeof token !== "undefined" && token !== null) {
        params.token = token;
      }
      Bazaarboy.post('event/edit/', params, function(response) {
        var err;
        if (response.status === 'OK') {
          return cb(null, response.event);
        } else {
          err = {
            error: response.error,
            message: response.message
          };
          return cb(err, null);
        }
      });
    },
    startEditingTitle: function() {
      var title;
      $('div#event div.title div.text').addClass('hidden');
      $('div#event div.title div.editor').removeClass('hidden');
      title = $('div#event div.title div.editor input').val();
      $('div#event div.title div.editor input').focus().val('').val(title);
      $('div#event div.title div.button').html('Save').addClass('stick');
    },
    stopEditingTitle: function() {
      var title,
        _this = this;
      title = $('div#event div.title div.editor input').val();
      this.save({
        name: title
      }, function(err, event) {
        if (!err) {
          $('div#event div.title div.text').html(title).removeClass('hidden');
          $('div#event div.title div.editor input').val(title);
          $('div#event div.title div.editor').addClass('hidden');
          $('div#event div.title div.button').html('Edit').removeClass('stick');
        } else {
          alert(err.message);
        }
      });
    },
    prepareUploadedCoverImage: function(coverUrl) {
      var scope,
        _this = this;
      if (!$('body').hasClass('collapsed')) {
        Bazaarboy.switchCollapsedStates(function() {
          _this.prepareUploadedCoverImage(coverUrl);
        });
        return;
      }
      $('div#event').addClass('big_cover').addClass('with_caption');
      scope = this;
      $('<img>').attr('src', mediaUrl + coverUrl).addClass('editing').load(function() {
        var frame, frameHeight, frameWidth;
        scope.uploads.cover.width = this.width;
        scope.uploads.cover.height = this.height;
        frame = $('div#event div.cover div.image');
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
      this.coverEditInProgress = true;
      frame = $('div#event div.cover div.image');
      coverImage = $('div#event div.cover div.image img').css({
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
      $('div#event div.cover div.controls span').removeClass('hidden');
      $('div#event div.cover div.controls a.edit').addClass('hidden').html('Edit Cover');
      $('div#event div.cover div.controls a.delete').addClass('hidden');
      $('div#event div.cover div.controls a.save').removeClass('hidden');
      $('div#event div.cover div.controls a.cancel').removeClass('hidden');
      maskZ = parseInt($('div#wrapper_overlay').css('z-index'));
      $('div#event div.cover').css({
        'z-index': maskZ + 1
      });
      $('div#event > div.title').css({
        'z-index': maskZ + parseInt($('div#event > div.title').css('z-index'))
      });
      $('div#event div.frame div.right div.info').not('div.action').not('div.details').not('div.facebook').css('z-index', maskZ - 1);
      $('div#wrapper_overlay').fadeIn(200);
      $('div#event div.cover div.controls').addClass('stick');
    },
    stopEditingCoverImage: function(cover) {
      if (cover == null) {
        cover = null;
      }
      $('div#event div.cover div.image div.bounds img').remove();
      $('div#event div.cover div.image div.bounds').css({
        width: '',
        height: '',
        top: '',
        left: ''
      });
      if (cover != null) {
        if (cover) {
          $('div#event div.cover div.image div.bounds').append(cover);
        } else {
          $('div#event').removeClass('with_caption').removeClass('big_cover');
          $('div#event div.cover div.controls').addClass('stick');
          $('div#event div.cover div.controls a.edit').html('Add Cover');
        }
      }
      $('div#event div.cover').css('z-index', '');
      $('div#event > div.title').css('z-index', '');
      $('div#event div.frame div.right div.info').not('div.action').not('div.details').not('div.facebook').css('z-index', '');
      $('div#wrapper_overlay').fadeOut(200);
      $('div#event div.cover div.controls span').addClass('hidden');
      $('div#event div.cover div.controls a.edit').removeClass('hidden');
      $('div#event div.cover div.controls a.delete').removeClass('hidden');
      $('div#event div.cover div.controls a.save').addClass('hidden');
      $('div#event div.cover div.controls a.cancel').addClass('hidden');
      $('div#event div.cover div.controls').removeClass('stick');
      this.coverEditInProgress = false;
    },
    saveCoverImage: function() {
      var bounds, coverImage, frame, height, scale, viewport, width, x, y,
        _this = this;
      frame = $('div#event div.cover div.image');
      bounds = $('div#event div.cover div.image div.bounds');
      coverImage = $('div#event div.cover div.image div.bounds img');
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
          }, function(err, event) {
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
      }, function(err, event) {
        if (!err) {
          $('div#event div.cover div.image div.bounds img').remove();
          $('div#event div.cover div.controls a.edit').html('Add Cover');
          $('div#event div.cover div.controls a.delete').addClass('hidden');
          $('div#event div.cover div.controls').addClass('stick');
          $('div#event').removeClass('big_cover').removeClass('with_caption');
          _this.cover = null;
        } else {
          alert(err.message);
        }
      });
    },
    startEditingCoverCaption: function() {
      var caption;
      $('div#event div.cover div.caption div.text').addClass('hidden');
      $('div#event div.cover div.caption div.editor').removeClass('hidden');
      caption = $('div#event div.cover div.caption div.editor input').val();
      $('div#event div.cover div.caption div.editor input').focus().val('').val(caption);
      $('div#event div.cover div.caption div.button').html('Save').addClass('stick');
    },
    stopEditingCoverCaption: function() {
      var caption,
        _this = this;
      caption = $('div#event div.cover div.caption div.editor input').val();
      this.save({
        caption: caption
      }, function(err, event) {
        var captionText;
        if (!err) {
          captionText = caption;
          if (caption.length === 0) {
            captionText = '<i>No caption yet.</i>';
          }
          $('div#event div.cover div.caption div.text').html(captionText).removeClass('hidden');
          $('div#event div.cover div.caption div.editor input').val(caption);
          $('div#event div.cover div.caption div.editor').addClass('hidden');
          $('div#event div.cover div.caption div.button').html('Edit').removeClass('stick');
        } else {
          alert(err.message);
        }
      });
    },
    startEditingDescription: function() {
      $('div.description div.controls a.edit').html('Cancel');
      $('div.description div.controls a.save').show();
      $('div.description div.editor').addClass('editing');
      $('div.description div.editor div.inner').redactor({
        buttons: ['formatting', 'bold', 'italic', 'deleted', 'fontcolor', 'alignment', '|', 'unorderedlist', 'orderedlist', 'outdent', 'indent', '|', 'image', 'video', 'link', '|', 'html'],
        boldTag: 'b',
        italicTag: 'i'
      });
    },
    stopEditingDescription: function(description) {
      $('div.description div.controls a.edit').html('Edit');
      $('div.description div.controls a.save').hide();
      $('div.description div.editor').removeClass('editing');
      $('div.description div.editor div.inner').redactor('destroy');
      $('div.description div.editor div.inner').html(description);
    },
    saveDescription: function() {
      var description,
        _this = this;
      description = $('div.description div.editor div.inner').redactor('get');
      this.save({
        description: description
      }, function(err, event) {
        if (!err) {
          _this.description = event.description;
          _this.stopEditingDescription(_this.description);
        } else {
          alert(err.message);
        }
      });
    },
    startEditingSummary: function() {
      $('div#event div.summary div.body div.text').addClass('hidden');
      $('div#event div.right div.summary div.editor').removeClass('hidden');
      $('div#event div.right div.summary div.button').html('Save').addClass('stick');
    },
    stopEditingSummary: function() {
      var summary,
        _this = this;
      summary = $('div#event div.summary div.editor textarea').val().trim();
      this.save({
        summary: summary
      }, function(err, event) {
        var summaryText;
        if (!err) {
          summaryText = summary;
          if (summary.length === 0) {
            summaryText = '<i>No summary yet.</i>';
          }
          $('div#event div.summary div.body div.text').html(summaryText).removeClass('hidden');
          $('div#event div.summary div.editor textarea').val(summary);
          $('div#event div.summary div.editor').addClass('hidden');
          $('div#event div.summary div.button').html('Edit').removeClass('stick');
        } else {
          alert(err.message);
        }
      });
    },
    startEditingTags: function() {
      $('div#event div.tags div.body div.text').addClass('hidden');
      $('div#event div.right div.tags div.editor').removeClass('hidden');
      $('div#event div.right div.tags div.button').html('Save').addClass('stick');
    },
    stopEditingTags: function() {
      var tags,
        _this = this;
      tags = $('div#event div.tags div.editor textarea').val().trim();
      this.save({
        tags: tags
      }, function(err, event) {
        var tag, tagsText, _i, _len;
        if (!err) {
          $('div#event div.tags div.editor textarea').val(tags);
          tagsText = '<i>No tags yet.</i>';
          if (tags.length !== 0) {
            tagsText = '';
            tags = tags.split(',');
            for (_i = 0, _len = tags.length; _i < _len; _i++) {
              tag = tags[_i];
              tagsText += "<div class=\"tag\">" + tag + "</div>";
            }
            tagsText += '<div class="clear"></div>';
          }
          $('div#event div.tags div.body div.text').html(tagsText).removeClass('hidden');
          $('div#event div.tags div.editor').addClass('hidden');
          $('div#event div.tags div.button').html('Edit').removeClass('stick');
        } else {
          alert(err.message);
        }
      });
    },
    initEditing: function() {
      var scope,
        _this = this;
      scope = this;
      $('div#event div.title div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingTitle();
        } else {
          scope.startEditingTitle();
        }
      });
      return;
      this.cover = $('div#event div.cover div.image div.bounds img');
      if (this.cover.length > 0) {
        this.cover = this.cover.clone();
      }
      $('div#event div.cover a.edit').click(function() {
        $('div#event div.cover input[name=image_file]').click();
      });
      $('div#event div.cover a.delete').click(function() {
        if (confirm('Are you sure you want to delete the cover image?')) {
          _this.deleteCoverImage();
        }
      });
      $('div#event div.cover a.save').click(function() {
        _this.saveCoverImage();
      });
      $('div#event div.cover a.cancel').click(function() {
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
      $('div#event div.cover input[name=image_file]').fileupload({
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
      $('div#event div.cover div.caption div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingCoverCaption();
        } else {
          scope.startEditingCoverCaption();
        }
      });
      this.description = $('div#event div.description div.inner').html();
      $('div#event div.description div.controls a.save').hide().click(function() {
        return _this.saveDescription();
      });
      $('div#event div.description div.controls a.edit').click(function() {
        if ($('div.description div.editor').hasClass('editing')) {
          _this.stopEditingDescription(_this.description);
        } else {
          _this.startEditingDescription();
        }
      });
      $('div#event div.summary div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingSummary();
        } else {
          scope.startEditingSummary();
        }
      });
      $('div#event div.tags div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingTags();
        } else {
          scope.startEditingTags();
        }
      });
    },
    init: function() {
      var collapseStates,
        _this = this;
      collapseStates = [['div#event', [['margin-left', '63px', '96px']]], ['div#event.big_cover div.cover', [['width', '750px', '876px'], ['left', '-63px', '-96px']]], ['div#event div.cover div.image', [['left', '-126px', '0']]], ['div#event > div.title', [['width', '750px', '876px'], ['left', '-63px', '-96px']]], ['div#event.big_cover div.cover div.caption', [['width', '750px', '876px']]], ['div#event.big_cover div.cover div.caption div.inner', [['margin-left', '63px', '96px']]], ['div#event > div.title', [['width', '750px', '876px'], ['left', '-63px', '-96px']]], ['div#event > div.title div.inner', [['left', '63px', '96px']]]];
      $.merge(Bazaarboy.collapseStates, collapseStates);
      $('div#event div.action').click(function() {
        $('div#wrapper_overlay').fadeIn(200);
        $('div.event_overlay_canvas').fadeIn(200);
      });
      $('div#wrapper_overlay').click(function() {
        if (!_this.coverEditInProgress) {
          $('div#wrapper_overlay').fadeOut(200);
          $('div.event_overlay_canvas').fadeOut(200);
        }
      });
      /*
      latitude = parseFloat $('div#event div.details div.map').attr('data-latitude')
      longitude = parseFloat $('div#event div.details div.map').attr('data-longitude')
      if latitude isnt NaN and longitude isnt NaN
          @drawMapWithCenter latitude, longitude
      */

      if (editable) {
        this.initEditing();
      } else {
        this.initTransaction();
      }
    }
  };

  Bazaarboy.event.index.init();

}).call(this);