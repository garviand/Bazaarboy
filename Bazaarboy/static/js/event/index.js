(function() {
  Bazaarboy.event.index = {
    description: void 0,
    map: void 0,
    cover: void 0,
    uploads: {
      cover: void 0
    },
    coverEditInProgress: false,
    purchaseInProgress: false,
    /*
    drawMapWithCenter: (latitude, longitude) ->
        center = new google.maps.LatLng(latitude + 0.0015, longitude)
        mapOpts = 
            center: center
            zoom: 14
            mapTypeId: google.maps.MapTypeId.ROADMAP
            draggable: false
            mapTypeControl: false
            overviewMapControl: false
            streetViewControl: false
            scaleControl: false
            zoomControl: false
        canvas = document.getElementById('map_canvas')
        @map = new google.maps.Map(canvas, mapOpts)
        markerPos = new google.maps.LatLng(latitude, longitude)
        marker = new google.maps.Marker({position: markerPos})
        marker.setMap @map
        return
    */

    adjustSidebarPosition: function() {
      var count, hangingButtons, i, sidebarPadding, topBase, _i;
      hangingButtons = $('div#event > div.title div.bottom div.hanging').not('div.hidden');
      count = hangingButtons.length;
      topBase = parseFloat($(hangingButtons[0]).css('top'));
      for (i = _i = 0; 0 <= count ? _i < count : _i > count; i = 0 <= count ? ++_i : --_i) {
        $(hangingButtons[i]).css('top', (topBase + (48 + 10) * i) + 'px');
      }
      if ($('div#event').hasClass('with_cover')) {
        $('div#event div.frame > div.right').css('padding-top', '');
      } else {
        sidebarPadding = count * (48 + 10) + 10;
        $('div#event div.frame > div.right').css({
          'padding-top': sidebarPadding + 'px'
        });
      }
    },
    /*
    adjustTitlePosition: () ->
        offset = $(window).scrollTop()
        topHeight = $('div#wrapper_top').outerHeight()
        if offset > topHeight
            $('div#event > div.title').css
                'position': 'fixed'
                'top': 0
            $('div#event div.cover').css
                'margin-top': $('div#event > div.title').outerHeight() + 'px'
        else
            $('div#event > div.title').css
                'position': ''
                'top': ''
            $('div#event div.cover').css
                'margin-top': ''
        return
    */

    adjustOverlayHeight: function() {
      var overlayHeight, visibleDiv, _i, _len, _ref;
      overlayHeight = 10;
      _ref = $('div.event_overlay_canvas > div').not('div.hidden');
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        visibleDiv = _ref[_i];
        overlayHeight += $(visibleDiv).outerHeight() + 10;
      }
      $('div.event_overlay_canvas').css({
        'margin-top': 0
      });
      $('div.event_overlay_canvas').height(overlayHeight);
    },
    share: function() {
      var caption, description, editorImages, event_image, image, name, url;
      url = window.location.href;
      name = $('div#event > div.title div.top div.text').text();
      caption = $('div#event > div.title div.top div.details').text();
      description = $('div#event div.summary div.body div.text').text();
      image = $('div#event div.cover div.image img');
      if (image.length === 0) {
        editorImages = $('div#event div.frame div.editor .inner').find('img');
        if (editorImages.length > 0) {
          image = editorImages[0].src;
        } else {
          event_image = 'DEFAULT_IMAGE';
        }
      } else {
        image = image.src;
      }
      return FB.ui({
        method: 'feed',
        link: url,
        name: name,
        caption: caption,
        description: description,
        picture: image
      }, function(response) {});
    },
    purchase: function(ticket, email, fullName, phone) {
      var params,
        _this = this;
      if (email == null) {
        email = null;
      }
      if (fullName == null) {
        fullName = null;
      }
      if (phone == null) {
        phone = null;
      }
      this.purchaseInProgress = true;
      $('div#rsvp div.action a.confirm').css('display', 'none');
      $('div#rsvp div.action div.loading').removeClass('hidden');
      params = {
        ticket: ticket
      };
      if ((email != null) && (fullName != null)) {
        params.email = email;
        params.full_name = fullName;
      }
      if (phone != null) {
        params.phone = phone;
      }
      Bazaarboy.post('event/purchase/', params, function(response) {
        var checkoutDescription;
        $('div#rsvp div.action a.confirm').css('display', '');
        $('div#rsvp div.action div.loading').addClass('hidden');
        if (response.status === 'OK') {
          $('div#rsvp div.confirmation div.code b').html(response.purchase.code);
          if (response.publishable_key != null) {
            checkoutDescription = response.purchase.event.name + ' ' + response.purchase.ticket.name;
            StripeCheckout.open({
              key: response.publishable_key,
              address: false,
              amount: Math.round(response.purchase.price * 100),
              currency: 'usd',
              name: response.purchase.event.name,
              description: checkoutDescription,
              panelLabel: 'Checkout',
              token: function(token) {
                $('div#rsvp div.action a.confirm').css('display', 'none');
                $('div#rsvp div.action div.loading').removeClass('hidden');
                Bazaarboy.post('payment/charge/', {
                  checkout: response.purchase.checkout,
                  stripe_token: token.id
                }, function(response) {
                  $('div#rsvp div.action a.confirm').css('display', '');
                  $('div#rsvp div.action div.loading').addClass('hidden');
                  if (response.status === 'OK') {
                    _this.completeCheckout();
                  } else {
                    alert(response.message);
                  }
                });
              }
            });
          } else {
            _this.completeCheckout();
          }
        } else {
          alert(response.message);
        }
      });
    },
    completeCheckout: function() {
      var scope;
      scope = this;
      $('div#rsvp div.confirmation').removeClass('hidden');
      this.adjustOverlayHeight();
      $('div#rsvp div.tickets').addClass('collapsed');
      $('div#rsvp div.tickets div.ticket').not('div.selected').animate({
        'height': 0
      }, function() {
        $(this).addClass('hidden');
      });
      $('div#rsvp div.action').css('overflow', 'hidden').animate({
        'height': 0
      }, function() {
        $(this).addClass('hidden');
      });
      $('div#rsvp div.info').css('overflow', 'hidden').animate({
        'height': 0
      }, function() {
        $(this).addClass('hidden');
        scope.adjustOverlayHeight();
      });
    },
    initTransaction: function() {
      var scope,
        _this = this;
      scope = this;
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
      $('div#rsvp div.ticket.valid').click(function() {
        if (!$('div#rsvp div.tickets').hasClass('collapsed')) {
          $('div#rsvp div.ticket.valid').removeClass('selected');
          $('div#rsvp div.ticket.valid input[type=radio]').prop('checked', false);
          $(this).addClass('selected');
          $(this).find('input[type=radio]').prop('checked', true);
          $('div#rsvp div.action').removeClass('hidden');
          $('div#rsvp div.confirmation div.ticket').html($(this).find('div.name').html());
          $('div#rsvp div.confirmation div.price b').html($(this).find('div.price b').html());
        }
      });
      $('div#rsvp div.action a.confirm').click(function() {
        var email, fullName, phone, ticket;
        if ($('div#rsvp div.ticket.valid.selected').length > 0) {
          ticket = $('div#rsvp div.ticket.valid.selected').attr('data-id');
          if ($('div#rsvp div.info').length === 0) {
            _this.purchase(ticket);
          } else {
            email = $('div#rsvp div.info input[name=email]').val();
            fullName = $('div#rsvp div.info input[name=full_name]').val();
            phone = $('div#rsvp div.info input[name=phone]').val();
            if (email.trim() === '') {
              alert('You must enter a valid email address.');
              return;
            }
            if (fullName.trim() === '') {
              alert('You must enter your full name,');
              return;
            }
            if (phone.trim() === '') {
              phone = null;
            }
            _this.purchase(ticket, email, fullName, phone);
          }
        }
      });
      if ((window.location.hash != null) && window.location.hash === '#rsvp' && !editable) {
        $('div#event div.title div.bottom > div.action').click();
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
      $('div#event > div.title div.top div.text').addClass('hidden');
      $('div#event > div.title div.top div.editor').removeClass('hidden');
      title = $('div#event > div.title div.top div.editor input').val();
      $('div#event > div.title div.top div.editor input').focus().val('').val(title);
      $('div#event > div.title div.top div.button').html('Save').addClass('stick');
    },
    stopEditingTitle: function() {
      var title,
        _this = this;
      title = $('div#event > div.title div.top div.editor input').val();
      this.save({
        name: title
      }, function(err, event) {
        if (!err) {
          $('div#event > div.title div.top div.text').html(title).removeClass('hidden');
          $('div#event > div.title div.top div.editor input').val(title);
          $('div#event > div.title div.top div.editor').addClass('hidden');
          $('div#event > div.title div.top div.button').html('Edit').removeClass('stick');
          document.title = title;
        } else {
          alert(err.message);
        }
      });
    },
    startEditingTimeLocation: function() {
      $('div#event > div.title div.details div.text').addClass('hidden');
      $('div#event > div.title div.details div.editor').removeClass('hidden');
      $('div#event > div.title div.bottom > div.button').html('Save').addClass('stick');
    },
    stopEditingTimeLocation: function() {
      var endDate, endTime, location, startDate, startTime,
        _this = this;
      startDate = $('div#event > div.title input[name=start_date]').val();
      if (!moment(startDate, 'MM/DD/YYYY').isValid()) {
        return;
      }
      startTime = $('div#event > div.title input[name=start_time]').val();
      if (!moment(startTime, 'h:mm a').isValid()) {
        return;
      }
      startTime = moment(startDate + ' ' + startTime, 'MM/DD/YYYY h:mm A');
      endDate = $('div#event > div.title input[name=end_date]').val();
      endTime = $('div#event > div.title input[name=end_time]').val();
      if (endDate.trim().length === 0 && endTime.trim().length === 0) {
        endTime = false;
      } else {
        if (!moment(endDate, 'MM/DD/YYYY').isValid()) {
          return;
        }
        if (!moment(endTime, 'h:mm a').isValid()) {
          return;
        }
        endTime = moment(endDate + ' ' + endTime, 'MM/DD/YYYY h:mm A');
      }
      location = $('div#event > div.title input[name=location]').val().trim();
      if (location.length === 0) {
        location = 'none';
      }
      this.save({
        start_time: startTime.utc().format('YYYY-MM-DD HH:mm:ss'),
        end_time: endTime ? endTime.utc().format('YYYY-MM-DD HH:mm:ss') : 'none',
        location: location
      }, function(err, event) {
        var timeLocation, timeString;
        if (!err) {
          timeString = '';
          startTime = startTime.local();
          if (startTime.format('mm') === '00') {
            timeString += startTime.format('dddd, MMM Do, ha');
          } else {
            timeString += startTime.format('dddd, MMM Do, h:mma');
          }
          if (endTime) {
            timeString += ' - ';
            endTime = endTime.local();
            if (endTime.format('D') === startTime.format('D')) {
              if (endTime.format('mm') === '00') {
                timeString += endTime.format('ha');
              } else {
                timeString += endTime.format('h:mma');
              }
            } else {
              if (endTime.format('mm') === '00') {
                timeString += endTime.format('dddd, MMM Do, ha');
              } else {
                timeString += endTime.format('dddd, MMM Do, h:mma');
              }
            }
          }
          timeLocation = timeString + ' at <b>' + event.location + '</b>';
          $('div#event > div.title div.details div.text').html(timeLocation);
          $('div#event > div.title div.details div.text').removeClass('hidden');
          $('div#event > div.title div.details div.editor').addClass('hidden');
          $('div#event > div.title div.bottom > div.button').html('Edit').removeClass('stick');
        } else {
          alert(err.message);
        }
      });
    },
    prepareUploadedCoverImage: function(coverUrl) {
      var scope;
      $('div#event').addClass('with_cover');
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
        scope.adjustSidebarPosition();
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
      $('div#event > div.title div.bottom div.controls span').removeClass('hidden');
      $('div#event > div.title div.bottom div.controls a.edit').addClass('hidden').html('Edit Cover');
      $('div#event > div.title div.bottom div.controls a.delete').addClass('hidden');
      $('div#event > div.title div.bottom div.controls a.save').removeClass('hidden');
      $('div#event > div.title div.bottom div.controls a.cancel').removeClass('hidden');
      maskZ = parseInt($('div#wrapper_overlay').css('z-index'));
      $('div#event div.cover').css({
        'z-index': maskZ + 1
      });
      $('div#event > div.title').css({
        'z-index': maskZ + parseInt($('div#event > div.title').css('z-index'))
      });
      $('div#event div.frame div.right div.info').css('z-index', maskZ - 1);
      $('div#wrapper_overlay').fadeIn(200);
      $('div#event > div.title div.bottom div.controls').addClass('stick');
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
          $('div#event > div.title div.bottom div.controls').addClass('stick');
          $('div#event > div.title div.bottom div.controls a.edit').html('Add Cover');
        }
      }
      $('div#event div.cover').css('z-index', '');
      $('div#event > div.title').css('z-index', '');
      $('div#event div.frame div.right div.info').css('z-index', '');
      $('div#wrapper_overlay').fadeOut(200);
      $('div#event > div.title div.bottom div.controls span').addClass('hidden');
      $('div#event > div.title div.bottom div.controls a.edit').removeClass('hidden');
      $('div#event > div.title div.bottom div.controls a.delete').removeClass('hidden');
      $('div#event > div.title div.bottom div.controls a.save').addClass('hidden');
      $('div#event > div.title div.bottom div.controls a.cancel').addClass('hidden');
      $('div#event > div.title div.bottom div.controls').removeClass('stick');
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
          $('div#event > div.title div.bottom div.controls a.edit').html('Add Cover');
          $('div#event > div.title div.bottom div.controls a.delete').addClass('hidden');
          $('div#event > div.title div.bottom div.controls').addClass('stick');
          $('div#event').removeClass('with_cover');
          _this.adjustSidebarPosition();
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
    addTicket: function() {
      var ticket;
      if (!$('div#tickets div.tickets div.empty').hasClass('hidden')) {
        $('div#tickets div.tickets div.empty').addClass('hidden');
      }
      ticket = $('div#tickets div.ticket.template').clone(true);
      $(ticket).removeClass('hidden').prependTo($('div#tickets div.tickets'));
      this.startEditingTicket(ticket);
    },
    deleteTicket: function(ticket) {
      var id,
        _this = this;
      id = $(ticket).attr('data-id');
      if ((id == null) || id.trim().length === 0) {
        $(ticket).remove();
        if ($('div#tickets div.tickets div.ticket').length === 0) {
          $('div#tickets div.tickets div.empty').removeClass('hidden');
        }
      } else {
        if (confirm('Are you sure you want to delete this ticket?')) {
          Bazaarboy.post('event/ticket/delete/', {
            id: id
          }, function(response) {
            if (response.status === 'OK') {
              $(ticket).remove();
              if ($('div#tickets div.tickets div.ticket').length === 0) {
                $('div#tickets div.tickets div.empty').removeClass('hidden');
              }
            } else {
              alert(response.message);
            }
          });
        }
      }
    },
    startEditingTicket: function(ticket) {
      $(ticket).find('a.switch').html('Save').removeClass('edit').addClass('save');
      $(ticket).addClass('editing');
    },
    stopEditingTicket: function(ticket) {
      var data, endpoint, id,
        _this = this;
      id = $(ticket).attr('data-id');
      data = $(ticket).find('form').serializeObject();
      endpoint = '';
      if ((id == null) || id.trim().length === 0) {
        endpoint = 'event/ticket/create/';
        data.event = eventId;
        if (data.quantity.trim() === '') {
          delete data.quantity;
        }
        if (data.start_time.trim() === '') {
          delete data.start_time;
        }
        if (data.end_time.trim() === '') {
          delete data.end_time;
        }
      } else {
        endpoint = 'event/ticket/edit/';
        data.id = id;
        if (data.quantity.trim() === '') {
          data.quantity = 'none';
        }
        if (data.start_time.trim() === '') {
          data.start_time = 'none';
        }
        if (data.end_time.trim() === '') {
          data.end_time = 'none';
        }
      }
      if (typeof token !== "undefined" && token !== null) {
        data.token = token;
      }
      Bazaarboy.post(endpoint, data, function(response) {
        var key, value, _ref;
        if (response.status !== 'OK') {
          alert(response.message);
        } else {
          console.log(response.ticket);
          _ref = response.ticket;
          for (key in _ref) {
            value = _ref[key];
            if (key === 'pk') {
              $(ticket).attr('data-id', response.ticket.pk);
            } else if (key === 'price') {
              $(ticket).find('div.price div.text').html("$ " + response.ticket.price);
            } else {
              $(ticket).find("div." + key + " div.text").html(response.ticket[key]);
              $(ticket).find("div." + key + " div.editor input").val(response.ticket[key]);
            }
          }
          $(ticket).find('a.swith').html('Edit').addClass('edit').removeClass('save');
          $(ticket).find('a.delete').removeClass('cancel');
          $(ticket).removeClass('editing');
        }
      });
    },
    switchLaunchState: function() {
      var _this = this;
      if ($('div#event > div.title div.bottom div.launch').hasClass('launched')) {
        if (confirm('Are you sure you want to take the event offline?')) {
          Bazaarboy.post('event/delaunch/', {
            id: eventId
          }, function(response) {
            if (response.status === 'OK') {
              $('div#event > div.title div.bottom div.launch').removeClass('launched').find('b').html('Launch Event');
              $('div#event > div.title div.bottom div.share').addClass('hidden');
              _this.adjustSidebarPosition();
            } else {
              alert(response.message);
            }
          });
        }
      } else {
        Bazaarboy.post('event/launch/', {
          id: eventId
        }, function(response) {
          if (response.status === 'OK') {
            $('div#event > div.title div.bottom div.launch').addClass('launched').find('b').html('Take Event Offline');
            $('div#event > div.title div.bottom div.share').removeClass('hidden');
            _this.adjustSidebarPosition();
          } else {
            alert(response.message);
          }
        });
      }
    },
    initEditing: function() {
      var scope,
        _this = this;
      scope = this;
      $('div#event > div.title div.bottom div.launch').click(function() {
        _this.switchLaunchState();
      });
      $('div#event > div.title div.top div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingTitle();
        } else {
          scope.startEditingTitle();
        }
      });
      $('div#event > div.title div.details input[name=start_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
      $('div#event > div.title div.details input[name=end_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
      $('div#event > div.title div.bottom > div.button').click(function() {
        if ($(this).hasClass('stick')) {
          scope.stopEditingTimeLocation();
        } else {
          scope.startEditingTimeLocation();
        }
      });
      this.cover = $('div#event div.cover div.image div.bounds img');
      if (this.cover.length > 0) {
        this.cover = this.cover.clone();
      }
      $('div#event > div.title div.bottom div.controls a.edit').click(function() {
        $('div#event > div.title div.bottom div.controls input[name=image_file]').click();
      });
      $('div#event > div.title div.bottom div.controls a.delete').click(function() {
        if (confirm('Are you sure you want to delete the cover image?')) {
          _this.deleteCoverImage();
        }
      });
      $('div#event > div.title div.bottom div.controls a.save').click(function() {
        _this.saveCoverImage();
      });
      $('div#event > div.title div.bottom div.controls a.cancel').click(function() {
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
      $('div#event > div.title div.bottom div.controls input[name=image_file]').fileupload({
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
      $('div#tickets div.controls a.add').click(function() {
        _this.addTicket();
      });
      $('div#tickets div.ticket a.switch').click(function() {
        var ticket;
        ticket = $(this).parent().parent().parent();
        if ($(this).hasClass('edit')) {
          scope.startEditingTicket(ticket);
        } else if ($(this).hasClass('save')) {
          scope.stopEditingTicket(ticket);
        }
      });
      $('div#tickets div.ticket a.delete').click(function() {
        var ticket;
        ticket = $(this).parent().parent().parent();
        scope.deleteTicket(ticket);
      });
    },
    init: function() {
      var _this = this;
      $('div#event div.title div.bottom > div.action').click(function() {
        $('div#wrapper_overlay').fadeIn(200);
        $('div.event_overlay_canvas').css({
          'top': $('div#event > div.title').height() + 20
        });
        $('div.event_overlay_canvas').fadeIn(200);
        _this.adjustOverlayHeight();
      });
      $('div#wrapper_overlay').click(function() {
        if (!_this.coverEditInProgress) {
          $('div#wrapper_overlay').fadeOut(200);
          $('div.event_overlay_canvas').fadeOut(200);
        }
      });
      this.adjustSidebarPosition();
      /*
      $(window).scroll () =>
          @adjustTitlePosition()
          return
      */

      $('div#event div.share').click(function() {
        _this.share();
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
