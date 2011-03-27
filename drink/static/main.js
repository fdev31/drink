
jQuery.validator.addMethod("identifier", function(value, element) {
    return this.optional(element) || !/^[.$%/][$%/]*/i.test(value);
}, 'No "$", "%" or "/" and don\' start with a dot, please :)');

function add_new_item(obj) {
    if( ! $(obj).data('edited')) {
      $(this).data('edited', true);
      var all_opts = $('#new_obj_class').find('option');
      if ( all_opts.length == 2 ) {
        $('#new_obj_class').css('visibility', 'visible').show();
        $('#new_obj_class').val($(all_opts[1]).val());
        $('#new_obj_class').hide();
        $('#name_choice').css('visibility', 'visible').show();
        $('#new_obj_name').focus()
      } else {
        $('#new_obj_class').css('visibility', 'visible').show();
    }
  }
}

$(document).ready(function(){
    // debug mode
    //$.validator.setDefaults({debug: true});

    $(".autovalidate").each(function(index, ob) { $(ob).validate() } );

    $('#auto_edit_form').keypress( function(ev, elt) {
        if ( ev.ctrlKey && ev.charCode == 10 ) {
            console.log(this);
            $(this).submit();
            return true;
        };
    });
    $("#selected_edit_key").change(function() {
        var action = $(this).val();
        $("#edit_form").attr("action", action+"/edit");
    });

    $('.editable span').click( function() {
        var o = $(this).prev();
        if ( ! o.is(':checked') ) {
            o.attr('checked', true);
            $(this).addClass('selected', 1000);
        } else {
            o.attr('checked', false);
            $(this).removeClass('selected', 1000);
        }
    });

    var item_added = function(data, status) {
        $('#new_obj_class').val('');
        $('#new_obj_name').val('');
        $('#add_object').data('edited', false);
        if ( !! add_item_hook ) {
            add_item_hook(data);
        }
    }

    var validate_new_obj = function(e) {
        if (e.keyCode == 27) {
            $('#name_choice').hide();
            $('#new_obj_class').val('');
            $('#new_obj_name').val('')
            $('#add_object').data('edited', false);
        } else if (e.keyCode == 13) {
            var item = {
                'class': $('#new_obj_class').val(),
                'name': $('#new_obj_name').val()
            };
            $('#name_choice').hide();
            $.post('add', item, item_added);
        }
    }

    $('#new_obj_name').keyup(validate_new_obj);

    $('#rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item');
            $(this).removeClass("selected");
			sortable.remove_entry(ui.draggable.remove());
			ui.draggable.remove();
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
    $('.auto_date').datepicker({dateFormat: "dd/mm/yy"});

});
