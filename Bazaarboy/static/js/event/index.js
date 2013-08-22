(function() {
  Bazaarboy.event.index = {
    description: void 0,
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
      scope = this;
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
      var collapseStates;
      collapseStates = [['div#event', [['margin-left', '63px', '96px']]], ['div#event.big_cover div.cover', [['width', '750px', '876px'], ['left', '-63px', '-96px']]], ['div#event > div.title', [['width', '750px', '876px'], ['left', '-63px', '-96px']]], ['div#event > div.title div.text', [['left', '63px', '96px']]]];
      $.merge(Bazaarboy.collapseStates, collapseStates);
      $('div#event div.action').click(function() {
        $('div#wrapper_overlay').fadeIn(200);
        $('div.event_overlay_canvas').fadeIn(200);
      });
      $('div#wrapper_overlay').click(function() {
        $('div#wrapper_overlay').fadeOut(200);
        $('div.event_overlay_canvas').fadeOut(200);
      });
      if (editable) {
        this.initEditing();
      } else {
        this.initTransaction();
      }
    }
  };

  Bazaarboy.event.index.init();

}).call(this);
