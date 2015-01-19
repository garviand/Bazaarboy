(function() {
  Bazaarboy.list.list = {
    uploads: {
      csv: void 0
    },
    submitting: false,
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('div.list').on('click', 'a.remove-member', function() {
        var member, member_id;
        member = $(this).closest('div.list-item');
        member_id = $(this).data('id');
        console.log(member_id);
        if (confirm('Are you sure you want to remove this person?')) {
          Bazaarboy.post('lists/remove/item/', {
            id: member_id
          }, function(response) {
            var member_count;
            if (response.status === 'OK') {
              member.remove();
              member_count = parseInt($('span.member-count').html()) - 1;
              $('span.member-count').html(member_count);
            } else {
              alert(response.message);
            }
          });
        }
      });
      $('a.start-member-add').click(function() {
        $('a.start-member-add').removeClass('secondary-btn');
        $('a.start-member-add').removeClass('active');
        $('a.start-member-add').addClass('secondary-btn-inverse');
        $(this).removeClass('secondary-btn-inverse');
        $(this).addClass('active');
        $(this).addClass('secondary-btn');
        $('div.member-add-interface').addClass('hide');
        $('a.cancel-add').css('display', 'block');
      });
      $('a.cancel-add').click(function() {
        $('a.start-member-add').removeClass('secondary-btn');
        $('a.start-member-add').removeClass('active');
        $('a.start-member-add').addClass('secondary-btn-inverse');
        $('div.member-add-interface').addClass('hide');
        $(this).css('display', 'none');
      });
      $('div.list-controls a.add-from-csv').click(function() {
        $('div.member-add-interface').addClass('hide');
        $('div.csv_upload_interface').removeClass('hide');
      });
      $('div.list-controls a.add-from-event').click(function() {
        $('div.member-add-interface').addClass('hide');
        $('div.event-add-interface').removeClass('hide');
      });
      $('div.list-controls a.add-single-item').click(function() {
        $('div.member-add-interface').addClass('hide');
        $('div.manual-add-interface').removeClass('hide');
      });
      $('div.manual-add-interface a.add-member-submit').click(function() {
        var params;
        $('div.manual-add-interface a.add-member-submit').html('Adding...');
        params = $('div.manual-add-interface form.add-item-form').serializeObject();
        params.id = listId;
        Bazaarboy.post('lists/add/item/', params, function(response) {
          var new_item;
          if (response.status === 'OK') {
            new_item = $('div#list-management div.list div.list-item.template').clone();
            new_item.find('div.name').html(response.item.first_name + " " + response.item.last_name);
            new_item.find('div.email').html(response.item.email);
            new_item.find('a.remove-member').attr('data-id', response.item.pk);
            new_item.removeClass('template');
            new_item.removeClass('hide');
            $('div#list-management div.list .list-items').prepend(new_item);
            $('div.manual-add-interface a.add-member-submit').html('Success!');
            $('div.manual-add-interface input[type=text]').val('');
            $('div.manual-add-interface textarea').val('');
            $('div.manual-add-interface textarea').html('');
            setTimeout(function() {
              return $('div.manual-add-interface a.add-member-submit').html('Add Member');
            }, 1000);
          } else {
            alert(response.message);
          }
        });
      });
      $('div.event-add-interface div.event-list div.event').click(function() {
        $(this).toggleClass('active');
      });
      $('div.event-add-interface a.cancel-event-add').click(function() {
        return $('a.cancel-add').click();
      });
      $('div.event-add-interface a.submit-event-add').click(function() {
        var added_members, duplicate_members, num_added, num_events, selected_events;
        if (!scope.submitting) {
          $(this).addClass('disabled-btn');
          $(this).html('Adding...');
          scope.submitting = true;
          selected_events = $('div.event-add-interface div.event-list div.event.active');
          num_events = selected_events.length;
          num_added = 0;
          added_members = 0;
          duplicate_members = 0;
          if (num_events > 0) {
            $.each(selected_events, function(event) {
              Bazaarboy.post('lists/add/event/', {
                id: listId,
                event: $(this).data('id')
              }, function(response) {
                added_members += response.added;
                duplicate_members += response.duplicates;
                num_added++;
                if (response.status === 'OK') {
                  if (num_added === num_events) {
                    $('div.event-add-interface div.event-add-controls div.error-message').html('Members: <span style="font-weight:bold;"> ' + added_members + '</span> Added -  <span style="font-weight:bold;">' + duplicate_members + '</span> Duplicates. Refreshing List, this may take a minute.....');
                    $('div.event-add-interface div.event-add-controls a').hide();
                    setTimeout(function() {
                      return location.reload();
                    }, 2500);
                  }
                } else {
                  alert(response.message);
                  $(this).removeClass('disabled-btn');
                  $(this).html('Confirm');
                  scope.submitting = false;
                }
              });
            });
          } else {
            alert('Must Select At Least 1 Event!');
            $(this).removeClass('disabled-btn');
            $(this).html('Confirm');
            scope.submitting = false;
          }
        }
      });
      $('div#list-management div.member-add-interface a.upload-csv-btn').click(function() {
        $('div#list-management form.upload_csv input[name=csv_file]').click();
      });
      $('div.csv_upload_interface a.cancel-csv-upload').click(function() {
        $('div.csv_upload_interface').addClass('hide');
        $('div.csv_upload_interface div.upload_row:not(.template)').remove();
        $('div.csv_upload_interface div.upload-btn-container').removeClass('hide');
        $('div.csv_upload_interface div.csv-info-container').addClass('hide');
        $('div.csv_upload_interface div.upload_rows').addClass('hide');
        $('div.csv_upload_interface div.title_rows').addClass('hide');
        $('div.member-add-interface').addClass('hide');
        $('div.csv_upload_interface div.csv-controls').addClass('hide');
        $('a.cancel-add').css('display', 'none');
      });
      $('body').on('change', 'div.csv_upload_interface select[name=field]', function() {
        if ($(this).val() === 'none') {
          $(this).parents('div.upload_row').removeClass('active');
        } else {
          $(this).parents('div.upload_row').addClass('active');
        }
        $(this).parents('div.csv_upload_interface').find('select[name=field] option').attr('disabled', false);
        $(this).parents('div.csv_upload_interface').find('div.upload_row.active select[name=field] option:selected').each(function() {
          $(this).parents('div.csv_upload_interface').find('select[name=field] option[value=' + $(this).val() + ']').attr('disabled', true);
        });
      });
      $('body').on('click', 'div.csv_upload_interface div.csv-controls a.submit-csv-btn', function() {
        var button, csv, format, id;
        if (!scope.submitting) {
          scope.submitting = true;
          button = $(this);
          button.html('Adding...');
          button.addClass('disabled-btn');
          id = listId;
          csv = scope.uploads.csv.pk;
          format = {};
          $('div.csv_upload_interface div.upload_row.active select[name=field] option:selected').each(function() {
            return format[$(this).val()] = $(this).parents('div.upload_row').data('col');
          });
          if (!format.hasOwnProperty('email')) {
            $('div.csv_upload_interface div.csv-controls div.error-message').html('You Must Select an EMAIL Column');
            setTimeout(function() {
              return $('div.csv_upload_interface div.csv-controls div.error-message').html('&nbsp;');
            }, 5000);
            button.html('Submit');
            scope.submitting = false;
            button.removeClass('disabled-btn');
            return;
          }
          if (!format.hasOwnProperty('first_name')) {
            $('div.csv_upload_interface div.csv-controls div.error-message').html('You Must Select a FIRST_NAME Column');
            setTimeout(function() {
              return $('div.csv_upload_interface div.csv-controls div.error-message').html('&nbsp;');
            }, 5000);
            button.html('Submit');
            scope.submitting = false;
            button.removeClass('disabled-btn');
            return;
          }
          format = JSON.stringify(format);
          Bazaarboy.post('lists/add/csv/', {
            id: id,
            csv: csv,
            format: format
          }, function(response) {
            if (response.status === 'OK') {
              $('div.csv_upload_interface div.csv-controls div.error-message').html('Members: <span style="font-weight:bold;"> ' + response.added + '</span> Added -  <span style="font-weight:bold;">' + response.duplicates + '</span> Duplicates. Refreshing List, this may take a minute.....');
              $('div.csv_upload_interface div.csv-controls a').hide();
              setTimeout(function() {
                $("html, body").animate({
                  scrollTop: 0
                }, 1);
                return location.reload();
              }, 2500);
            } else {
              $('div.csv_upload_interface div.csv-controls div.error-message').html(response.message);
              setTimeout(function() {
                return $('div.csv_upload_interface div.csv-controls div.error-message').html('&nbsp;');
              }, 5000);
            }
            button.html('Submit');
            scope.submitting = false;
            button.removeClass('disabled-btn');
          });
        }
      });
      $('div#list-management form.upload_csv input[name=csv_file]').fileupload({
        url: rootUrl + 'file/csv/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var filename, response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            scope.uploads.csv = response.file;
            filename = response.filename;
            Bazaarboy.post('lists/csv/prepare/', {
              csv: response.file.pk
            }, function(response) {
              var final_results, i, j, new_row, num, result, results, results_columns, results_rows, _i, _j, _k, _l, _len, _ref, _ref1;
              if (response.status === 'OK') {
                $('div.csv_upload_interface div.csv-info-container div.csv-name').html(filename);
                $('div.csv_upload_interface div.upload-btn-container').addClass('hide');
                $('div.csv_upload_interface div.csv-info-container').removeClass('hide');
                $('div.csv_upload_interface div.upload_rows').removeClass('hide');
                $('div.csv_upload_interface div.title_rows').removeClass('hide');
                $('div.csv_upload_interface div.csv-controls').removeClass('hide');
                results = response.results;
                results_rows = Object.keys(results).length;
                if (results_rows > 0) {
                  final_results = [];
                  results_columns = results[0].length;
                  for (i = _i = 0, _ref = results_columns - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
                    final_results[i] = [];
                  }
                  for (i = _j = 0, _ref1 = results_columns - 1; 0 <= _ref1 ? _j <= _ref1 : _j >= _ref1; i = 0 <= _ref1 ? ++_j : --_j) {
                    for (j = _k = 0; _k <= 2; j = ++_k) {
                      final_results[i][j] = results[j][i];
                    }
                  }
                  for (num = _l = 0, _len = final_results.length; _l < _len; num = ++_l) {
                    result = final_results[num];
                    new_row = $("div.csv_upload_interface div.upload_row.template").clone();
                    new_row.attr('data-col', num);
                    new_row.find('div.col-1').html(result[0]);
                    new_row.find('div.col-2').html(result[1]);
                    new_row.find('div.col-3').html(result[2]);
                    new_row.removeClass('hide');
                    new_row.removeClass('template');
                    $("div.csv_upload_interface div.upload_rows").append(new_row);
                  }
                  $('div.csv_upload_interface').removeClass('hide');
                  $("html, body").animate({
                    scrollTop: $("div.csv_upload_interface").offset().top
                  }, 500);
                } else {
                  alert('There are no rows in this CSV!');
                }
              } else {
                alert(response.message);
              }
            });
          } else {
            alert(response.message);
          }
        }
      });
    }
  };

  Bazaarboy.list.list.init();

}).call(this);
