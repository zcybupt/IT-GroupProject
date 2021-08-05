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

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

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
        console.log(data);
        if (data["success"]) {
          likeEle.html(data["likes"]);
          likedReviews = likedReviews + "," + reviewId;
          localStorage.setItem("likedReviews", likedReviews);
        }
      }
  })
}

