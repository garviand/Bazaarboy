Bazaarboy.list.list =
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
                            results = response.results
                            results_rows = Object.keys(results).length
                            if results_rows > 0
                                final_results = []
                                results_columns = results[0].length
                                for i in [0..results_columns-1]
                                    final_results[i] = []
                                for i in [0..results_columns-1]
                                    for j in [0..2]
                                        final_results[i][j] = results[j][i]
                                for result, num in final_results
                                    new_row = $("div.csv_upload_interface div.upload_row.template").clone()
                                    new_row.attr 'data-col', num
                                    new_row.find('div.col-1').html result[0]
                                    new_row.find('div.col-2').html result[1]
                                    new_row.find('div.col-3').html result[2]
                                    new_row.removeClass 'hide'
                                    new_row.removeClass 'template'
                                    $("div.csv_upload_interface div.upload_rows").append(new_row)
                                $('div.csv_upload_interface').removeClass 'hide'
                            else
                                alert 'There are no rows in this CSV!'
                        else
                            alert response.message
                        return
                else
                    alert response.message
                return
        return

Bazaarboy.list.list.init()