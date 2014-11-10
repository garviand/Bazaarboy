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
		$('a.finalize-btn').click () ->
			projectId = $(this).data('id')
			Bazaarboy.post 'designs/review/finalize/'+projectId+'/', {}, (response) ->
				if response.status is 'OK'
					swal
						title: "Success!"
						text: "Your project has been completed. You can download the final designs from your dashboard."
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

Bazaarboy.designs.review.init()