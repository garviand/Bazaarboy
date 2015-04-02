(function() {
  Bazaarboy.list.index = {
    init: function() {
      var scope;
      scope = this;
      $("a.show-archived-signups").click(function() {
        $("div.archived-button-container").hide();
        return $("div.archived_sign_up").removeClass('hide');
      });
      $("a.delete-signup.btn").click(function() {
        var list, signupId;
        list = $(this).closest("div.list");
        signupId = $(this).data("id");
        return swal({
          title: "Are You Sure?",
          text: "Are you sure you want to archive this signup? You can still view it by clicking the 'View Archived Signups' button.",
          type: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes, DeArchivelete",
          closeOnConfirm: true
        }, function() {
          return Bazaarboy.post('lists/signup/delete/', {
            id: signupId
          }, function(response) {
            if (response.status === 'OK') {
              list.remove();
            } else {
              swal(response.message);
            }
          });
        });
      });
      $("a.delete-list-btn").click(function() {
        var list, listId;
        list = $(this).closest("div.list");
        listId = $(this).data("id");
        return swal({
          title: "Are You Sure?",
          text: "Are you sure you want to delete this list?",
          type: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes, Delete",
          closeOnConfirm: true
        }, function() {
          return Bazaarboy.post('lists/delete/', {
            id: listId
          }, function(response) {
            if (response.status === 'OK') {
              list.remove();
            } else {
              swal(response.message);
            }
          });
        });
      });
      $(".new-list-btn").click(function() {
        $("div#new-list-modal").foundation('reveal', 'open');
      });
      $("a.close-list-modal").click(function() {
        $("div#new-list-modal").foundation('reveal', 'close');
      });
      $("div#new-list-modal div.new-list-inputs a.create-list").click(function() {
        var list_name;
        $(this).html('Creating...');
        list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val();
        if (list_name.trim() !== '') {
          Bazaarboy.post('lists/create/', {
            profile: profileId,
            name: list_name,
            is_hidden: 1
          }, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('lists/' + response.list.pk);
            }
          });
        } else {
          swal('List name can\'t be empty');
        }
      });
    }
  };

  Bazaarboy.list.index.init();

}).call(this);
