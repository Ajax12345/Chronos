$(document).ready(function(){
    /*
    for (var i = 1; i < 8; i++){
      var av_height = Math.floor(parseInt($('#day_'+i.toString()).css('height').match('\\d+'))/24);
      var halved = av_height/2;
      for (var b = 1; b < 25; b++){
        var new_html = `
          <div class='hour_block' id='day_${i}_hour_${b}' style='height:${av_height}px'></div>
        `;
        $('#day_'+i.toString()).append(new_html);
      }
    }
    */
    $.ajax({
      url: "/dynamic_calendar_display",
      type: "get",
      data: {val: ''},
      success: function(response) {
        if (response.success === 'True'){
          $('.full_calendar').html(response.html);
          create_timestamp_strip();
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
    function create_timestamp_strip(){
      for (var i = 1; i < 25; i++){
        var formatted = i.toString()+':00 AM';
        if (i > 12){
          if (i === 24){
            formatted = '12:00 PM';
          }
          else{
            formatted = (i%12).toString()+':00 PM';
          }
        }
        var the_html = `
          <p class='timeslot_time'><strong>${formatted}</strong></p>
        `;
        $('.timeslots').append(the_html);
      }
    }

    function previous_spacing(day, id){
      var totals = 0;
      $('div[id^="'+day+'_"]').each(function(){
        if (parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5)) < parseInt(id)){
          var current_total = parseInt($(this).css('height').match('\\d+'));
          //console.log('running_height = '+current_total.toString());
          totals += Math.floor(current_total/45);
        }
      });
      return totals;
    }
    function close_to(val, _divisor, _range){
      var flag = false;
      for (var i = 0; i <= _range; i++){
        if ((val+i)%_divisor === 0){
          flag = true;
        }
      }
      return flag;
    }
    function condense_events(){
      $('.event_test_block').each(function(){
        var parent_height = parseInt($('#'+$(this).prop('id').substring(6)).css('height').match('\\d+'));
        var from_top = parseInt($(this).css('top').match('\\d+'));
        var height = parseInt($(this).css('height').match('\\d+'));
        var anchor_id = parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5));
        var previous_time = previous_spacing($(this).prop('id').match('day_\\d+'), parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5)));
        if (from_top >= 45){
          var full_id = this.id.match('day_\\d+_hour_\\d+');
          var day_id = full_id[0].match('day_\\d+');
          var current_id = parseInt(full_id[0].match('hour_\\d+')[0].substring(5))
          $(this).css('top', (from_top-45).toString()+'px');
          $(this).css('height', (parseInt($(this).css('height').match('\\d+'))-45).toString()+'px');
          $('div[id^="'+day_id+'+"]').each(function(){
            var original_id = $(this).prop('id')
            var incremented_id = parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5))+1;
            var new_id_here = day_id+"_hour_"+incremented_id.toString()
            $(this).prop('id', new_id_here);
            if ($(this).next().html() != ""){
              /*
              <div class="event_test_block" id='event_${this.id}' data-created="False">
                <button id='remove_event_${this.id}' class='remove_event'><i class="fas fa-times" style='color:white;font-size:1.3em'></i></button>
                <p class='event_title_display' id='title_display_${this.id}'></p>
                <p class='event_timestamp' id='timestamp_for_${this.id}'></p>
              </div>
              */
              $('#event_'+original_id).prop('id', 'event_'+new_id_here);
              $('#remove_event_'+original_id).prop('id', 'remove_event_'+new_id_here);
              $('#timestamp_for_'+original_id).prop('id', 'timestamp_for_'+new_id_here);
            }
          });
          var new_html = `
          <div class='hour_block' id='${full_id}' style='height:45px'>
            <div style='height:22.5px;border-bottom-style:dotted;border-bottom-width:1px;border-bottom-color:#B6B6B6'></div>
          </div>
          `
          var last_id = parseInt(full_id[0].match('hour_\\d+')[0].substring(5))- 1;
          var last_day = full_id[0].match('day_\\d+');
          $(new_html).insertAfter('#'+last_day+'_'+last_id.toString());
        }
      });
    }
    function update_timestamps(){
      $('.event_test_block').each(function(){
        var parent_height = parseInt($('#'+$(this).prop('id').substring(6)).css('height').match('\\d+'));
        var from_top = parseInt($(this).css('top').match('\\d+'));

        var height = parseInt($(this).css('height').match('\\d+'));
        var anchor_id = parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5));
        var previous_time = previous_spacing($(this).prop('id').match('day_\\d+'), parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5)));
        //console.log(previous_time);
        var hour1 = previous_time+1
        var new_height = ((hour1*45)+parent_height)
        var hour2 = Math.floor(new_height/45);
        var minutes1 = Math.floor((from_top/new_height)*(hour2*60));
        hour1 += Math.floor(minutes1/60);
        var minutes1 = minutes1%60;
        var meridian1 = 'AM';
        if (hour1 > 12){
          hour1 = hour1%12;
          meridian1 = 'PM';
        }
        var padding = '';
        if (minutes1 < 10){
          padding='0';
        }
        var minutes2 = Math.floor(((from_top+height)/new_height)*(hour2*60));
        var hour2 = Math.floor(minutes2/60)+hour1;
        var minutes2 = minutes2%60;
        if (minutes2 + 2 >= 60){
          hour2 += 1;
          minutes2 = 0;
        }
        var meridian2 = 'AM';
        if (meridian1 === 'PM'){
          meridian2 = 'PM';
        }
        if (hour2 > 12){
          if (hour2 === 24){
            hour2 = 12;
          }
          else{
            hour2 = hour2%12;
          }
          meridian2 = 'PM';
        }
        var padding2 = '';
        if (minutes2 < 10){
          padding2 = '0';
        }
        var generated = hour1.toString()+':'+padding+minutes1.toString()+ ' '+meridian1 + ' - ' + hour2.toString()+':'+padding2+minutes2.toString()+ ' '+meridian2;
        $('#timestamp_for_'+this.id.match('day_\\d+_hour_\\d+')).text(generated);
      });
      setTimeout(function(){
        update_timestamps();
      }, 40);
    }
    update_timestamps();
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

    var hashed_times = {};
    var all_times = []
    function event_exists(_id){
      var flag = false;
      $('.event_test_block').each(function(){
        if (this.id.match('day_\\d+_hour_\\d+') == _id){
          flag = true;
        }
      });
      return flag;
    }
    function convert_timestamp(a){
      var _lower_option = undefined;
      for (var i = 0; i < all_times.length; i++){
        if (hashed_times[all_times[i]] <= a && a <= hashed_times[all_times[i]]+44){
          _lower_option = all_times[i];
          break;
        }
      }
      if (a%45 != 0){
        var _top = a%45;
        var mins = Math.floor((_top*60)/45);
        if (mins < 10){
          mins = '0'+mins.toString();
        }
        else{
          mins = mins.toString();
        }
        var _start = _lower_option.match('^\\d+');
        var meridian = _lower_option.match('[A-Z]+$');
        var _lower_option = _start+':'+mins+' '+meridian;
      }
      return _lower_option;
    }
    function generate_timestamp(a, b){
      return convert_timestamp(a)+' - '+convert_timestamp(b);
    }
    function revert_time(a){
      var hour = parseInt(a.match('^\\d+'))-1;
      var minutes = parseInt(a.match(':\\d+')[0].substring(1));
      var meridian = a.match('[A-Z]+$');
      if (meridian[0] === 'PM'){
        hour += 12;
      }
      hour = hour*45;
      minutes = parseInt(60*(minutes/45));
      return hour + minutes;
    }
    $('.full_calendar').on('input', '#event_name', function(){
      $('#for_name').text('');
    });
    $('.calendar_options').on('click', '#calendar_settings', function(){
      $('#settings_underline').css('background-color', '#FABC09');
      $('#by_weekly_underline').css('background-color', '#21DCAC');
      $('#by_monthly_underline').css('background-color', '#21DCAC');
      $.ajax({
        url: "/calendar_settings",
        type: "get",
        data: {val: ''},
        success: function(response) {
          if (response.success === 'True'){
            $('.full_calendar').html(response.html);
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });
    $('.calendar_options').on('click', '#calendar_by_week', function(){
      $('#settings_underline').css('background-color', '#21DCAC');
      $('#by_weekly_underline').css('background-color', '#FABC09');
      $('#by_monthly_underline').css('background-color', '#21DCAC');

      $.ajax({
        url: "/dynamic_calendar_display",
        type: "get",
        data: {val: ''},
        success: function(response) {
          if (response.success === 'True'){
            $('.full_calendar').html(response.html);
            create_timestamp_strip();
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });
    $('.full_calendar').on('click', '.color_sample', function(){
      if (parseFloat($(this).css('opacity')) >= 1){
        var current_id = this.id;
        $(this).css('opacity', '0.3');
        $('.color_sample').each(function(){
          if ($(this).prop('id') != current_id){
            $(this).css('opacity', '1');
          }
        });
      }
      else{
        $(this).css('opacity', '1');
      }
    });
    $('.full_calendar').on('click', '.create_new_event_category', function(){
      var _name = $('#category_name').val();
      if (_name === ''){
        $('#for_color_input').text('cannot be left empty');
      }
      else{
        var color = undefined;
        var border_color = undefined;
        $('.color_sample').each(function(){
          if (parseFloat($(this).css('opacity')) < 1){
            color = $(this).css('background-color');
            border_color = $(this).css('border-color');
          }
        });
        $('#category_name').val();
        $.ajax({
          url: "/create_category",
          type: "get",
          data: {name: _name, color:color, border:border_color},
          success: function(response) {
            if (response.success === 'True'){
              $('#create_category_modal').modal('toggle');
              var the_html = `
              <div class='row'>
                  <div class='col-md-auto'>
                    <div class='pallete_sample' style='background-color:${color};border-color:${border_color};'></div>
                  </div>
                  <div class='col-md-auto'><p class='category_text'><strong>${_name}</strong></p></div>
                </div>
              `;
              $('.full_category_listing').append(the_html);
              var banner_html = `
              <div class='info_banner'>
                Category "${_name}" created!
              </div>
              `;
              $('.info_banner_wrapper').html(banner_html);
              setTimeout(function(){
                $(".info_banner").fadeOut(600);
              }, 2000);
              setTimeout(function(){
                $(".info_banner").remove();
              }, 8000);
            }
            else{
              $('#for_color_input').text('category already exists');
            }
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
      }
    });
    $('.full_calendar').on('input', '#category_name', function(){
      $('#for_color_input').text('');
    });
    $('.full_calendar').on('click', '.remove_info_banner', function(){
      $('.info_banner').remove();
    });

    function new_event_collection(day_id){
      var collections = [];
      var _last = [];
      var flag = true;
      $('div[id^="event_'+day_id+'"]').each(function(){
        var current_hour = parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5));
        //console.log(_last);
          if ($(this).data('created') === 'False'){
            if (_last.length === 0){
              _last.push($(this).prop('id'));
            }
            else{
              var last_hour = parseInt(_last[_last.length-1].match('hour_\\d+')[0].substring(5));
              if (current_hour - last_hour === 1){
                _last.push(this.id);
              }
              else{
                collections.push(_last);
                _last = [this.id];
              }
            }
          }
          else{
            collections.push(_last);
            _last = [];
          }
      });
      collections.push(_last);
      var final_result = [];
      for (var i = 0; i < collections.length; i++){
        if (collections[i].length > final_result.length){
          final_result = collections[i];
        }
      }
      return final_result;
    }
    function update_day_col(day_id, event_id){
      var grouping = new_event_collection(day_id);
      //console.log('grouping');
      //console.log(grouping);
      if (grouping.length > 0){
        var last_id = parseInt(grouping[grouping.length-1].match('hour_\\d+')[0].substring(5));
        //console.log(last_id);
        var current_hour = parseInt(event_id.match('hour_\\d+')[0].substring(5));
        //console.log(current_hour);
        if (current_hour-last_id === 1){
          //console.log('in here');
          grouping.push(event_id);
        }
        var new_height = 0;
        var start_id = parseInt(grouping[0].match('hour_\\d+')[0].substring(5));
        var last_id = parseInt(grouping[grouping.length-1].match('hour_\\d+')[0].substring(5));
        for (var i = 0; i < grouping.length; i++){
          new_height += parseInt($('#'+grouping[i].substring(6)).css('height').match('\\d+'));
          $('#'+grouping[i]).remove();
          $('#'+grouping[i].match('day_\\d+_hour_\\d+')[0]).remove();
        }
        //alert(new_height);
        var new_event_id = day_id+'_hour_'+start_id.toString();
        var new_html = `
          <div class='hour_block' id='${new_event_id}' style='height:${new_height}px'>
          <div class="event_test_block" id='event_${new_event_id}' data-created="False" style='height:${new_height}px'>
            <button id='remove_event_${new_event_id}' class='remove_event'><i class="fas fa-times" style='color:white;font-size:1.3em'></i></button>
            <p class='event_title_display' id='title_display_${new_event_id}'></p>
            <p class='event_timestamp' id='timestamp_for_${new_event_id}'></p>
          </div>
          </div>
        `;
        //console.log(new_html);
        if (start_id === 1){
          //console.log('inserting: '+"#"+day_id+'_hour_'+(last_id+1).toString());
          $(new_html).insertBefore("#"+day_id+'_hour_'+(last_id+1).toString());
        }
        else{
          //console.log('inserting: '+"#"+day_id+'_hour_'+(start_id-1).toString());
          $(new_html).insertAfter("#"+day_id+'_hour_'+(start_id-1).toString());
        }
        $('#event_'+new_event_id).resizable({handles:"s,n", minHeight:0, maxHeight:new_height-1});
        for (var i = last_id+1; i < 25; i++){
          var new_id1 = '#'+day_id+'_hour_'+i.toString();
          var new_id2 = day_id+'_hour_'+(i-grouping.length+1).toString();
          $(new_id1).attr('id', new_id2);
          /*
          <button id='remove_event_${this.id}' class='remove_event'><i class="fas fa-times" style='color:white;font-size:1.3em'></i></button>
          <p class='event_title_display' id='title_display_${this.id}'></p>
          <p class='event_timestamp' id='timestamp_for_${this.id}'></p>
          */
          $('#event_'+new_id1.substring(1)).attr('id', 'event_'+new_id2);
          $('#title_display_'+new_id1.substring(1)).attr('id', 'title_display_'+new_id2);
          $('#remove_event_'+new_id1.substring(1)).attr('id', 'remove_event_'+new_id2);
          $('#timestamp_for_'+new_id1.substring(1)).attr('id', 'timestamp_for_'+new_id2);
        }
      }
    }
    $('.full_calendar').on('click', '.hour_block', function(){
      if (!event_exists(this.id)){
        var new_html = `
        <div class="event_test_block" id='event_${this.id}' data-created="False">
          <button id='remove_event_${this.id}' class='remove_event'><i class="fas fa-times" style='color:white;font-size:1.3em'></i></button>
          <p class='event_title_display' id='title_display_${this.id}'></p>
          <p class='event_timestamp' id='timestamp_for_${this.id}'></p>
        </div>
        `;
        $(this).html(new_html);
        update_day_col(this.id.match('day_\\d+'), 'event_'+this.id);
        $('#event_'+this.id).resizable({handles:"s,n", minHeight:0, maxHeight:44});
      }
    });
    function max_day_val(day_id){
      var _max = 0;
      $('div[id^="'+day_id+'_"]').each(function(){
        if (!$(this).prop('id').includes('dummy')){
          var result = parseInt($(this).prop('id').match('hour_\\d+')[0].substring(5));
          if (result > _max){
            _max = result;
          }
        }
      });
      return _max;
    }
    $('.full_calendar').on('click', '.remove_event', function(ev){
      ev.stopPropagation();
      var parent_id = this.id.match('day_\\d+_hour_\\d+')[0];
      var month = $('.calendar_month').text();
      var year = $('.calendar_year').text();
      var week_range = $('.range_heading').text();
      var timerange = $('#timestamp_for_'+parent_id).text();
      $.ajax({
        url: "/delete_event",
        type: "get",
        data: {payload: JSON.stringify({'parent_id':parent_id, 'month':month, 'year':year, 'week_range':week_range, 'timerange':timerange})},
        success: function(response) {
          $(".full_calendar").html(response.html);
          create_timestamp_strip();
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });
    $('.full_calendar').on('click', '.event_test_block', function(ev){
      ev.stopPropagation();
      if ($(this).data('created') === 'False'){
        var parent_id = this.id.match('day_\\d+_hour_\\d+');
        $.ajax({
          url: "/render_categories",
          type: "get",
          data: {val: ''},
          success: function(response) {
            $('.category_options').html(response.html);
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
        $("#create_event_modal").modal('toggle');
        $('#selected_name').html("<strong style='color:gray'>default</strong>");
        $('.create_calendar_event_confirm').attr('id', 'modal_for_'+parent_id);
      }
      else{

        var parent_id = this.id.match('day_\\d+_hour_\\d+')[0];
        var current_month = $('.calendar_month').text();
        var week_range = $('.range_heading').text();
        var timerange = $('#timestamp_for_'+parent_id).text();
        var year = $('.calendar_year').text();
        var payload = {'parent_id':parent_id, 'month':current_month, 'year':year, 'week_range':week_range, 'timerange':timerange};
        $.ajax({
          url: "/event_quick_look",
          type: "get",
          data: {payload: JSON.stringify(payload)},
          success: function(response) {
            $('#display_quick_look').html(response.html);
            $('#display_quick_look').modal('toggle');
            //$("#place_for_suggestions").html(response);
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
      }
    });
    $('.full_calendar').on('click', '.create_calendar_event_confirm', function(){
      var parent_id = this.id.match('day_\\d+_hour_\\d+');
      var title = $('#event_name').val();
      var description = $('#event_description').val();
      var category = $('#selected_name').text();
      var category_color = $('#selected_square').css("background-color");
      var category_border_color = $('#selected_square').css("border-color");
      if (title === ''){
        $('#for_name').text('cannot be left blank');
      }
      else{
        $('#event_name').val('');
        $('#event_description').val('');
        $('#event_'+parent_id).css('background-color', category_color);
        $('#event_'+parent_id).css('border-color', category_border_color);
        $("#create_event_modal").modal('toggle');
        $('#selected_name').html("<strong style='color:gray'>default</strong>");
        $('#selected_square').css('background-color', 'red');
        //background-color:red;border-color:#FF354D
        $('#selected_square').css('border-color', '#FF354D');
        /*
        if (title.length > 8){
          title = title.substring(8)+'...';
        }
        */
        //console.log('down here');
        $('#title_display_'+parent_id).text(title);
        $('#event_'+parent_id).data('created', 'True');
        var current_month = $('.calendar_month').text();
        var week_range = $('.range_heading').text();
        var timerange = $('#timestamp_for_'+parent_id).text();
        var year = $('.calendar_year').text();
        var payload = {'title':title, 'description':description, 'category':category, 'background_color':category_color, 'border_color':category_border_color, 'month':current_month, 'week_range':week_range, 'timerange':timerange, 'year':year, 'parent_id':parent_id[0]}
        $.ajax({
          url: "/create_calendar_event",
          type: "get",
          data: {data: JSON.stringify(payload)},
          success: function(response) {
            $(".full_calendar").html(response.html);
            create_timestamp_strip();
          },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
        //$('#event_'+parent_id).removeClass('ui-resizable');
        //condense_events()
      }
    });
    $('.full_calendar').on('click', '.on_hover_style', function(){
      var main_id = this.id.match('\\d+');
      var current_selected_name = $('#selected_name').html();
      var current_color = $('#selected_square').css('background-color');
      var current_border_color = $('#selected_square').css('border-color');
      var this_selected_text = $(this).html();
      var this_selected_color = $('#categorycolor'+main_id).css('background-color');
      var this_selected_border_color = $('#categorycolor'+main_id).css('border-color');
      $('#selected_square').css('background-color', this_selected_color);
      $('#selected_square').css('border-color', this_selected_border_color);
      $('#selected_name').html(this_selected_text);
      $("#categorytext"+main_id).html(current_selected_name);
      $('#categorycolor'+main_id).css('background-color', current_color);
      $('#categorycolor'+main_id).css('border-color', current_border_color);
    });
    $('.full_calendar').on('click', '.month_nav', function(){
      var month = $(this).data('month');
      var year = $(this).data('year');
      var dayrange = $(this).data('dayrange');
      $.ajax({
        url: "/navigate_calendar_by_week",
        type: "get",
        data: {values: JSON.stringify({'month':month, 'year':year, 'dayrange':dayrange})},
        success: function(response) {
          if (response.success === 'True'){
            $('.full_calendar').html(response.html);
            create_timestamp_strip();
          }

        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });
    function update_by_month_events(_day){

      $.ajax({
        url: "/by_month_event_listing",
        type: "get",
        data: {payload: JSON.stringify({'month':$('._calendar_month').text(), 'year':$('._calendar_year').text(), 'day':_day})},
        success: function(response) {
          $('.day_event_snapshot').html(response.html);
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });

    }
    $('.calendar_options').on('click', '#calendar_by_month', function(){
      $('#settings_underline').css('background-color', '#21DCAC');
      $('#by_weekly_underline').css('background-color', '#21DCAC');
      $('#by_monthly_underline').css('background-color', '#FABC09');
      $.ajax({
        url: "/by_month_calendar",
        type: "get",
        data: {val: ''},
        success: function(response) {
          $(".full_calendar").html(response.html);
          update_by_month_events($('.today').text());
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });

    $('.full_calendar').on('click', '._month_nav', function(){
      var direction = 0;
      if (this.id === '_forward'){
        direction = 1;
      }
      var month = $('._calendar_month').text();
      var year = $('._calendar_year').text();
      $.ajax({
        url: "/update_by_month_calendar",
        type: "get",
        data: {vals: JSON.stringify({'month':month, 'nav':direction, 'year':year})},
        success: function(response) {
          var _html = '';
          if ($('.day_event_snapshot').html() != undefined){
            _html = $('.day_event_snapshot').html();
          }
          $(".full_calendar").html(response.html);
          if ($('.today').text() != ''){
            update_by_month_events($('.today').text());
          }
          else{
            if (_html != ''){
              $('.day_event_snapshot').html(_html);
            }
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    });

    function clear_extra_clicks(){
      $('.previous_day').each(function(){
        $(this).css('background-color', 'white');
        $(this).css('color', 'black');

      });
      $('.today_day').each(function(){
        $(this).css('background-color', 'white');
        $(this).css('color', 'black');

      });

    }

    $('.full_calendar').on('click', '.previous_day', function(){
      if ($(this).css('background-color') === 'rgb(255, 0, 0)'){
        $(this).css('background-color', 'white');
        $(this).css('color', 'black');
        if ($('.today').text() != ''){
          update_by_month_events($('.today').text());
        }
      }
      else{
        clear_extra_clicks();
        $(this).css('background-color', 'red');
        $(this).css('color', 'white');
        update_by_month_events($(this).text());
      }


    });
    $('.full_calendar').on('click', '.today_day', function(){
      if ($(this).css('background-color') === 'rgb(255, 0, 0)'){
        $(this).css('background-color', 'white');
        $(this).css('color', 'black');
        if ($('.today').text() != ''){
          update_by_month_events($('.today').text());
        }

      }
      else{
        clear_extra_clicks();
        $(this).css('background-color', 'red');
        $(this).css('color', 'white');
        update_by_month_events($(this).text());
      }
    });
    $('.full_calendar').on('click', '.expand_first_time_listing', function(){
      var main_timestamp = $('#_beautified_timestamp').text();
      var full_timerange = $('#start_time_for_'+this.id.match('\\d+')).data('timerange');
      $.ajax({
        url: "/update_pannel_event_listing",
        type: "get",
        data: {payload: JSON.stringify({'_timestamp':main_timestamp, 'timerange':full_timerange})},
        success: function(response) {
          if (response.success === 'True'){
            $('#display_quick_look').html(response.html);
            $('#display_quick_look').modal('toggle');
          }
          //$("#place_for_suggestions").html(response);
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });

    });
  });