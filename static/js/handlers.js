setInterval("my_function();", 5000);
function my_function() {
    $('#refresh1').load(location.href + ' #latest_div');
    $('#refresh2').load(location.href + ' #log_div');
    $('#data').load(location.href + ' #head-of-data');
}
$(function () {
    $('a#restart_btn').on('click', function (e) {
        e.preventDefault()
        $.getJSON('/restart_btn',
            function (data) {
                //do nothing
            });
        return false;
    });
});
$(function () {
    $('a#quit_btn').on('click', function (e) {
        e.preventDefault()
        $.getJSON('/quit_btn',
            function (data) {
                //do nothing
            });
        return false;
    });
});
$(function () {
    $('a#toggle_predicting_btn').on('click', function (e) {
        if (document.querySelector('#toggle_predicting_btn').innerHTML == '<button class="btn">Predicting</button>') {
            document.querySelector('#toggle_predicting_btn').innerHTML = '<button class="btn holding">Holding</button>';
        }
        else if (document.querySelector('#toggle_predicting_btn').innerHTML == '<button class="btn holding">Holding</button>') {
            document.querySelector('#toggle_predicting_btn').innerHTML = '<button class="btn">Predicting</button>';
        }

        console.log(document.querySelector('#toggle_predicting_btn').innerHTML);
        e.preventDefault()
        $.getJSON('/toggle_predicting_btn',
            function (data) {
                //do nothing
            });

        $('#feedback').load(location.href + ' #info');
        return false;

    });

});