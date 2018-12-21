$(document).ready(function(){
  var jsonified_data = [];
  var full_html = [];
  var seen = [];
  var data_attrs = ['privacy', 'calendar', 'basic'];
  var selected_dates = [];
  var selected_pannel = 'users';
  var users_and_groups = [];
  function previous_calendar(){
    data_attrs.push('calendar');
    $('.create_event_pannel').html(full_html.pop());
    var _ = jsonified_data.pop();
    for (var i = 0; i < selected_dates.length; i++){
      if (matching_months(selected_dates[i])){
        $('#'+selected_dates[i]).css('background-color', '#FF354D');
        $('#'+selected_dates[i]).css('color', 'white');
      }

    }

  }
  function previous_basic(){
    data_attrs.push('basic');
    $('.create_event_pannel').html(full_html.pop());
    var setup_data = jsonified_data.pop();
    var headers = ['name', 'description', 'location'];
    for (var i = 0; i < headers.length; i++){

      $('#event_'+headers[i]).val(setup_data[headers[i]]);
    }

  }
  var previous_functions = {'basic':previous_basic, 'calendar':previous_calendar};
  function basic_attrs(){

    if ($('#event_name').val() === ''){
      $('#for_name').text('cannot be left blank');
      data_attrs.push('basic');
    }
    else{

      var headers = ['name', 'description', 'location'];
      var data_row = {};
      for (var i = 0; i < headers.length; i++){
        data_row[headers[i]] = $('#event_'+headers[i]).val();
      }
      jsonified_data.push(data_row);
      full_html.push($('.create_event_pannel').html());
      seen.push('basic');
      $.ajax({
        url: "/render_event_creation_calendar",
        type: "get",
        data: {val: ""},
        success: function(response) {
          if (response.success === 'True'){

            $('.create_event_pannel').html(response.calendar);
            for (var i = 0; i < selected_dates.length; i++){
              if (matching_months(selected_dates[i])){
                $('#'+selected_dates[i]).css('background-color', '#FF354D');
                $('#'+selected_dates[i]).css('color', 'white');
              }

            }
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }
  }

  function calendar_attrs(){

    if (selected_dates.length === 0){
      $('.missing_dates').text('please select at least one day');
      data_attrs.push('calendar');
    }
    else{
      jsonified_data.push(selected_dates);
      full_html.push($('.create_event_pannel').html());
      seen.push('calendar');
      $.ajax({
        url: "/event_privacy_settings",
        type: "get",
        data: {val: ''},
        success: function(response) {
          if (response.success === 'True'){
            $('.create_event_pannel').html(response.html);
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }


  }
  var hashed_results = {"basic":basic_attrs, 'calendar':calendar_attrs};
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
  function is_selected(_the_id){
    for (var i = 0; i < selected_dates.length; i++){
      if (_the_id === selected_dates[i]){
        return true;
      }
    }
    return false;
  }
  function remove_selected(the_id){
    var new_container = [];
    for (var i = 0; i < selected_dates.length; i++){
      if (selected_dates[i] != the_id){
        new_container.push(selected_dates[i])
      }
    }
    return new_container;
  }
  function matching_months(datetime){
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var month_hashings = {};
    for (var i = 0; i < months.length; i++){
      month_hashings[(i+1).toString()] = months[i];
    }
    var split_month = datetime.split("-");
    return $('.calendar_month').text() === month_hashings[split_month[0]];
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
  $('.create_event_pannel').on('input', '#event_name', function(){
    $('#for_name').text('');
    var _remainder = 25-$('#event_name').val().length;

    if (_remainder < 10){

      var _prefix = 's';
      if (_remainder === 1){
        _prefix = '';
      }
      var text = `
      ${_remainder} character${_prefix} left
      `
      $('#for_name').text(text);
    }
    if (_remainder <= 0){
      $('#event_name').val($('#event_name').val().substring(0, 24));
    }
  });
  $('.create_event_pannel').on('input', '#event_description', function(){
    $('#for_description').text('');
    var _remainder = 50-$('#event_description').val().length;
    if (_remainder < 15){
      var _prefix = 's';
      if (_remainder === 1){
        _prefix = '';
      }
      var text = `
      ${_remainder} character${_prefix} left
      `
      $('#for_description').text(text);
    }
    if (_remainder <= 0){
      $('#event_description').val($('#event_description').val().substring(0, 49));
    }
  });
  $('.create_event_pannel').on('click', '.next_pannel', function(){

    var current = data_attrs.pop();

    hashed_results[current]();

  });
  $('.create_event_pannel').on('input', '#event_name', function(){
    $('#for_name').text('');
  });
  $('.tab_pannel').on('click', '.create_event', function(){

  });
  $('.create_event_pannel').on('click', '.today_day', function(){
    var the_id = this.id;
    if (is_selected(the_id)){
      $(this).css('background-color', 'white');
      $(this).css('color', 'black');
      selected_dates = remove_selected(the_id);

    }
    else{
      $(this).css('background-color', '#FF354D');
      $(this).css('color', 'white');
      selected_dates.push(the_id);
      $('.missing_dates').text('');
    }
  });
  $('.create_event_pannel').on('click', '.today', function(){
    var the_id = this.id;
    if (is_selected(the_id)){
      $(this).css('background-color', '#21DCAC');
      $(this).css('color', 'white');
      selected_dates = remove_selected(the_id);


    }
    else{
      $(this).css('background-color', '#FF354D');
      $(this).css('color', 'white');
      selected_dates.push(the_id);
      $('.missing_dates').text('');
    }
  });

  $(document).on({
    mouseenter: function () {
      if (!is_selected(this.id)){
        $(this).css('background-color', '#FF354D');
        $(this).css('color', 'white');
      }
    },
    mouseleave: function () {
      if (!is_selected(this.id)){
        $(this).css('background-color', 'white');
        $(this).css('color', 'black');
      }
    }
  }, '.today_day');
  $(document).on({
    mouseenter: function () {
      if (!is_selected(this.id)){
        $(this).css('background-color', '#FF354D');
        $(this).css('color', 'white');
      }
    },
    mouseleave: function () {
      if (!is_selected(this.id)){
        $(this).css('background-color', '#21DCAC');
        $(this).css('color', 'white');
      }
    }
  }, '.today');
  $('.create_event_pannel').on('click', '.month_nav', function(){
    var month = $('.calendar_month').text();
    var year = $('.calendar_year').text();
    var flag = 0;
    if (this.id === 'forward'){
      flag = 1;
    }
    $.ajax({
      url: "/update_calendar",
      type: "get",
      data: {nav: flag, month:month, year:year},
      success: function(response) {
        if (response.success === 'True'){
          $('.create_event_pannel').html(response.html);
          for (var i = 0; i < selected_dates.length; i++){
            if (matching_months(selected_dates[i])){
              $('#'+selected_dates[i]).css('background-color', '#FF354D');
              $('#'+selected_dates[i]).css('color', 'white');
            }

          }
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
  });
  $('.create_event_pannel').on('click', '.previous_pannel', function(){
    previous_functions[seen.pop()]();
  });
  $('.create_event_pannel').on('click', '.privacy_setting', function(){
    if (this.id === 'make_public'){
      var the_html = `
      <p class='create-event-header' style='font-size:30px;text-align:center;'><span style='color:#FABC09'><strong>${jsonified_data[0]["name"]}</strong></span> created!</p>
      <div style='height:20px;'></div>
      <div class='green_check'><i class="fas fa-check" style='font-size:4em;line-height:100px'></i></div>
      <div style='height:40px;'></div>
      
      <div class='container' style='margin-left:60px;'>
        <div class='row'>
          <div class='col-md-auto'>
          <p class='create-event-header' style='font-size:23px;margin-top:5px;text-align:center;'>Link: </p>
          </div>
          <div class='col-md-auto'>
            <input class='detail_input' id='final_event_link' value='http://chronos.com/events/1'>
          </div>
        </div>
      </div>
      `
      $('.create_event_pannel').html(the_html);
      $("#final_event_link").select();
      $("#final_event_link").prop("readonly", true)
      //$('.create_event_pannel').css('text-align', 'center');
      /*
      setTimeout(function(){
        window.location.replace('/dashboard')
      }, 700);
      */
    }
    else{
      $.ajax({
        url: "/select_users_groups",
        type: "get",
        data: {val: ''},
        success: function(response) {
          if (response.success === 'True'){
            $('.create_event_pannel').html(response.html);
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }
  });
  $('.create_event_pannel').on('click', '.user_select_pannel', function(){
    $('#underscore_'+selected_pannel).css('display', 'none');
    if (selected_pannel === 'users'){
      selected_pannel = 'groups';
      $('.add_people').css('display', 'none');
      $('.group_listing_text').html('<i>You have not created any groups</i>');
    }
    else{
      selected_pannel = 'users'
      $('.add_people').css('display', 'block');
      $('.group_listing_text').html('<i>No users added</i>');
    }
    $('.add_people').attr('placeholder', 'Filter '+selected_pannel+'....');
    $('#underscore_'+selected_pannel).css('display', 'block');
  });
  $('.create_event_pannel').on('input', '.add_people', function(){
    if ($(this).val() === ''){
      $('.found_user_results').css('display', 'none');
    }
    else{
      var current_displayed_users = [];
      $('.filtered_user_result').each(function(){
        current_displayed_users.push(parseInt($(this).prop('id').match('\\d+')));
      });
      $.ajax({
        url: "/filter_users",
        type: "get",
        data: {keyword: $(this).val(), users:JSON.stringify(current_displayed_users)},
        success: function(response) {
          if (response.success === 'True'){
            $('.found_user_results').css('display', 'block');
            $('.found_user_results').html(response.html);
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    }
  });
  $('.create_event_pannel').on('click', '.filter_username', function(){
    var the_id = this.id.match('\\d+');
    var username = $('#user_'+the_id).text();
    var initials = $('#user_styling_'+the_id).text();
    var background_color = $('#user_styling_'+the_id).css('background-color');
    $('#user_filter_row_'+the_id).remove();
    var the_html = `
    <div class='row filtered_user_result' id='user_row_${the_id}'>
      <div class='col-md-auto'>
        <div class="user_avatar">
            <div class="avatar" id='user_style_${the_id}' style='background-color:${background_color};'><p style='line-height:30px;'>${initials}</p></div>

        </div>
      </div>
      <div class='col-md-auto'><p class='dashboard_username filter_display_username' id='user_display_${the_id}' style='color:black;margin-left:-20px;'>${username}</p></div>

    </div>

    `;
    var count = 0;
    $('.filtered_user_result').each(function(){
      count += 1;
    });
    if (count > 0){
      $('.user_display_pannel').append(the_html);
    }
    else{
      $('.user_display_pannel').html('');
      $('.user_display_pannel').append('<div style="height:20px;"></div>');
      $('.user_display_pannel').append(the_html);
    }
    $('.create_private_finish').css('display', 'block');
    var new_count = 0;
    $('.filtered_server_results').each(function(){
      new_count += 1;
    });
    if (new_count === 0){
      $('.found_user_results').html('<i class="no_users_found">No users found</i>')
    }
  });
  $('.create_event_pannel').on('click', '.filter_display_username', function(){
    var the_id = this.id.match('\\d+');
    $('#user_row_'+the_id).remove();
    var check_count = 0;
    $('.filter_display_username').each(function(){
      check_count += 1;
    });
    if (check_count === 0){
      var the_html = `
      <p class="group_listing_text"><i>No users added</i></p>
      `;
      $('.user_display_pannel').html(the_html);
        $('.create_private_finish').css('display', 'none');
    }
  });
  $('.create_event_pannel').on('click', '.create_private_finish', function(){
    var selected_users = [];
    $('.filtered_user_result').each(function(){
      selected_users.push(parseInt($(this).prop('id').match('\\d+')));

    });
    jsonified_data.push(selected_users);
    alert(JSON.stringify(jsonified_data));
  });
});
