$(document).ready(function(){
  function display_warning(count){
    $('.event_upcomming_warning').fadeOut(500);
     $('.event_upcomming_warning').fadeIn(500);
     if (count < 10){
       setTimeout(function(){display_warning(count+1)}, 1000);
     }
  }
  //display_warning(0);
  function hours_min(_hours, _minutes){
    _meridian = 'AM';
    if (_hours > 12){
      _hours = (_hours%12).toString()
      _meridian = 'PM';
    }
    else{
      _hours = _hours.toString();
    }
    if (_minutes < 10){
      _minutes = '0'+_minutes.toString();
    }
    else{
      _minutes = _minutes.toString();
    }
    return _hours+':'+_minutes+' '+_meridian;
  }
  function update_datetime(){

    var _date = new Date();
    var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    $('.hour_min').text(hours_min(_date.getHours(), _date.getMinutes()));
    $('.day_of_week').text(days[_date.getDay()]);
    $('.day').text(_date.getDate());
    $('.month').text(months[_date.getMonth()]);
    $('.year').text(_date.getFullYear());
    setTimeout(function(){ update_datetime(); }, 1000);
  }
  update_datetime();
  $('.personal_info').on('input', '.detail_input', function(){
    $('.for_profile_update').css('display', 'block');
    var headers = ['name', 'email'];
    for (var i = 0; i < headers.length; i++){
      $('#for_update_'+headers[i]).text('');
    }
  });
  $('.for_profile_update').on('click', '.update_profile', function(){
    var headers = ['name', 'email'];
    var _result = {};
    var flag = true;
    for (var i = 0; i < headers.length; i++){
      var _temp = $('#event_'+headers[i]).val();
      if (_temp === ''){
        $('#for_update_'+headers[i]).text('cannot be left blank');
        flag = false
        break;
      }
      _result[headers[i]] = _temp;
    }
    if (flag){

      var full_structure = JSON.stringify(_result);

      $.ajax({
      url: "/update_profile",
      type: "get",
      data: {info: full_structure},
      success: function(response) {
        if (response.success === 'True'){
          $('.dashboard_username').text(response.name);
          $('.avatar').text(response.initials);
          $('.avatar_text').text(response.initials);
          $('.update_message_display').css('display', 'block');
          $('.for_profile_update').css('display', 'none');
          setTimeout(function(){$(".update_message_display").fadeOut("slow");}, 1000);

          setTimeout(function(){$('.update_message_display').css('display', 'none');}, 3000);
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
    }
  });
  $('.button_pannel').on('click', '#logout', function(){
    $.ajax({
      url: "/signout",
      type: "get",
      data: {val: ''},
      success: function(response) {
        if (response.success === 'True'){
          window.location.replace('/');
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
  })

});
