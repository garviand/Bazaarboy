Bazaarboy.designs.create =
    createProject: (user_email, services, description, assets, register) ->
        Bazaarboy.post 'designs/project/create/', {services:services, description:description, assets:assets}, (response) ->
            if loggedIn
                StripeCheckout.open
                    key: response.publishable_key
                    address: false
                    amount: response.price
                    currency: 'usd'
                    name: 'Bazaarboy Designs'
                    panelLabel: 'Checkout'
                    email: user_email
                    image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png'
                    token: (token) =>
                        Bazaarboy.post 'designs/project/charge/', 
                            checkout: response.project.checkout
                            stripe_token: token.id
                        , (response) =>
                            console.log response
                            if response.status is 'OK'
                                swal
                                    title: "Congrats!"
                                    text: "Your Design Project has Started. Check your dashboard for updates from your designer. You will also recieve email updates when new submissions are sent from the artist."
                                    type: "success"
                                    , ->
                                        window.location.href = '/designs'
                                        return
                            else
                                alert response.message
                            return
                        return
            else
                if register
                    window.location.href = '/register/?next=designs&code=' + response.project.code
                else
                    window.location.href = '/login/?next=designs&code=' + response.project.code
            return
        return
    init: () ->
        scope = this
        # SELECT SERVICES
        $("div.services a.service-option").click () ->
            $(this).toggleClass('active')
            total = 0
            $("div.services a.service-option.active").each () ->
                total += parseInt($(this).data('price'))
            if total > 0
                $("div.payment div.cost").html '$' + total
            else
                $("div.payment span.cost").html ''
            return
        # CHECKOUT
        $("div.payment a.payment-btn").click () ->
            user_email = $(this).data('email')
            nextPage = $(this).data('next')
            if $("div.services a.service-option.active").length is 0
                swal("", "You must select at least one service", "error")
            else if $("div.description textarea[name=description]").val().trim() is ''
                swal("", "You must write a description of your project", "error")
            else
                if $("form#new-project input[name=assets]").val().trim() is ''
                    swal
                        title: "No Assets Attached"
                        text: "Are you sure you want to continue without attaching any images for the designer?"
                        type: "warning"
                        showCancelButton: true
                        confirmButtonText: "Yes"
                        closeOnConfirm: true
                        , ->
                            description = $("div.description textarea[name=description]").val()
                            services = ''
                            assets = $("form#new-project input[name=assets]").val()
                            $("div.services a.service-option.active").each () ->
                                if services is ''
                                    services += $(this).data('id')
                                else
                                    services += ', ' + $(this).data('id')
                                if nextPage == 'register'
                                    scope.createProject(user_email, services, description, assets, true)
                                else
                                    scope.createProject(user_email, services, description, assets, false)
                else
                    description = $("div.description textarea[name=description]").val()
                    services = ''
                    assets = $("form#new-project input[name=assets]").val()
                    $("div.services a.service-option.active").each () ->
                        if services is ''
                            services += $(this).data('id')
                        else
                            services += ', ' + $(this).data('id')
                    if nextPage == 'register'
                        scope.createProject(user_email, services, description, assets, true)
                    else
                        scope.createProject(user_email, services, description, assets, false)
            return
        # IMAGE UPLOADING with DROPZONE PLUGIN
        $("div.dropzone").dropzone({
            url: "/designs/asset/upload/"
            paramName: "image_file"
            init: () ->
                this.on 'success', (file) ->
                    image = $.parseJSON(file.xhr.response)
                    image_id = image.image.pk
                    if $("form#new-project input[name=assets]").val().trim() is ''
                        $("form#new-project input[name=assets]").val(image_id)
                    else
                        oldVal = $("form#new-project input[name=assets]").val()
                        $("form#new-project input[name=assets]").val(oldVal + ', ' + image_id)
                    return
                return
                this.on 'error', (file) ->
                    swal("Error", "The file could not be uploaded", "error")
                    return
                return
        })
        return

Bazaarboy.designs.create.init()