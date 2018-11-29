$(document).ready(function(){
  $('.login').on('input', '.credential', function(){
    $('#for_'+this.id).text('');


  });
  $('.login').on('click', '.login_button', function(){
    var names = ['name', 'email', 'password', 'password_confirm'];
    var result = {};
    var flag = true;

    for (var i = 0; i < names.length; i++){
      var _val = $('#'+names[i]).val();
      if (_val === ''){
        flag = false;
        $('#for_'+names[i]).text('cannot be left blank');
        break;
      }
      else{
        result[names[i]] = _val;
      }
    }
    if (flag){
      if (result['password'] != result['password_confirm']){
        $('#for_password_confirm').text('passwords do not match');
      }
      else{
        var payload = JSON.stringify(result);
        $.ajax({
          url: "/register_user",
          type: "get",
          data: {info: payload},
          success: function(response) {
            if (response.success === 'True'){
              window.location.replace('/dashboard');
            }
            else{
              if (response.for === 'name'){
                $('#for_name').text('name already taken');
              }
              else{
                $('#for_email').text('email is already registered');
              }
            }
            
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
      }


    }
  });
});
