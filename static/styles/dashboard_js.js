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
  });
