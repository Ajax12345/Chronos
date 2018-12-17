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
    $('.tab_pannel').on('click', '.create_event', function(){
      window.location.replace('/create');
    });
    $('.main_wrapper').on('click', '.more_event_details', function(){
      if ($(this).text() === 'details'){
        var _id = this.id.match('\\d+');
        var timerange = $('#event_timerange_for_'+_id).text();
        var timestamp = $('#event_timerange_for_'+_id).data('timestamp');
        $(this).html('<u>close</u>');
        $.ajax({
          url: "/event_display_details",
          type: "get",
          data: {payload: JSON.stringify({'timerange':timerange, '_timestamp':timestamp})},
          success: function(response) {
            $('#extra_info_'+_id).html(response.html);
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
      }
      else{
        $(this).html('<u>details</u>');
        var _id = this.id.match('\\d+');
        $('#extra_info_'+_id).html('');

      }
    });
    $('.main_wrapper').on('click', '._month_nav', function(){
      //user_personal_event_listings
      var _page_num = $(this).data('page');
      $.ajax({
        url: "/user_personal_event_listings",
        type: "get",
        data: {page: _page_num},
        success: function(response) {
          $(".main_wrapper").html(response.html);
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });
    $(document).on({
      mouseenter: function () {
        var timestamp = $(this).data('timestamp');
        var ref = $(this);
        $.ajax({
          url: "/render_mini_calendar",
          type: "get",
          data: {timestamp: timestamp},
          success: function(response) {
            console.log(response.html);
            ref.data('content', response.html);
            ref.popover();
            ref.popover('show');
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
        
      },
      mouseleave: function () {
          $(this).popover('hide');
      }
    }, ".personal_event_timestamp"); //pass the element as an argument to .on
    
  });
