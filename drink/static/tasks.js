/* TODO:
 replace click: pop-ups editable description
 hover: edit + delete
*/
function editEvent(eventId) {
    window.location.href = eventId+"/";
    return true;
}
function deleteEvent(eventId) {
    $.ajax({
            url:'rm?name='+encodeURI(eventId),
    }).success(function() {
              $('#calendar').fullCalendar('removeEvents', eventId);
    });
}

function add_item_hook(item) {
    $('#calendar').fullCalendar('renderEvent',
        {'title': item.title, 'url': item.id+'/', 'start': new Date() }
    );
}
$(document).ready(function() {

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,today,next',
            center: 'title',
            right: 'month,agendaWeek,agendaDay' // replace agenda with basic to get simpler output
        },
        defaultView: "agendaWeek",
        editable: true,
        height: 700,
        minTime: 6,
        maxTime: 23,
        events: "events",
        /*
        eventClick: function (ev, jsE, view) {
            $('<div title="'+ev.title+'">'+ev.description+'</div>').appendTo('body').dialog();
            return false;
        },
        */
        // TODO: popup edit & remove functions
        eventMouseover: function(calEvent, domEvent) {
	        var layer =	"<div class='events-layer' class='fc-transparent' style='position:absolute; width:100%; height:100%; top:-1px; text-align:right; z-index:100'><a><img class='minicon' src='/static/actions/delete.png' onClick='deleteEvent(\""+calEvent.id+"\");'></a>  <a><img class='minicon' src='/static/actions/edit.png' onClick='editEvent(\""+calEvent.id+"\");'></a></div>";
//	        layer.fadeIn('slow');
	        $(this).append(layer);
	        return false;
	},
	eventMouseout: function(calEvent, domEvent) {
	    $(".events-layer").fadeOut('slow', function() {$(this).remove();});
},
	/*
        eventMouseover:
         function (ev, jsE, view) { },
        eventMouseout: function (ev, jsE, view) { },
       */
        eventRender: function(ev, elt) {
            elt.attr('title', ev.description);
        },
        eventResize: function( event, dayDelta, minuteDelta, revertFunc, jsEvent, ui, view ) {
        /*
            var text = ''+dayDelta+' Days, '+minuteDelta+' min.';
            $('<div>'+text+'</div>').appendTo('body').dialog();
            console.log(event);
*/
            form = {
                '_dk_fields': 'duration',
                'duration': (event.end.getTime()-event.start.getTime())/3600.0/1000,
            }
            $.post(event.id+"/edit", form);

        },
        eventDrop: function( event, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, ui, view ) {
        /*
            var text = ''+dayDelta+' Days (all day: '+allDay+'), '+minuteDelta+' min.';
            $('<div>'+text+'</div>').appendTo('body').dialog();
*/
            form = {'_dk_fields': 'all_day/date/start_time'}

            if (allDay) { form.all_day = 1 }

            form.date = event.start.getDate()+'/'+(1+event.start.getMonth())+'/'+event.start.getFullYear();

            form.start_time = event.start.getHours()+':'+event.start.getMinutes()

            $.post(event.id+"/edit", form);
        },
    });
});
