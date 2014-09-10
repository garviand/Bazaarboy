(function() {
  Bazaarboy.list.index = {
    init: function() {
      var scope;
      scope = this;
      $("a.new-list-btn").click(function() {
        $("div#new-list-modal").foundation('reveal', 'open');
      });
      $("a.close-list-modal").click(function() {
        $("div#new-list-modal").foundation('reveal', 'close');
      });
      $("div#new-list-modal div.controls a.create-list").click(function() {
        var list_name;
        list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val();
        if (list_name.trim() !== '') {
          Bazaarboy.post('list/create/', {
            profile: profileId,
            name: list_name,
            is_hidden: 1
          }, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('list/' + response.list.pk);
            }
          });
        } else {
          alert('List name can\'t be empty');
        }
      });
    }
  };

  Bazaarboy.list.index.init();

}).call(this);