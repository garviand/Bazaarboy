Bazaarboy.admin.login =
	searchProfiles: (value) ->
		Bazaarboy.get 'profile/search/', {keyword: value}, (response) ->
			if response.status is 'OK'
				profiles = response.profiles
				if profiles.length > 0
					return profiles
				else
					return []
			return
		return
	init: () ->
		scope = this
		# Sort Current Events
		$('.event-filters a.sort-btn').click () ->
			$('.event-filters a.sort-btn').removeClass('active')
			$(this).addClass('active')
			if $(this).data('sort') == 'date'
				tinysort('.event-list>.event',{data:$(this).data('sort'), order:'asc'})
			else
				tinysort('.event-list>.event',{data:$(this).data('sort'), order:'desc'})
			return
		# Autocomplete For Profile Login Search
		$('div.login-profile input[name=profile_name]').autocomplete
			html: true,
		  source: (request, response) ->
		  	Bazaarboy.get 'profile/search/', {keyword: request.term}, (results) ->
		  		profiles = []
		  		for profile in results.profiles
		  			thisLabel = '<div class="autocomplete_result row" data-id="' + profile.pk + '">'
		  			if profile.image_url?
		  				thisLabel += '<div class="small-1 columns autocomplete_image" style="background-image:url(' + profile.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />'
		  			thisLabel += '<div class="small-11 columns autocomplete_name">' + profile.name + '</div>'
		  			thisLabel += '</div>'
		  			profiles.push({label: thisLabel, value: profile.name})
		  		return response(profiles)
		  	return
		$('body').on 'click', '.autocomplete_result, .admin-login', (event) ->
			id = $(this).data('id')
			Bazaarboy.get 'admin/login/profile/', {id: id}, (response) ->
				if response.status is 'OK'
					Bazaarboy.redirect 'index'
				else
					alert response.message
				return
			return
		$('div.event_export .input_container input[name=event_name]').keyup (event) =>
			value = $('div.event_export .input_container input[name=event_name]').val()
			if value
				@searchEvents(value)
			else
				$('div.event_export .event_choices').empty()
			return
		return

Bazaarboy.admin.login.init()