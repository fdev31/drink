$(document).ready(function() {

    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        editable: true,
        events: "events",
        eventDrop: function(event, delta) {
            alert(event.title + ' was moved ' + delta + ' days\n' +
                '(should probably update your database)');
        },

    });
});
