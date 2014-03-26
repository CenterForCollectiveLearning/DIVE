window.onload = function() {
    // variable for file
    var file;

    $('#data-file').on('change', function(event) {
        files = event.target.files;
    })

    $('#data-submit').click(function(event) {
        var data = new FormData();
        data.append('dataset', files[0])

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: data,
            cache: false,
            processData: false,
            contentType: false,
            success: function(data) {});}
        });
    })
};
