/* TODO:
 replace click: pop-ups editable description
 hover: edit + delete
*/
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
        eventClick: function (ev, jsE, view) {
            if ( !! ev.description ) {
                $('<div>'+ev.description+'</div>').appendTo('body').dialog();
                return false;
            }
        },
        // TODO: popup edit & remove functions
        eventMouseover: function (ev, jsE, view) { },
        eventMouseout: function (ev, jsE, view) { },
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
