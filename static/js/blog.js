



$("ul.tablist>li>a").hover(function(){
    $("strong").finish();
    $(this).children().effect("shake", { times:4,distance:4,direction:"up" }, 30);
}, function() {
    $("strong").finish();
});
$(".sideheadstyle>a").hover(function(){
    $(this).finish();
    $(this).effect("pulsate",{times:5});
}, function() {
    $(this).finish();
});


