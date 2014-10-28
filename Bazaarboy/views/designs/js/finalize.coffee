Bazaarboy.designs.finalize =
    init: () ->
        scope = this
        $("div.payment a.payment-btn").click () ->
            projectId = $(this).data('id')
            projectCode = $(this).data('code')
            userEmail = $(this).data('email')
            Bazaarboy.post 'designs/project/finalize/', {project:projectId, code:projectCode}, (response) ->
                if response.status is 'OK'
                    StripeCheckout.open
                        key: response.publishable_key
                        address: false
                        amount: response.price
                        currency: 'usd'
                        name: 'Bazaarboy Designs'
                        panelLabel: 'Checkout'
                        email: userEmail
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
                return
        return

Bazaarboy.designs.finalize.init()