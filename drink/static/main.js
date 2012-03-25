// globals
debug = false;
drink = false;

// UI Object
ui = new Object({
  draw_comments: function(comments) {
        if(!!!comments)
            comments = [];
        if(comments.length !== 0) {
            $('#comments').append('<div>Comments:</div>');
            for (i=0; i<comments.length; i++) {
                var e = $('<div><strong>'+comments[i].from+':</strong>&nbsp;'+comments[i].message+'</div>');
                e.hide();
                e.fadeIn()
                $('#comments').append(e);
            }
        }
        $('#comments').append('<form id="dk_comment"  action="#" method="post" />');
        var text = $('<textarea class="edited_comment">Your comment here...</textarea>');
        $('#comments #dk_comment').append(text);
        text.click(function(e) {
            var txt = $(e.target);
            txt.unbind();
            txt.parent().append($('<span class="button" onclick="ui.validate_comment()">Send!</span>'));
            txt.attr('value', '');
        });
  },
  validate_comment : function() {
        var e = $('#comments textarea');
        var txt = e.attr('value');
        $.post(base_path+'comment', {text: txt}).
            success(function(d) {
                ui.draw_comments(d.comments);
            });
        $('#comments').html('');
    },
  go_back: function() {
        if (document.location.pathname != base_path) {
            document.location.href = base_path;
        } else {
            document.location.href = base_path+'../';
        }
  },
  load_html_content: function(data) {
     for (var n=0; n<data.css.length; n++) {
        var tmp_css = data.css[n];
        if ( tmp_css[0] == '/') {
            tmp_css = '<link type="text/css" rel="stylesheet" href="'+tmp_css+'"></link>';
        } else {
            tmp_css = '<style type="text/css">'+tmp_css+'</style>';
        }
        $('head').append($(tmp_css));
        }
        for (var n=0; n<data.js.length; n++) {
            var tmp_js = data.js[n];
            if ( tmp_js[0] == '/') {
                tmp_js = '<script type="text/javascript" src="'+tmp_js+'"></script>';
            } else {
                tmp_js = '<script type="text/javascript" >'+tmp_js+'</script>';
            }
            $('head').append($(tmp_js));
        }
        $('#main_body').html(data.html);
        if(debug) console.log('load html content');
        dom_initialize($('#main_body'));
    },
    // ADD an entry Popup
    add_entry: function() {
    	var k = drink.d.classes;
         if ( k.length < 1 ) {
            w = $('<div title="Ooops!">Nothing can be added here, sorry</div>').dialog({closeOnEscape:true});
            setTimeout(function(){w.fadeOut(function(){w.dialog('close');});}, 2000);
            return;
        }
        var template = '<div id="new_obj_form"  title="New item informations"><select class="obj_class" class="required" name="class"><option value="" label="Select one item type">Select one item type</option>';
        var tpl_ftr = '</select><div class="obj_name"><label for="new_obj_name">Name</label><input id="new_obj_name" type="text" name="name" class="obj_name required identifier" minlength="2" /></div></div>';
        for (t=0; t<k.length; t++) {
            template += '<option value="{0}" label="{0}">{0}</option>'.replace(/\{0\}/g, k[t]);
        }
        var new_obj = $(template+tpl_ftr);
        var check_fn = function(e) {
            if (e.keyCode == 13) {
                validate_fn();
            }
        };
        var validate_fn = function() {
            new_obj.dialog("close");
            var item = {
                'class': new_obj.find('.obj_class').val(),
                'name': new_obj.find('input.obj_name').val()
            };
            $.post(base_path+'add', item).success(function(data) { if(validate(data)) {drink.add_item(data, true);} } );
        };

        new_obj.find('input.obj_name').keyup(check_fn);

        new_obj.dialog({
            closeOnEscape: true,
            modal: true,
            buttons: [ {text: 'OK', click: validate_fn} ]
        });

        if (k.length == 1) {
            new_obj.find(".obj_class").val(k[0]).attr('disabled', true);
            new_obj.find('input.obj_name').trigger('click').focus();
        }
    },
    edit: function(what) {
        ui.dialog('<div title="Edit"><iframe style="height: 100%" src="'+what+'edit?embedded=1"></iframe></div>');
    },
    ask_user: function(title, msg, callback) {
        return ui.dialog('<div title="'+title+'">'+msg+'<form id="drink_question" action="js: return false" onvalidate="return false;"><input type="text" id="drink_answer" name="question"></input></form></div>', {
            Ok: function() {
                $( this ).dialog( "close" ); 
                callback($(this).find('input').val());
            }
        });
    },
    success_dialog: function(title, msg) {
        return ui.dialog('<div title="'+title+'">'+msg+'</div>', {
            Ok: function() { $( this ).dialog( "close" ); }
        });
    },
    failure_dialog: function(title, msg) {
        return ui.dialog('<div title="'+title+'">'+msg+'</div>', {
            Ok: function() { $( this ).dialog( "close" ); }
        });
    },
    dialog: function(body, buttons, style) {
        var d = $(body);
        d.dialog({
            modal: true,
            closeOnEscape: true,
            buttons: buttons,
            width: '50%'
        });
        if (style == 'big') {
            d.css('width', '100%');
            d.css('padding', '0');
            d.css('margin', 'auto');
            d.css('height', '66%');
        }
        dom_initialize(d);
        return d;
    },
    load_action_list: function(actions) {

        if ( !!!actions  )  {
            $('#header_bar').slideUp();
            return;
        }
        var pa = $('#page_actions');
        var html = [];

        for (i=0 ; i<actions.length ; i++) {
            elt = actions[i];
            if (typeof(elt) == "string") {
                var text=elt;
            } else {
                // if condition validated & write operations allowed
                if (
                    (!elt.condition || eval(elt.condition) )  && (drink.d._perm.match('w') || drink.d._perm.match(elt.perm)) ) {
                    // if plain link
                    if (elt.action.match(/^[^\(\)\[\] ;]+$/)) {
                        if(!!elt.action.match(/\/$/)) {
                            var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                        } else {
                            var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+base_path+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                        }
                    } else { // javascript code
                      var text='<a class="action '+(elt.style || '')+'" title="'+elt.title+'" onclick="'+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                      if (elt.key)
                        keys.add(elt.key, elt.action);
                    }
                } else {
                    var text=null;
                }
            }
            if ( text ) { html.push(text); }
        }

        pa.html(html.join(''));
        dom_initialize( pa );

        if (actions.length === 0) {
            $('#header_bar').slideUp();
        } else {
            setTimeout(function(){ $('#header_bar').slideDown('slow'); }, 1000 );
        }
    },
    // Move
    move_current_page: function() {
        var win = ui.dialog('<div id="move-confirm" title="Do you really want to move this item ?">Please, type destination path:<input style="width: 90%" type="text" id="move-destination" class="completable" complete_type="objpath" value="/pages/"></input></div>', {
            Move: function() {
                $.post($('#move-confirm #move-destination').val()+'/borrow',
                    {'item': base_path},
                    function() {
                        document.location.href = $('#move-confirm #move-destination').val();
                }).error(function(){
                    ui.dialog('<div title="Error occured">Sorry, something didn\'t work correctly</div>');
               });
            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        });
    },
    focus: new Position(-1, [
        ['items', '#main_body .entry'],
        ['actions',  '#commands a.action']
    ], 'highlighted')
    }
);

// KEYPRESS THINGS
var KeyHandler = function(o, options) {
  /*
    keypress(function(ev, dom) {
    console.log(ev);
        if ((!!!mod['shift'] || ev.shiftKey) && (!!!mod['ctrl'] || ev.ctrlKey) && (!!!mod['alt'] || ev.metaKey) && ev.keyCode == kcode ) {
            func(ev, dom, elt);
        }
    });
    */

    this.add = function(key, code) {
        var kcode = this.k[key];
        if (kcode) {
            if (debug && this.hooks[kcode]) {
                alert('Duplicate handler for "'+key+'" key!');
            }
            this.hooks[kcode] = code;
        } else {
            alert("Unknown keycode: "+key);
        }
    };
    this.call = function(e, options) {
        var tag = e.target.tagName;
        var accept = !e.ctrlKey && !e.altKey && !e.shiftKey && tag != 'INPUT' && tag != 'TEXTAREA' && tag != 'SELECT';
        if (accept || me.options.forced.some(function(e) {return e == tag;}) ) {
           var code = me.hooks[e.which];
           if (!code) {
               code = me.hooks[String.fromCharCode(e.which)];
            }
           if (code) {
                try {
                    if (typeof(code) == 'string') {
                        eval(code);
                    } else {
                        code(e);
                    }
                } catch (x) {
                    if(debug) {console.log(code) ; console.log(x); }
                }
                if (debug) console.log('handled '+e.which);
                return false;
            } else {
                if (debug) console.log("Don't know how to handle", e, "with", options);
            }
        }
        return true;
    };
    var me = this;
    var apply_on = $(o || document);
    this.hooks = [];
    this.options = {'forced': []};
    if (options)
        $.extend(this.options, options);
    this.k = {
        BACK: 8,
        ENTER: 13,
        ESC: 27,
        UP: 38,
        LEFT: 37,
        RIGHT: 39,
        DOWN: 40,
        INS: 45,
        DEL: 46
    };

    for (i=65; i<=90; i++) {
        this.k[String.fromCharCode(i)] = i;
    }
    // Hook all keypresses in window
    $(document).bind('keyup', null, this.call);

    return this;
};

keys = new KeyHandler();

// REMOVE ITEM THINGS

remove_item_hooks = [];

function add_hook_remove_item(o) { remove_item_hooks.push(o); }

function call_hook_remove_item(o) {
   for(i=0; i<remove__hooks.length; i++) {
        remove_item_hooks[i](data);
   }
}

function dom_initialize(dom) {
    // hides some things by default
    dom.find('.starts_hidden').slideUp(0);

    // sumbit forms on Ctrl+Enter press
    dom.find('#auto_edit_form').keypress( function(ev, elt) {
        if ( ev.ctrlKey && ev.charCode == 10 ) {
            $(this).submit();
            return true;
        }
    });
    // autocomplete paths
    dom.find('input.completable[complete_type=objpath]').keyup(function(e) {
        if (debug) { console.log('match'); console.log(e); }
        var o = $(this);
        if (e.which == 13) {
            o.parent().parent().find('button:first').trigger('click');
        }
        if (e.which < 64 && e.which != 17 && e.which != 32 && e.which != 16) return;
        get_matching_elts(o.val(), function(items, path) {
                    o.parent().find('.completed').remove();
                    if (items.length > 1) {
                        var list = items.join('</li><li>');
                        $('<ul class="completed"><li>' + list + '</li></ul>').insertAfter(o);
                    } else {
                        if (items.length == 1 ) {
                            var best_match = items[0];
                            var components = path.split(RegExp('/'));
                            if ( components && components[components.length-1] !== '' ) {
                                components.pop();
                            }
                            components.push(best_match);
                            components.push('');
                            o.val(components.join('/'));
                        }
                    }
            }
        );
    });

    // change style of checkboxes titles in editable spans form
    dom.find('.editable span').click( function() {
        var o = $(this).prev();
        if ( ! o.is(':checked') ) {
            o.attr('checked', true);
            $(this).addClass('selected', 1000);
        } else {
            o.attr('checked', false);
            $(this).removeClass('selected', 1000);
        }
    });

    // drop edit form's droppable, FIXME: is this code executed ?
    dom.find('.edit_form').droppable({
        drop: function(event, ui) {
            if(debug) console.log('This code is executed #343 drop');
            $(this).removeClass("selected");
    		$($(this)[0][0]).val(ui.draggable.data('item').replace(/&/g, '%26').replace(/\?/g, '%3f'));
            $(this).attr("action", ui.draggable.data('item')+"/edit");
	        $(this).submit();
        },
        over: function(event, ui) {
            if(debug) console.log('This code is executed #343 over');
            $(this).addClass('selected');
        },
        out: function(event, ui) {
            if(debug) console.log('This code is executed #343 out');
            $(this).removeClass("selected");
        }
    });


    // the old rm_form was droppable, FIXME: replace with a trash icon or something
    dom.find('.rm_form').droppable({
        drop: function(event, ui) {
            var item = ui.draggable.data('item');
            $(this).removeClass("selected");
	        ui.remove_entry(ui.draggable.remove());
	        ui.draggable.remove();
        },
        over: function(event, ui) {
            $(this).addClass('selected');
        },
        out: function(event, ui) {
            $(this).removeClass("selected");
        }
    });

    // automatic settings for some special classes
    dom.find('.editable span').addClass('toggler');

    // setup some behaviors

    dom.find(".autovalidate").each(function(index, ob) { $(ob).validate(); } );

    dom.find('.auto_date').datepicker({dateFormat: "dd/mm/yy"});
    
    main_list = dom.find('#main_list');
    if (!!!main_list) {
        main_list = dom.find('.sortable');
	} else {
		main_list.sortable({
		    cursor: 'move',
		    distance: 50,
		    accept: '.entry',
		    //tolerence: 'pointer',
		    helper: 'original',
		    revert: true,
		    stop: function(event, ui) {
		        if ( event.ctrlKey ) {
		            var pat = $('#'+this.id+' li').map( function() { return $(this).data('item'); } ).get().join('/');
		            $.post('move', {'set': pat});
		            return true;
		        } else {
		            return false;
		        }
		    }
		});
	}
} // dom_initialize


// Helper function to complete valid object path's

function get_matching_elts(path_elt, callback) {
    if (path_elt.match('/')) {
        var _elts = path_elt.split('/');
        _elts.filter(function(e) { if (!!e) return true; });
        url = [document.location.origin];
        for (n=0;n<_elts.length;n++) {
            if (n == _elts.length-1) {
                pattern = _elts[n];
            } else {
                url.push(_elts[n]);
            }
        }
        url.push("/match?pattern=" + pattern);
        url = url.join('/');
    } else {
        pattern  = path_elt;
        url = base_path + "match?pattern=" + pattern;
    }
    var cur_path = path_elt;
    // AJAX URL
    
    $.get(url).success(function(data) { callback(data.items, cur_path); } );
}

/////// INIT/STARTUP STUFF

$(document).ready(function(){

    // add global methods
    $.fn.extend({
        center: function() {
            $('html,body').animate({
                scrollTop : $(this).offset().top - ($(window).height()/2) },
                100); }
        }
    );

    // some globals

    // extend validator (forms)

    $.validator.addMethod("identifier", function(value, element) {
        return this.optional(element) || ! RegExp('^[._$%/][$%/]*', 'i').test(value);
    }, 'No "$", "%" or "/" and don\' start with a dot or an underscore, please :)');

    // load main content

    // init keys
    // Some shortcuts
    keys.add('J', function() {
        ui.focus.next();
    });
    keys.add('K', function() {
        ui.focus.prev();
    });
    keys.add('ENTER', function() {
        var link = ui.focus.selected_link();
        if(debug) console.log(link);
        if (typeof(link) == 'string') {
            m = link.match(/^js: *(.*?) *$/);
            if (m) {
                eval(m[1]);
            } else {
                window.location = link;
            }
        } else {
            link.focus();
            link.trigger('click');
        }
    });
    keys.add('DEL', function() {
        ui.remove_entry( ui.focus.selected_item().data('item') );
    });
    keys.add('BACK', function() {
        ui.go_back();

    });
    keys.add('S', function() {
        // focus first entry
        $("input:text:visible:first").focus().center();
    });
    keys.add('ESC', function() {
        ui.focus.clear();
    });
    keys.add('E', function() {
        drink.serve(undefined, 'edit');
    });
    keys.add('L', function() {
        drink.serve(undefined, 'list');
    });
    keys.add('V', function() {
        drink.serve(undefined, 'view');
    });
    keys.add('H', function() {
        ui.dialog('<div title="Keyboard shortcuts"><ul><li>[E]dit</li><li>[S]earch / [S]elect first input field</li><li>[L]ist</li><li>[V]iew</li><li>[BACKSPACE] : one level up</li><li>[J] and [K]: change selection</li><li>[INS]ert</li><li>[DEL]ete</li><li>[ENTER]</li><li>[ESC]APE current dialogs</li></ul></div>');
    });

    $('#header_bar').on('dblclick', function() { $('#header_bar').fadeOut('slow'); });
	
	drink = new Drink();
// end of statup code
});
