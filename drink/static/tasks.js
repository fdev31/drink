function add_item_hook(item) {
    $('#calendar').fullCalendar('renderEvent',
        {'title': item.title, 'url': item.id+'/', 'start': new Date() }
    );
}
$(document).ready(function() {

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        defaultView: "agendaWeek",
        editable: true,
        events: "events",
        eventDrop: function(event, delta) {
            alert(event.title + ' was moved ' + delta + ' days\n' +
                '(should probably update your database)');
        },

    });
});
