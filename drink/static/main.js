// globals

add_item_hooks = [];

jQuery.validator.addMethod("identifier", function(value, element) {
    return this.optional(element) || !/^[._$%/][$%/]*/i.test(value);
}, 'No "$", "%" or "/" and don\' start with a dot or an underscore, please :)');

function add_hook_add_item(hook) {
    add_item_hooks.push(hook);
}
function call_hook_add_item(data) {
   for(i=0; i<add_item_hooks.length; i++) {
        add_item_hooks[i](data);
   }
}
function add_new_item(obj) {
    if( ! $(obj).data('edited')) {
      $(this).data('edited', true);
      var all_opts = $('#new_obj_class').find('option');
      if ( all_opts.length == 2 ) {
        $('#new_obj_class').css('visibility', 'visible').show();
        $('#new_obj_class').val($(all_opts[1]).val());
        $('#new_obj_class').hide();
        $('#name_choice').css('visibility', 'visible').show();
        $('#new_obj_name').focus();
      } else {
        $('#new_obj_class').css('visibility', 'visible').show();
    }
  }
}

function item_added(data, status) {
    $('#new_obj_class').val('');
    $('#new_obj_name').val('');
    $('#add_object').data('edited', false);
    call_hook_add_item(data);
}

function validate_new_obj(e) {
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

function refresh_action_list(data) {
    var pa = $('#page_actions');
    var html = [];
    for (i=0;i<data.length;i++) {
        elt = data[i];
        if (typeof(elt) == "string") {
            var text=elt;
        } else {
            if (elt.href) {
              var text='<a title="'+elt.title+'" href="'+encodeURI(base_uri+elt.href)+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
            } else {
              var text='<a title="'+elt.title+'" onclick="'+elt.onclick+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
            };
        };
        html.push(text);
    }
    $('#page_actions').html(html.join(''));

    // add some hook for the new_obj_name validation
    $('#new_obj_name').keyup(validate_new_obj);

};

function get_matching_elts(path_elt, callback) {
    if (path_elt.match('/')) {
        var _elts = path_elt.split('/');
        _elts.filter(function(e) { if (!!e) return true; });
        for (n=0;n<_elts.length;n++) {
            if (n == _elts.length-1) {
                pattern = _elts[n];
            } else {
                url = _elts[n];
            }
        }
        url = url + "match?pattern=" + pattern;
    } else {
        pattern  = path_elt;
        url = document.location.pathname + "match?pattern=" + pattern;
    };
    // AJAX URL
    $.get(url).success(function(data) { callback(data.items) } );
}


$(document).ready(function(){
    base_uri = document.location.href.replace(/[^/]*$/, '');
    // add some features to jQuery

    $.extend({
        edit_entry: function(data) {
           frame = $('<iframe title="Edit object" src="'+base_uri+'/'+data+'/edit?embedded=1">No iframe support :(</iframe>');
            frame.dialog({modal:true, width:'90%'});
            frame.css('width', '100%');
            frame.css('padding', '0');
            frame.css('margin', 'auto');
            frame.css('height', '66%');
        },
        remove_entry: function(item) {
            $('<div id="remove-confirm" title="Do you really want to remove this item ?">Please, confirm removal.</div>').dialog({
                modal: true,
                buttons: {
                    Accept: function() {
                        $( this ).dialog( "close" );
                        $.ajax({
                            url:'rm?name='+encodeURI(item),
                        }).success(function() {
                            var safe_name = item.replace( /"/g, '\\"');
                            $('#edit_form select option[value="'+safe_name+'"]').remove();
                            $('#rm_form select option[value="'+safe_name+'"]').remove();
                            $('#rm_form select option[value="'+safe_name+'"]').remove();
                            $('ul > li.entry:data(item='+item+')').slideUp('slow', function() {$(this).remove()});
                            delete child_items[item];
                        }).error(function(){
                            $('<div title="Error occured">Sorry, something didn\'t work correctly</div>').dialog();
                           });
                    },
                    Cancel: function() {
                        $( this ).dialog( "close" );
                    }
                }
            });

        }
    });
    // debug mode
    //$.validator.setDefaults({debug: true});
    $(".autovalidate").each(function(index, ob) { $(ob).validate() } );

    $('#auto_edit_form').keypress( function(ev, elt) {
        if ( ev.ctrlKey && ev.charCode == 10 ) {
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
    // focus first entry
    $("input:text:visible:first").focus();
    // update actions list
    $.ajax({url:'actions'}).success(refresh_action_list)//.error(function() {  $('<div title="Error occured">Sorry, something didn\'t work correctly</div>').dialog();});
});
