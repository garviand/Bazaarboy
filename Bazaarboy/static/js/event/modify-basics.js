(function() {
  Bazaarboy.event.modify.basics = {
    init: function() {
      var originalEndTime, originalStartTime;
      originalStartTime = $("form.event-modify input[name=start_time]").val();
      originalEndTime = $("form.event-modify input[name=end_time]").val();
      $("form.event-modify input[name=start_time], form.event-modify input[name=end_time]").timeAutocomplete({
        blur_empty_populate: false
      });
      $("form.event-modify input[name=start_time]").val(originalStartTime);
      $("form.event-modify input[name=end_time]").val(originalEndTime);
      $('form.event-modify input[name=start_date]').pikaday({
        format: 'MM/DD/YYYY',
        onSelect: function() {
          $('form.event-modify input[name=end_date]').pikaday('gotoDate', this.getDate());
          $('form.event-modify input[name=end_date]').pikaday('setMinDate', this.getDate());
        }
      });
      $('form.event-modify input[name=end_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
    }
  };

  Bazaarboy.event.modify.basics.init();

}).call(this);
