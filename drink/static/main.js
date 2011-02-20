
jQuery.validator.addMethod("identifier", function(value, element) {
    return this.optional(element) || !/^[.$%/][$%/]*/i.test(value);
}, 'No "$", "%" or "/" and don\' start with a dot, please :)');

$(document).ready(function(){
    // debug mode
    //$.validator.setDefaults({debug: true});

    $(".autovalidate").each(function(index, ob) { $(ob).validate() } );

    $("#selected_edit_key").change(function() {
        var action = $(this).val();
        $("#edit_form").attr("action", action+"/edit");
    });

    $('.editable span').click( function() {
        var o = $(this).prev();
        o.attr('checked', ! o.is(':checked'));
    });

    $('#rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item');
            $(this).removeClass("selected");
            $.ajax({
                url:'rm?name='+item,
            });
			ui.draggable.hide();
			// FIXME: does not work ?! only replaces one value...
			var safe_name = item.replace('"', '\\"');
			$('#edit_form select option[value="'+safe_name+'"]').remove();
			$('#rm_form select option[value="'+safe_name+'"]').remove();
        },
        over: function(event, ui) {
            $(this).addClass('selected');
        },
		out: function(event, ui) {
		    $(this).removeClass("selected");
		}
    });

    $('#edit_form').droppable({
        drop: function(event, ui) {
            $(this).removeClass("selected");
    		$($(this)[0][0]).val(ui.draggable.data('item'));
            $(this).attr("action", ui.draggable.data('item')+"/edit");
			$(this).submit();
        },
        over: function(event, ui) {
            $(this).addClass('selected');
        },
		out: function(event, ui) {
		    $(this).removeClass("selected");
		}
    });

    $('.editable span').addClass('toggler');
});