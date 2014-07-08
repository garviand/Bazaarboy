(function() {
  Bazaarboy.list = {
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
              if (response.status === 'OK') {
                console.log(response);
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

  Bazaarboy.list.init();

}).call(this);
