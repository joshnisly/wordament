
$('#StartProcessBtn').bind('click', function(event)
{
    var statusHandle = doAjaxWithStatus({
        url: startUrl,
        data: {
            'should_fail': $('#ShouldFailCheck')[0].checked
        },
        statusElem: $('#ProcessStatus')
    });

    function cancelProcess()
    {
        statusHandle.cancel();
    }
    $('#CancelProcessBtn').bind('click', cancelProcess);
});

$('.StartDynamicProcessBtn').bind('click', function(event)
{
    var url = $(event.target).attr('url')
    console.log(url)
    var statusHandle = doAjaxWithStatus({
        url: url,
        data: {
            'should_fail': false
        },
        statusElem: $('#ProcessStatus'),
        exclusivity_error: function(sErrMsg){
            window.console.log('Caught it. Error: ' + sErrMsg)
        }
    });

    function cancelProcess()
    {
        statusHandle.cancel();
    }
    $('#CancelProcessBtn').bind('click', cancelProcess);
});



