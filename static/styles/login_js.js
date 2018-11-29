$(document).ready(function(){

  $('.login').on('input', '.credential', function(){
    $('#for_'+this.id).text('');


  });
  $('.login').on('click', '.login_button', function(){

    var username = $('#username').val();

    var password = $('#password').val();
    var flag = true;
    if (username === ''){

      $('#for_username').text('cannot be left blank');
      flag = false;
    }
    else if (password === ''){
      $('#for_password').text('cannot be left blank');
      flag = false;
    }
    else{

      $.ajax({
        url: "/login_user",
        type: "get",
        data: {info: JSON.stringify({'name':username, 'password':password})},
        success: function(response) {
          if (response.success === 'False'){
            $('#for_password').text('invalid email or password');
          }
          else{
            window.location.replace('/dashboard');
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }
  });
});
