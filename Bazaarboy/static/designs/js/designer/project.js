(function() {
  Bazaarboy.designs.designer.project = {
    init: function() {
      $("div.actions-container div.services a.service-btn").click(function() {
        $("div.actions-container div.services a.service-btn").removeClass('active');
        $(this).addClass('active');
      });
      $("div.actions-container a.add-submission-btn").click(function() {
        var assets, notes, projectId, service;
        projectId = $(this).data('id');
        if ($("form#designer-project input[name=assets]").val().trim() === '') {
          swal("Wait!", "You must attach at least one asset", "warning");
        } else if ($("div.actions-container div.services a.service-btn.active").length === 0) {
          swal("Wait!", "You must select the type of submission", "warning");
        } else {
          notes = $('textarea[name=designer_notes]').val();
        }
        service = $("div.actions-container div.services a.service-btn.active").data('id');
        assets = $("form#designer-project input[name=assets]").val();
        Bazaarboy.post('designs/designer/submit/' + projectId, {
          service: service,
          assets: assets,
          notes: notes
        }, function(response) {
          if (response.status === 'OK') {
            return swal({
              title: "Success",
              text: "The submission has gone through!",
              type: "success"
            }, function() {
              location.reload();
            });
          } else {
            return swal("Error", response.message, "error");
          }
        });
      });
      $("div.dropzone").dropzone({
        url: "/designs/asset/upload/",
        paramName: "image_file",
        init: function() {
          this.on('success', function(file) {
            var image, image_id, oldVal;
            image = $.parseJSON(file.xhr.response);
            image_id = image.image.pk;
            if ($("form#designer-project input[name=assets]").val().trim() === '') {
              $("form#designer-project input[name=assets]").val(image_id);
            } else {
              oldVal = $("form#designer-project input[name=assets]").val();
              $("form#designer-project input[name=assets]").val(oldVal + ', ' + image_id);
            }
          });
          return;
          this.on('error', function(file) {
            swal("Error", "The file could not be uploaded", "error");
          });
        }
      });
    }
  };

  Bazaarboy.designs.designer.project.init();

}).call(this);
