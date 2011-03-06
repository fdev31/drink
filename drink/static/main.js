
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
    var item_added = function(data, status) {
        if ( !! sortable ) {
            sortable.append(make_li(data));
        }
    }

    var validate_new_obj = function(e) {
        if (e.keyCode == 13) {
            $('#name_choice').hide();
            $.post('add', {'class': $('#new_obj_class').val(), 'name': $('#new_obj_name').val()}, item_added);
        }
    }

    $('#new_obj_name').keyup(validate_new_obj);

    $('#rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item').replace(/&/g, '%26').replace(/\?/g, '%3f');
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
    		$($(this)[0][0]).val(ui.draggable.data('item').replace(/&/g, '%26').replace(/\?/g, '%3f'));
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

//    $('#commands .togglable').slideUp(0);

});
