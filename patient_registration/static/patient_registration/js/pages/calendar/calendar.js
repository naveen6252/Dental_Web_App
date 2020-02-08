$(function () {
    enableDrag();

    function enableDrag() {
        $('#external-events .fc-event').each(function () {
            $(this).data('event', {
                title: $.trim($(this).text()), // use the element's text as the event title
                stick: true // maintain when user navigates (see docs on the renderEvent method)
            });
            // make the event draggable using jQuery UI
            $(this).draggable({
                zIndex: 999,
                revert: true,      // will cause the event to go back to its
                revertDuration: 0  //  original position after the drag
            });
        });
    }

    /*$(".save-event").on('click', function () {
        var categoryName = $('#addNewEvent form').find("input[name='category-name']").val();
        var categoryColor = $('#addNewEvent form').find("select[name='category-color']").val();
        if (categoryName !== null && categoryName.length != 0) {
            $('#event-list').append('<div class="fc-event bg-' + categoryColor + '" data-class="bg-' + categoryColor + '">' + categoryName + '</div>');
            $('#addNewEvent form').find("input[name='category-name']").val("");
            $('#addNewEvent form').find("select[name='category-color']").val("");
            enableDrag();
        }
    });*/


    var calendar = $('#calendar');
    // Add direct event to calendar
    var newEvent = function (start) {
        let date = start.toDate();
        let day = date.getDate().toString();
        let month = (date.getMonth() + 1).toString();
        let year = date.getFullYear().toString();
        let hour = start.hours().toString()
        let minute = start.minutes().toString()
        let second = start.seconds().toString()
        if (month.length < 2)
            month = '0' + month;
        if (day.length < 2)
            day = '0' + day;
        if (hour.length < 2)
            hour = '0' + hour;
        if (minute.length < 2)
            minute = '0' + minute;
        if (second.length < 2)
            second = '0' + second;
        let date_string = year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + second;
        $('#addDirectEvent input[name="date"]').val(date_string);
        $('#addDirectEvent').modal('show');
    }

    // initialize the calendar
    calendar.fullCalendar({
        header: {
            left: 'title',
            center: '',
            right: 'month, agendaWeek, agendaDay, prev, next'
        },
        editable: true,
        droppable: true,
        eventLimit: true, // allow "more" link when too many events
        selectable: true,
        events: event_data,
        drop: function (date, jsEvent) {
            // var originalEventObject = $(this).data('eventObject');
            // var $categoryClass = $(this).attr('data-class');
            // var copiedEventObject = $.extend({}, originalEventObject);
            // //console.log(originalEventObject + '--' + $categoryClass + '---' + copiedEventObject);
            // copiedEventObject.start = date;
            // if ($categoryClass)
            //   copiedEventObject['className'] = [$categoryClass];
            // calendar.fullCalendar('renderEvent', copiedEventObject, true);
            // is the "remove after drop" checkbox checked?
            if ($('#drop-remove').is(':checked')) {
                // if so, remove the element from the "Draggable Events" list
                $(this).remove();
            }
        },
        select: function (start, end, allDay) {
            newEvent(start);
        },
        eventClick: function (calEvent, jsEvent, view) {
            var eventModal = $('#eventViewModal');
            eventModal.modal('show');
            eventModal.find('span[id="patient"]').html(calEvent.title);
            eventModal.find('span[id="time"]').html(calEvent.start._i);
            eventModal.find('span[id="note"]').html(calEvent.note);
            eventModal.find('.edit-btn').click(function () {
                window.location.href = '/appointment/' + calEvent.appointment_id + '/update/'
            });
            eventModal.find('.delete-btn').click(function () {
                window.location.href = '/appointment/' + calEvent.appointment_id + '/delete/'
            });
        }
    });
});