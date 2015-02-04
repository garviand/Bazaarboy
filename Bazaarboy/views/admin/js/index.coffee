Bazaarboy.admin.login =
	sort_method: 'rsvps'
	searchProfiles: (value) ->
		Bazaarboy.get 'profile/search/', {keyword: value}, (response) ->
			if response.status is 'OK'
				profiles = response.profiles
				if profiles.length > 0
					console.log profiles
					return profiles
				else
					return []
			return
		return
	sort_li: (a, b) ->
		if Bazaarboy.admin.login.sort_method == 'date'
			return ($(b).data(Bazaarboy.admin.login.sort_method)) < ($(a).data(Bazaarboy.admin.login.sort_method)) ? 1 : -1
		else
			return ($(b).data(Bazaarboy.admin.login.sort_method)) > ($(a).data(Bazaarboy.admin.login.sort_method)) ? 1 : -1
	init: () ->
		scope = this
		console.log scope.sort_method
		# Sort Current Events
		$('.event-filters a.sort-btn').click () ->
			$('.event-filters a.sort-btn').removeClass('active')
			scope.sort_method = $(this).data('sort')
			$(this).addClass('active')
			$('.event-list .event').sort(scope.sort_li).appendTo('.event-list')
			return
		# Autocomplete For Profile Login Search
		$('div.login-profile input[name=profile_name]').autocomplete
			html: true,
		  source: (request, response) ->
		  	Bazaarboy.get 'profile/search/', {keyword: request.term}, (results) ->
		  		profiles = []
		  		for profile in results.profiles
		  			console.log profile
		  			thisLabel = '<div class="autocomplete_result row" data-id="' + profile.pk + '">'
		  			if profile.image_url?
		  				thisLabel += '<div class="small-1 columns autocomplete_image" style="background-image:url(' + profile.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />'
		  			thisLabel += '<div class="small-11 columns autocomplete_name">' + profile.name + '</div>'
		  			thisLabel += '</div>'
		  			profiles.push({label: thisLabel, value: profile.name})
		  		return response(profiles)
		  	return
		$('body').on 'click', '.autocomplete_result', (event) ->
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