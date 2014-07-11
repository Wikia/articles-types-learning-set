$(function(){
    $(window).resize(setSize);

    $('.watson-hover').hover(toggleHide, toggleHide);

    $('.watson-btn').click(function() {
        var that = this;
        var data = {
            "csrfmiddlewaretoken": $('.token input').val(),
            "type": $(this).text(),
            "metric": $(this).data('metric')
        };
        $.ajax({
            url: window.location.href,
            type: "POST",
            data: data
        }).success(function(e) {
            $parent = $('.watson-metric').has(that);
            $parent.find('.btn-success').removeClass('btn-success');
            if (e != 'None') {
                $(that).addClass('btn-success');
                $parent.find('.watson-cat').has(that).children('button').addClass('btn-success');
            }
        });
    });

    $('.watson-next').click(function() {
        $.ajax({
            url: "/next/"
        }).done(function(data){
            window.location.href = window.location.origin + data.path;
        });
    });

    $('.watson-sessions').click(function() {
        if(!$('.watson-sessions-dropdown ul').children().length) {
            $.ajax({
                url: "/sessions/"
            }).done(function(data){
                var $ul = $(document.createElement('ul'));
                $ul.addClass('dropdown-menu');
                for(item in data){
                    var $li = $(document.createElement('li'));
                    var $a = $(document.createElement('a'));
                    $a.click(data[item].name, changeSession);
                    $a.html(data[item].name);
                    $li.html($a);
                    $ul.append($li);
                }
                $('.watson-sessions-dropdown').append($ul);
            });
        }
    });

    function setSize() {
        var height = $(document).height() - $('.navbar').height();
        $('.watson-desktop').width($(document).width() - $('.watson-mobile').width());
        $('.watson-desktop').height(height);
        $('.watson-desktop').css('margin-top', $('.navbar').height());
        $('.watson-mobile').height(height);
        $('.watson-mobile').css('margin-top', $('.navbar').height());
    }

    function toggleHide(el) {
        $(el.currentTarget).children('span').toggleClass('hide');
    }

    function changeSession(e) {
        window.location.href = window.location.origin + '/watson/' + e.data;
    }

    setSize();
});
