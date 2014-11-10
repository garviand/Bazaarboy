(function() {
  Bazaarboy.designs.review = {
    init: function() {
      $('a.submit-btn').click(function() {
        var emptyReview, reviews;
        reviews = {};
        emptyReview = false;
        $('textarea[name=owner_notes]').each(function() {
          if ($(this).val().trim() === '') {
            swal({
              title: "Wait",
              text: "One of the submissions has no comments. Still want to submit?",
              type: "warning",
              showCancelButton: true,
              confirmButtonText: "Yes, submit review!"
            });
          }
          reviews[$(this).data('id')] = $(this).val();
        });
        if (!emptyReview) {
          Bazaarboy.post('designs/review/submit/', {
            reviews: JSON.stringify(reviews)
          }, function(response) {
            if (response.status === 'OK') {
              swal({
                title: "Success!",
                text: "Your comments have been submitted.",
                type: "success"
              }, function() {
                window.location.href = '/designs';
              });
            } else {
              swal({
                title: "Error",
                text: response.message,
                type: "error"
              });
            }
          });
        }
      });
      $('a.finalize-btn').click(function() {
        var projectId;
        projectId = $(this).data('id');
        Bazaarboy.post('designs/review/finalize/' + projectId + '/', {}, function(response) {
          if (response.status === 'OK') {
            return swal({
              title: "Success!",
              text: "Your project has been completed. You can download the final designs from your dashboard.",
              type: "success"
            }, function() {
              window.location.href = '/designs';
            });
          } else {
            return swal({
              title: "Error",
              text: response.message,
              type: "error"
            });
          }
        });
      });
    }
  };

  Bazaarboy.designs.review.init();

}).call(this);
