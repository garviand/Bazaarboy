Bazaarboy.designs.review =
	init: () ->
		$('a.submit-btn').click () ->
			reviews = {}
			emptyReview = false
			$('textarea[name=owner_notes]').each () ->
				if $(this).val().trim() is ''
					swal
						title: "Wait"
						text: "One of the submissions has no comments. Still want to submit?"
						type: "warning"
						showCancelButton: true
						confirmButtonText: "Yes, submit review!"
				reviews[$(this).data('id')] = $(this).val()
				return
			if not emptyReview
				Bazaarboy.post 'designs/review/submit/', {reviews:JSON.stringify(reviews)}, (response) ->
					if response.status is 'OK'
						swal
							title: "Success!"
							text: "Your comments have been submitted."
							type: "success"
							, ->
								window.location.href = '/designs'
								return
					else
						swal
							title: "Error"
							text: response.message
							type: "error"
					return
			return
		return

Bazaarboy.designs.review.init()