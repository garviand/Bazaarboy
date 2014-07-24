(function() {
  Bazaarboy.list.list = {
    uploads: {
      csv: void 0
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('div#list-management div.controls a.add-single-item').click(function() {
        $('div#add-item-modal').foundation('reveal', 'open');
      });
      $('a.add-item-close').click(function() {
        $('div#add-item-modal').foundation('reveal', 'close');
      });
      $('div#add-item-modal form.add-item-form').on('valid.fndtn.abide', function() {
        var params;
        $('div#add-item-modal div.submit-add-item a.add-item-submit').html('Adding...');
        params = $('div#add-item-modal form.add-item-form').serializeObject();
        params.id = listId;
        return Bazaarboy.post('list/add/item/', params, function(response) {
          var new_item;
          if (response.status === 'OK') {
            new_item = $('div#list-management div.list div.list-item.template').clone();
            new_item.find('div.name').html(response.item.first_name + " " + response.item.last_name);
            new_item.find('div.email').html(response.item.email);
            new_item.removeClass('template');
            new_item.removeClass('hide');
            $('div#list-management div.list .list-items').prepend(new_item);
            $('div#add-item-modal div.submit-add-item div.message').html('Added!');
            setTimeout(function() {
              return $('div#add-item-modal div.submit-add-item div.message').html('&nbsp;');
            }, 3000);
            $('div#add-item-modal div.submit-add-item a.add-item-submit').html('Add To List');
            $('div#add-item-modal form.add-item-form input').val('');
            $('div#add-item-modal form.add-item-form textarea').val('');
          } else {
            $('div#add-item-modal div.submit-add-item div.message').html(response.message);
            setTimeout(function() {
              return $('div#add-item-modal div.submit-add-item div.message').html('&nbsp;');
            }, 3000);
            $('div#add-item-modal div.submit-add-item a.add-item-submit').html('Add To List');
          }
        });
      });
      $('div#add-item-modal a.add-item-submit').click(function() {
        $('div#add-item-modal form.add-item-form').submit();
      });
      $('div#list-management div.controls a.add-from-event').click(function() {
        $('div#add-event-modal').foundation('reveal', 'open');
      });
      $('a.add-event-close').click(function() {
        $('div#add-event-modal').foundation('reveal', 'close');
      });
      $('div#add-event-modal form.add-event-form div.event-list').click(function() {
        $(this).toggleClass('selected');
      });
      $('div#add-event-modal form.add-event-form a.add-event-submit').click(function() {
        var num_added, num_events, selected_events;
        $('div#add-event-modal form.add-event-form a.add-event-submit').html('Adding...');
        selected_events = $('div#add-event-modal form.add-event-form div.row.event-list.selected');
        num_events = selected_events.length;
        num_added = 0;
        console.log(num_events);
        $.each(selected_events, function(event) {
          Bazaarboy.post('list/add/event/', {
            id: listId,
            event: $(this).data('id')
          }, function(response) {
            num_added++;
            if (response.status === 'OK') {
              if (num_added === num_events) {
                $('div#add-event-modal form.add-event-form').addClass('hide');
                $('div#add-event-modal div.add-event-success').removeClass('hide');
                setTimeout(function() {
                  return location.reload();
                }, 2500);
              }
            } else {
              alert(response.message);
              $('div#add-event-modal form.add-event-form a.add-event-submit').html('Add To List');
            }
          });
        });
      });
      $('div#list-management div.controls a.upload-csv-btn').click(function() {
        $('div#list-management form.upload_csv input[name=csv_file]').click();
      });
      $('div.csv_upload_interface div.csv-controls a.cancel-csv-btn').click(function() {
        $('div.csv_upload_interface').addClass('hide');
        $('div.csv_upload_interface div.upload_row:not(.template)').remove();
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
        button = $(this);
        button.html('Adding...');
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
          return;
        }
        if (!format.hasOwnProperty('first_name')) {
          $('div.csv_upload_interface div.csv-controls div.error-message').html('You Must Select a FIRST_NAME Column');
          setTimeout(function() {
            return $('div.csv_upload_interface div.csv-controls div.error-message').html('&nbsp;');
          }, 5000);
          button.html('Submit');
          return;
        }
        format = JSON.stringify(format);
        Bazaarboy.post('list/add/csv/', {
          id: id,
          csv: csv,
          format: format
        }, function(response) {
          if (response.status === 'OK') {
            $('div.csv_upload_interface div.csv-controls div.error-message').html('CSV Uploaded Succesfully. Refreshing List.....');
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
        });
      });
      $('div#list-management form.upload_csv input[name=csv_file]').fileupload({
        url: rootUrl + 'file/csv/upload/',
        type: 'POST',
        add: function(event, data) {
          data.submit();
        },
        done: function(event, data) {
          var response;
          response = jQuery.parseJSON(data.result);
          if (response.status === 'OK') {
            scope.uploads.csv = response.file;
            Bazaarboy.post('list/csv/prepare/', {
              csv: response.file.pk
            }, function(response) {
              var final_results, i, j, new_row, num, result, results, results_columns, results_rows, _i, _j, _k, _l, _len, _ref, _ref1;
              if (response.status === 'OK') {
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
