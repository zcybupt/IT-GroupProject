$(document).ready(function () {
  Array.from($('.review .more .text-wrap')).forEach(ele => {
    if (ele.offsetHeight >= 200) {
      $(ele).addClass('maxHeight');
    } else {
      $(ele).children('.util').hide();
    }
  })

  $('.unfold').on('click', e => {
    e.preventDefault();
    $(e.target).parents('.text-wrap').removeClass('maxHeight').end().hide().siblings().show();
  })

  $('.put').on('click', e => {
    e.preventDefault();
    $(e.target).parents('.text-wrap').addClass('maxHeight').end().hide().siblings().show();
  })
})

function like(reviewId) {
    let likeEle = $('#' + reviewId);
    let likedReviews = localStorage.getItem("likedReviews");

    if (likedReviews && likedReviews.indexOf(reviewId) > -1) {return;}

    $.ajax({
      url: '/rango/reviews/like/',
      type: 'post',
      headers: {
        "X-CSRFToken": getCookie('csrftoken'),
        "Content-Type": 'application/json',
      },
      data: JSON.stringify({'review_id': reviewId}),
      dataType: "json",
      success: function (data) {
        if (data["success"]) {
          likeEle.html(data["likes"]);
          likedReviews = likedReviews + "," + reviewId;
          localStorage.setItem("likedReviews", likedReviews);
        }
      }
  })
}

function postComment(movieId) {
  let titleBox = $(".title-box");
  if (!titleBox.val()) {
    alert("Please enter your title!");
    return;
  }

  let textBox = $(".text-box");
  if (!textBox.val()) {
    alert("Please enter your review!");
    return;
  }

  let rating = $('input[name=rating]:checked').attr("id");
  if (!rating) {
    alert("Please rate this movie!");
    return;
  }

  $.ajax({
    url: "/rango/movies/" + movieId + "/review",
    type: 'post',
    headers: {
      "X-CSRFToken": getCookie('csrftoken'),
      "Content-Type": 'application/json',
    },
    data: JSON.stringify({
      "title": titleBox.val(),
      "content": textBox.val(),
      "rating": rating
    }),
    dataType: "json",
    success: function (data) {
      if (data["success"]) {
        let newComment = '<div class="review-item">'
        +  '<div class="d-flex">'
        +    '<div class="short-content pl-4">'
        +      '<h5>'
        +        '<i class="fa fa-user"></i>'
        +        '<span>' + data["username"] + '</span>'
        +        '<span class="ml-3 cr1">&nbsp' + data["rating"] + '</span>'
        +        '<span class="ml-3 time">' + data["review_time"] + '</span>'
        +      '<h5>'
        +      '<h4 class="cr1">' + titleBox.val() + '</h4>'
        +      '<div class="more">'
        +        '<div class="text-wrap">'
        +          '<div class="text">' + textBox.val() + '<div>'
        +        '<div>'
        +        '<div class="response">'
        +          '<a class="fabulous" href="javascript:void(0)">'
        +            '<i class="fa fa-thumbs-o-up" style="font-family: FontAwesome;"></i>'
        +            '<span id="' + data["review_id"] + '" onClick="like(' + data["review_id"] + ')">0</span>'
        +          '<a>'
        +        '<div>'
        +      '<div>'
        +    '<div>'
        +  '<div>'
        +'<div>'

        $(newComment).prependTo('.review');
      } else {
        if (data["msg"] === "login required") {
          window.location = "/rango/login";
        }
      }
    }
  })
}
