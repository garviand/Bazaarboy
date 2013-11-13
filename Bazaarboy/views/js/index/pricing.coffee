@Bazaarboy.pricing = 
    init: () ->
        $(".pricing_content .scrolling_input a").click () ->
            orgName = $(".pricing_content .scrolling_input input[name=name]").val()
            orgEmail = $(".pricing_content .scrolling_input input[name=email]").val()
            window.location.href = rootUrl + 'user/register?name=' + encodeURIComponent(orgName) + '&email=' + encodeURIComponent(orgEmail)
            return
        return

Bazaarboy.pricing.init()