$(document).ready(function () {
    // Navbar muda de cor ao rolar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $(".navbar").addClass("scrolled");
        } else {
            $(".navbar").removeClass("scrolled");
        }
    });

    // Alternar conteúdos "Missão, Visão e Valores"
    $(".number").click(function () {
        let target = $(this).attr("data-target");

        $(".content-box").removeClass("active");
        $("#" + target).addClass("active");

        $(".number").removeClass("active");
        $(this).addClass("active");
    });
});
