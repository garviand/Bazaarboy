Bazaarboy.designs.designer.project =
    init: () ->
    	$("div.actions-container div.services a.service-btn").click () ->
    		$("div.actions-container div.services a.service-btn").removeClass 'active'
    		$(this).addClass 'active'
    		return
    	$("div.actions-container a.add-submission-btn").click () ->
    		projectId = $(this).data('id')
    		if $("form#designer-project input[name=assets]").val().trim() is ''
    			swal("Wait!", "You must attach at least one asset", "warning")
    		else if $("div.actions-container div.services a.service-btn.active").length == 0
    			swal("Wait!", "You must select the type of submission", "warning")
    		else
    			service = $("div.actions-container div.services a.service-btn.active").data('id')
    			assets = $("form#designer-project input[name=assets]").val()
    			Bazaarboy.post 'designs/designer/submit/'+projectId, {service:service, assets:assets}, (response) ->
    				if response.status is 'OK'
    					swal
                            title: "Success"
                            text: "The submission has gone through!"
                            type: "success"
                            , ->
                                location.reload()
                                return
    				else
    					swal("Error", response.message, "error")
    		return
    	$("div.dropzone").dropzone({
            url: "/designs/asset/upload/"
            paramName: "image_file"
            init: () ->
                this.on 'success', (file) ->
                    image = $.parseJSON(file.xhr.response)
                    image_id = image.image.pk
                    if $("form#designer-project input[name=assets]").val().trim() is ''
                        $("form#designer-project input[name=assets]").val(image_id)
                    else
                        oldVal = $("form#designer-project input[name=assets]").val()
                        $("form#designer-project input[name=assets]").val(oldVal + ', ' + image_id)
                    return
                return
                this.on 'error', (file) ->
                    swal("Error", "The file could not be uploaded", "error")
                    return
                return
        })
        return

Bazaarboy.designs.designer.project.init()