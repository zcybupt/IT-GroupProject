$(document).ready(function () {
  $('.movie-grid').each(function (){
    let rating_ul = $(this).find(".rating");
    let stars = $(this).find("#movie-stars").val();
    for (let i = 0; i < stars; i++) {
      rating_ul.append("<li class=\"fas fa-star\"></li>");
    }
    for (let i = 0; i < 5 - stars; i++) {
      rating_ul.append("<li class=\"far fa-star\"></li>");
    }
  })
})