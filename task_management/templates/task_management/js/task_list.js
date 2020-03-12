// リストの追加・編集・削除のAjax通信
// リストの追加・編集・削除用モーダルを開いたときに属性を編集する
// リストを並び替えた時のAjax通信



$(function() {
  // リスト追加時のajax通信
  $('form#add-list-form').submit(function(event) {
    event.preventDefault();
    let form = $(this);
    $.ajax({
      url: form.prop('action'),
      method: form.prop('method'),
      data: form.serialize(),
      timeout: 10000,
      dataType: 'json',
    })
    .done(function(data) {
      // モーダルを閉じる
      $('body').removeClass('modal-open');
      $('.modal-backdrop').remove();
      $('#add-list-modal').modal('hide');

      // リスト一覧とフォームを直す
      $("ul#lists").append(data['list_item']);
      $("form#add-list-form").html(data['list_form']);
    })
  })

  // マウスホバーしたリストに編集・削除ボタンを表示する
  $('#lists').on({
    'mouseenter': function() {
      $(this).find('span.list-edit-buttons').addClass('active');
    },
    'mouseleave': function() {
      $(this).find('span.list-edit-buttons').removeClass('active');
    }
  }, 'li.list');

  // リストの編集ボタンを押すと、モーダルのaction、inputの初期値が合わせて変化する
  $('#lists').on('click', '.edit-list-button', function() {
    let pk = $(this).parents('.list').data('list-id');
    let url = $('#edit-list-form').prop('action').replace(/77777/, pk);
    let value = $(this).parents('.list').find('.list-name').text()
    $('#edit-list-form').attr('action', url)
    $('#edit-list-form input#edit_list_for_name').val(value)
  });

  // リスト編集時のajax通信
  $('form#edit-list-form').submit(function(event) {
    event.preventDefault();
    let form = $(this);
    $.ajax({
      url: form.prop('action'),
      method: form.prop('method'),
      data: form.serialize(),
      timeout: 10000,
      dataType: 'json',
    })
    .done(function(data) {
      // モーダルを閉じる
      $('body').removeClass('modal-open');
      $('.modal-backdrop').remove();
      $('#edit-list-modal').modal('hide');

      // リストの名前を変える
      let name = data.name
      let pk = data.pk;
      $(`li.list[data-list-id='${pk}']`).find('.list-name').text(name).hide().fadeIn();
    });
  })

  // リストの削除ボタンを押すと、モーダルのaction、inputの初期値が合わせて変化する
  $('#lists').on('click', '.remove-list-button', function() {
    let pk = $(this).parents('.list').data('list-id');
    let url = $('#remove-list-form').prop('action').replace(/77777/, pk);
    let value = $(this).parents('.list').find('.list-name').text();

    $('#remove-list-form').attr('action', url);
    $('#remove-list-modal').find('.remove-list-name').text(value);
  });

  // リスト削除のajax通信
  $('#remove-list-form').submit(function(event) {
    event.preventDefault();
    let form = $(this)
    $.ajax({
      url: form.prop('action'),
      method: form.prop('method'),
      data: form.serialize(),
      timeout: 10000,
      dataType: 'text',
    })
    .done(function(pk) {
      // モーダルを閉じる
      $('body').removeClass('modal-open');
      $('.modal-backdrop').remove();
      $('#remove-list-modal').modal('hide');

      // リストを削除する
      $(`#lists .list[data-list-id="${pk}"]`).animate(
        {'opacity':'0'},
        function() {
          $(this).slideUp();
        }
      );
    })
  })
  
  // リストのソート
  $('#lists').sortable({
    axis: 'y',
    cursor: 'grabbing',
    update: updateListSort,
  });
})
let updateListSort = function(e, ui) {
  let li = ui.item;
  let pk = li.data('list-id');
  let sort_number = $('ul#lists li.list').index(li);
  let csrf_token = getCookie("csrftoken");
  $.ajax({
    url: '',
    method: 'POST',
    data: { 'pk':pk, 'sort_number': sort_number, 'csrfmiddlewaretoken': csrf_token},
    timeout: 10000,
    dataType: 'text',
  })
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
