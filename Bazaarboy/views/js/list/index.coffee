Bazaarboy.list =
    uploads:
        csv: undefined
    init: () ->
        scope = this
        $('div#list-management form.upload_csv input[name=csv_file]').fileupload
            url: rootUrl + 'file/csv/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    scope.uploads.csv = response.file
                    Bazaarboy.post 'list/csv/prepare/', {csv: response.file.pk}, (response) =>
                        if response.status is 'OK'
                            console.log response
                        else
                            alert response.message
                        return
                else
                    alert response.message
                return
        return

Bazaarboy.list.init()