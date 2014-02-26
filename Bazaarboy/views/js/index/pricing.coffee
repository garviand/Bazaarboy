@Bazaarboy.pricing =
    fees:
        bazaarboy:
            service: .02
            non_prof: .01
            cc: .03
            extra: .5
            max: 10
        eventbrite:
            service: .025
            non_prof: .02
            cc: .03
            extra: .99
            max: 9.95
        ticketleap:
            service: .02
            non_prof: .02
            cc: .03
            extra: 1
            max: 10
    calculate_fee: (amount, company) ->
        if $('.fees_calculator input[name=nonprofit]').is(':checked')
            total = Math.min(company.max, ((amount * company.non_prof) + company.extra)) + (amount * company.cc)
        else
            total = Math.min(company.max, ((amount * company.service) + company.extra)) + (amount * company.cc)
        return total
    print_fees: () ->
        raw_price = $(".fees_calculator input[name=ticket_price]").val()
        price = parseFloat(raw_price)
        if(!isNaN(price))
            $(".calculator_price.bazaarboy").html('&nbsp;-&nbsp;$'+@calculate_fee(price, @fees.bazaarboy).toFixed(2)+'<br />')
            $(".calculator_price.eventbrite").html('&nbsp;-&nbsp;$'+@calculate_fee(price, @fees.eventbrite).toFixed(2)+'<br />')
            $(".calculator_price.ticketleap").html('&nbsp;-&nbsp;$'+@calculate_fee(price, @fees.ticketleap).toFixed(2)+'<br />')
        else
            $(".calculator_price.bazaarboy").html('&nbsp;-&nbsp;$0<br />')
            $(".calculator_price.eventbrite").html('&nbsp;-&nbsp;$0<br />')
            $(".calculator_price.ticketleap").html('&nbsp;-&nbsp;$0<br />')
        return
    adjust_plus_sign: () ->
        full_height = $("#fees .box.service").height()
        plus_height = $("#fees .plus img").height()
        plus_top = ((full_height*.6) - (plus_height/2))
        $("#fees .plus img").css("top", plus_top+"px")
        return
    init: () ->
        @adjust_plus_sign()
        $(window).resize () =>
            @adjust_plus_sign()
        $(".fees_calculator input[name=ticket_price]").keyup () =>
            @print_fees()
        $(".fees_calculator input[name=nonprofit]").click () =>
            @print_fees()
        $(".pricing_content .scrolling_input a").click () ->
            orgName = $(".pricing_content .scrolling_input input[name=name]").val()
            orgEmail = $(".pricing_content .scrolling_input input[name=email]").val()
            window.location.href = rootUrl + 'user/register?name=' + encodeURIComponent(orgName) + '&email=' + encodeURIComponent(orgEmail)
            return
        return

Bazaarboy.pricing.init()