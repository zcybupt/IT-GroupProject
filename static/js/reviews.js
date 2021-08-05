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
        console.log(data);
      } else {
        if (data["msg"] === "login required") {
          window.location = "/rango/login";
        }
      }
    }
  })
}
