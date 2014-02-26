(function() {
  this.Bazaarboy.pricing = {
    fees: {
      bazaarboy: {
        service: .02,
        non_prof: .01,
        cc: .03,
        extra: .5,
        max: 10
      },
      eventbrite: {
        service: .025,
        non_prof: .02,
        cc: .03,
        extra: .99,
        max: 9.95
      },
      ticketleap: {
        service: .02,
        non_prof: .02,
        cc: .03,
        extra: 1,
        max: 10
      }
    },
    calculate_fee: function(amount, company) {
      var total;
      if ($('.fees_calculator input[name=nonprofit]').is(':checked')) {
        total = Math.min(company.max, (amount * company.non_prof) + company.extra) + (amount * company.cc);
      } else {
        total = Math.min(company.max, (amount * company.service) + company.extra) + (amount * company.cc);
      }
      return total;
    },
    print_fees: function() {
      var price, raw_price;
      raw_price = $(".fees_calculator input[name=ticket_price]").val();
      price = parseFloat(raw_price);
      if (!isNaN(price)) {
        $(".calculator_price.bazaarboy").html('&nbsp;-&nbsp;$' + this.calculate_fee(price, this.fees.bazaarboy).toFixed(2));
        $(".calculator_price.eventbrite").html('&nbsp;-&nbsp;$' + this.calculate_fee(price, this.fees.eventbrite).toFixed(2));
        $(".calculator_price.ticketleap").html('&nbsp;-&nbsp;$' + this.calculate_fee(price, this.fees.ticketleap).toFixed(2));
      } else {
        $(".calculator_price.bazaarboy").html('&nbsp;-&nbsp;$0');
        $(".calculator_price.eventbrite").html('&nbsp;-&nbsp;$0');
        $(".calculator_price.ticketleap").html('&nbsp;-&nbsp;$0');
      }
    },
    adjust_plus_sign: function() {
      var full_height, plus_height, plus_top;
      full_height = $("#fees .box.service").height();
      plus_height = $("#fees .plus img").height();
      plus_top = (full_height * .6) - (plus_height / 2);
      $("#fees .plus img").css("top", plus_top + "px");
    },
    init: function() {
      var _this = this;
      this.adjust_plus_sign();
      $(window).resize(function() {
        return _this.adjust_plus_sign();
      });
      $(".fees_calculator input[name=ticket_price]").keyup(function() {
        return _this.print_fees();
      });
      $(".fees_calculator input[name=nonprofit]").click(function() {
        return _this.print_fees();
      });
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
