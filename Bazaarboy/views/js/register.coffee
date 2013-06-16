$(document).ready ->
    $("form[name=register]").submit (event) ->
        event.preventDefault()
        return false
    return