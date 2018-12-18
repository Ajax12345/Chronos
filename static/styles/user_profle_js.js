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
  
  $('.user_settings_examine_pannel').on('click', '.logout', function(){
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
  $(document).on({
    mouseenter: function () {
     
      $(this).popover();
      $(this).popover('show');
      
      
    },
    mouseleave: function () {
        $(this).popover('hide');
    }
  }, ".extra_information"); 
  //user_email_visibility
  $('.user_settings_examine_pannel').on('click', '.email_actions', function(){
    var _text = $(this).text();
    $.ajax({
      url: "/user_email_visibility",
      type: "get",
      data: {action: _text},
      success: function(response) {
        //pass
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
    $('#email_extra_information').popover();
    if (_text === 'Hide email'){
      $('#email_text_header').html('<strong>Email (hidden):</strong>');
      $('.email_actions').text('Show email');
      $('#main_email_stuff').html("<i class='fas fa-question-circle extra_information' id='email_extra_information' style='margin-top:10px;font-size:1.3em;color:#FABC09' data-toggle='popover' data-placement='right' data-content='<p>Your email is currently hidden from profile viewers.</p>' data-html='true'></i>")
      //$('#email_extra_information').data('content', '<p>Your email is currently hidden from profile viewers.</p>');

    }
    else{
      $('#email_text_header').html('<strong>Email (visible):</strong>');
      $('.email_actions').text('Hide email');
      $('#main_email_stuff').html("<i class='fas fa-question-circle extra_information' id='email_extra_information' style='margin-top:10px;font-size:1.3em;color:#FABC09' data-toggle='popover' data-placement='right' data-content='<p>Your email is currently visible on your profile.</p>' data-html='true'></i>")
      //$('#email_extra_information').data('content', '<p>Your email is currently visible on your profile.</p>');
    }
  });
  $('.user_settings_examine_pannel').on('click', '.view_more', function(){
    if ($(this).text() === 'More'){
      $(this).html("Close<i class='fas fa-times' style='margin-top:8px;margin-left:5px;'></i>")
      var the_html = `
        <div class='delete_account'>
          <div style='height:30px'></div>
          <button class='_delete_account'>Delete account</button>
          <div style='height:30px'></div>
          <p><small>This action cannot be undone.</small></p>
        </div>
      `;
      $('.view_more_results').html(the_html);
    }
    else{
      $(this).html("More<i class='fas fa-angle-down' style='margin-top:5px;margin-left:5px;'></i>");
      $('.view_more_results').html('');
    }
  });
  $('.user_settings_examine_pannel').on('input', '.detail_input', function(){
    var the_html = `
      <div class='container'>
        <div class='row'>
          <div class='col-md-auto'>
            <button class='cancel_changes'>Cancel</button>
          </div>
          <div class='col-md-auto'>
            <button class='update_changes'>Save changes</button>
          </div>

        </div>
      </div>
    `;
    $('.button_action_pannel').html(the_html);
  });
  $('.user_settings_examine_pannel').on('click', '.cancel_changes', function(){
    window.location.replace('/profile');
  });
  $('.user_settings_examine_pannel').on('click', '.update_changes', function(){
    var _name = $('#event_name').val();
    var _email = $('#event_email').val();
    if (_name === ''){
      $("#for_update_name").text('cannot be left blank');
    } 
    else if (_email === ''){
      $("#for_update_email").text('cannot be left blank');
    }
    else{
      $.ajax({
        url: "/update_profile",
        type: "get",
        data: {info: JSON.stringify({'name':_name, 'email':_email})},
        success: function(response) {
          $('.avatar').html(response.initials);
          $('.dashboard_username').html(response.name);
          $('.avatar_text').text(response.initials); //may not be needed
          $('.button_action_pannel').html('');
          $('.update_message_display').css('display', 'block');
          //$('.for_profile_update').css('display', 'none');
          setTimeout(function(){$(".update_message_display").fadeOut("slow");}, 1000);

          setTimeout(function(){$('.update_message_display').css('display', 'none');}, 3000);
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }
    
  });
  $('.user_settings_examine_pannel').on('click', '.profile_view', function(){
    window.location.replace('/profile/view');
  });
});
