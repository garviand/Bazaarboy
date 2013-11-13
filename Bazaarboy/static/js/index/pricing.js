(function() {
  this.Bazaarboy.pricing = {
    init: function() {
      $(".pricing_content .scrolling_input a").click(function() {
        var orgEmail, orgName;
        orgName = $(".pricing_content .scrolling_input input[name=name]").val();
        orgEmail = $(".pricing_content .scrolling_input input[name=email]").val();
        window.location.href = rootUrl + 'user/register?name=' + encodeURIComponent(orgName) + '&email=' + encodeURIComponent(orgEmail);
      });
    }
  };

  Bazaarboy.pricing.init();

}).call(this);
