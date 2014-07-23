(function() {
  Bazaarboy.list.list = {
    uploads: {
      csv: void 0
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
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
