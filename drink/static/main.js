// globals
debug = false;

var Entry = function(data) {
    var me = this;
    // remove_entry
    this.popup_remove = function(item) {
        ui.dialog('<div id="remove-confirm" title="Do you really want to remove this item ?">Please, confirm removal.</div>', {
            Accept: function() {
                $( this ).dialog( "close" );
                $.ajax({
                    url: me.path+'rm?name='+me.id
                }).success(function() {
                    me.elt.slideUp('slow', function() {$(this).remove();});
                }).error(function(){
                    ui.dialog('<div title="Error occured">Sorry, something didn\'t work correctly</div>');
                   });
            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        });
    };
    /* Popup actions for items */
    this.popup_actions = function (event) {
        if (event.type == "mouseenter") {
            var me = $(this);
            if ( me.data('edit_called') ) {
                return;
            }

            var elt = page_struct.get_by_id(me.data('item'));
            if (!elt) return;
            if(!elt._perm.match(/w/)) { return; }

            $(this).data('edit_called', setTimeout(function() {
                var item_name = me.data('item');
                var edit_span = $('<span class="actions"></span>');
                edit_span.append('<a title="Edit" onclick="page_struct.get_ent(\''+item_name+'\').popup_edit()"><img class="minicon" src="/static/actions/edit.png" /></a>');
                edit_span.append('<a title="Delete" onclick="page_struct.get_ent(\''+item_name+'\').popup_remove()" ><img class="minicon" src="/static/actions/delete.png" /></a>');
                edit_span.fadeIn('slow');
                me.append(edit_span);

                }, 500));
        } else if (event.type == "mouseleave") {
            clearTimeout($(this).data('edit_called'));
            $(this).data('edit_called', false);
            $(this).find('.actions').fadeOut('slow', function() {$(this).remove();});
        }
    };

    // handle inline title edition
    this._blur_on_validate = function (e) {
        if (e.keyCode == 27) {
             $(this).data('canceled', true);
             $(this).trigger('blur');
        } else if (e.keyCode == 13) {
             $(this).trigger('blur');
        }
    };

    this._exit_edit_title = function () {
        var txt = null;
        uid = $(this).parent().data('item');
        if (uid == undefined ) { return; }

        if ( !!!$(this).data('canceled') && $(this).val() != $(this).data('orig_text') ) {
            txt = $(this).val().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            $.post(''+encodeURI(uid)+'/edit', {title: txt} );
        } else {
            txt = $(this).data('orig_text');
        }

        $(this).replaceWith($('<a class="item_name" href="./'+encodeURI(uid)+'/">'+txt+'</a>'));
        $(this).parent().dblclick(me._enter_edit_func);
    };

    // edit_entry
    this.popup_edit = function() {
       ui.dialog('<iframe title="'+me.title+'\'s properties" src="'+me.path+me.id+'/edit?embedded=1">No iframe support :(</iframe>', buttons=null, style='big');
    };

    this.edit_title = function () {
        if(!me._perm.match(/w/)) { return; }
        if ( me.elt.has('input').length !== 0 ) { return; }

        var orig = me.elt.find('a.item_name').first();
        // set an input field up, with focus
        var inp = $("<input class=\"inline_edit\" value='"+orig.text()+"' />");
        inp.data('orig_text', orig.text());

        // replace second children
        orig.replaceWith(inp);
        inp = me.elt.find("input");
        inp.select();

        // on entry input blur
        inp.blur(me._exit_edit_title);

        // trigger blur on ENTER keyup
        inp.keyup(me._blur_on_validate);
    };

    this._get_html = function() {
        /* FIXME: ugly code */
        var expr = page_struct.get_from_factory('items', 'entry');
        var e = eval(expr)(me);
        ui.main_list.list.append(e);
        if (page_struct.get_from_factory('items', 'click')) {
            e.bind('click', page_struct.get_from_factory('items', 'click'));
        } else if (page_struct.get_from_factory('items', 'dblclick')) {
            e.bind('dblclick', eval(page_struct.get_from_factory('items', 'dblclick')));
        }
        // Html is element is prepared, now inject it
        e.data('item', me.id);
        e.data('item_url', me.path+me.id);
        if (page_struct.get_from_factory('items', 'hover')) {
            e.bind('mouseenter mouseleave', eval(page_struct.get_from_factory('items', 'hover')));
        }
        if ( !! me._nb_items ) {
            if ( me._nb_items == 1 ) {
                e.append($('&nbsp;<span class="infos">(1 item)</span>'));
            } else {
                e.append($('&nbsp;<span class="infos">('+me._nb_items+' items)</span>'));
            }
        }
        return e;
    };

    /* construtor */
    this.default_factory = function() {
        // builds li element around an item object
        var mime = "";
        if ( me.mime ) {
            if ( me.mime.match( url_regex )) {
                mime = me.mime;
            } else {
                mime = "/static/mime/"+me.mime+".png";
            }
        } else {
            mime = "/static/mime/page.png";
        }
        return $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+me.path+me.id+'/" title="'+me.description+'">'+(me.title || me.id)+'</a></li>');
    };

    this.image_factory = function() {
        // builds li element around an item object
        var mime = "";
        if ( me.mime ) {
            if ( me.mime.match( url_regex )) {
                mime = me.mime;
            } else {
                mime = "/static/mime/"+me.mime+".png";
            }
        } else {
            mime = "/static/mime/page.png";
        }
        return $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+me.path+me.id+'/" title="'+me.description+'"><img src="'+me.path+me.id+'/raw" /><div class="caption">'+(me.title || me.id)+'</a></div></li>');
    };

    $.extend(this, data);
    // make html entry
    var e = me._get_html();
    me.elt = e;
    // add itself to main_list
    e.disableSelection();
    e.hide();
    e.fadeIn('slow');
    return this;
};

var Page = function () {
    var me = this;
    this.classes = [];
    this._perm = 'r';
    this.description = '';
    this.id = '?';
    this.items = [];
    this.mime = "none";
    this.path = "/";
    this.logged_in = false;
    this.title = "unk";
    this.merge = function (d) {
        me.id_idx_map = new Object();
        $.extend(me, d);
        me.items = [];
        me.entries = [];
        if (d.items) {
            for (var i=0 ; i<d.items.length ; i++)
                me.add_item(d.items[i]);
        } else {
            me.items = me.entries = [];
        }
    };
    this.get_ent = function(child_id) {
        return this.entries[this.id_idx_map[child_id]];
    };
    this.get_by_id = function(child_id) {
        return this.items[this.id_idx_map[child_id]];
    };
    this.get_from_factory = function(which, what) {
        var val = me[which+'_factory'][what];
        if (val && !!!val.match(/.*\./))
            val = "me."+val;
        return val;
    };
    this.add_item = function(data) {
        var e = new Entry(data);
        me.id_idx_map[data.id] = me.entries.length;
        me.entries.push( e );
        me.items.push( data );
        e.elt.center();
        call_hook_add_item(data);
    };
    this._fill = function (data, status, req) {
        if(debug) console.log(data);
        me.merge(data);
        if (!data._perm) return;

        //setTimeout(ui.load_action_list, 500, data.actions);
        ui.load_action_list(data.actions);

        // list-item creation fonction
        var foot = $('#footers');

        if (me._perm.match(/r/)) {
            if (me.i_like) {
                foot.append( $("<button>I don't like anymore</button>") );
            } else {
                foot.append( $("<button>I like it!</button>") );
            }
            foot.append( $('<div id="comments" />') );
            $.post('comment').success( function(data) {
                if(data.comments.length === 0) {
                    $('#comments').append('<span>No comment yet</span>');
                } else {
                    $('#comments').append('<div>Comments:</div>');
                    for (i=0; i<data.comments.length; i++) {
                        $('#comments').append($('<div><strong>'+data.comments[i].from+':</strong>&nbsp;'+data.comments[i].message+'</div>'));
                    }
                }
            });
        }
        if ( me._perm.match(/a/) ) {
            foot.append( $('<div id="file-uploader" class="row"></div>') );

            // Integration of http://valums.com/ajax-upload/
            try {
                qq.UploadDropZone.prototype._isValidFileDrag = function(e){
                    return true;
                };
                var uploader = new qq.FileUploader({
                    element: $('#file-uploader')[0],
                    action: 'upload',
                    //debug: true,
                    showMessage: function(message){ $('<div title="Drop zone">'+message+'</div>'); },
                    onComplete: function(id, fileName, data){
                        if ( data.id ) {
                            ui.add_item(data);
                        }
                        $('ul.qq-upload-list > li.qq-upload-success').fadeOut('slow',
                            function() { $(this).remove(); });
                    }});
            } catch (ReferenceError) {
                //console.log('Uploader code not available');
            }
        }
    };
    this.reload = function() {
        $.post('struct', {'childs': true, 'full': true})
            .success(me._fill).error(function() {
            ui.dialog('<div title="Error occured">Listing can\'t be loaded :(</div>');
        });
    };
    return this;
};

page_struct = new Page();

url_regex = /^(\/|http).+/;
base_uri = document.location.href.replace(RegExp('[^/]*$'), '');
base_path = base_uri.replace(RegExp('http?://[^/]*'), '');

var Position = function(default_pos, list_getter, selection_class) {
    this.position = default_pos;
    this.lists = list_getter; /* name: children css_selector */
    this.current_list = list_getter[0]; /* name , list */
    this.current_list_pos = 0;
    this.selection_class = selection_class;
    this.wrap = true;

    this._select = function() {
        l = this.current_list[1];
        if ( typeof(l) == "string" ) {
            l = $(l);
        } else /* function */ {
            l = l();
        }
        return l;
    };
    this.clear = function() {
        var i = this.selected_item();
        i.removeClass(this.selection_class);
        this.current_list_pos = 0;
        this.current_list = this.lists[0];
        this.position = -1;
        this.highlight( this._select()[0] );
    };
    this.selected_link = function() {
        var m = this.selected_item();
        if (m.attr('href')) {
            return m.attr('href');
        } else if (m.attr('onclick')) {
            return 'js:'+m.attr('onclick');
        } else if (m.find('a:first').attr('href')) {
            return m.find('a:first').attr('href');
        } else if (m.find('.action:first').attr('onclick')) {
            return 'js:'+m.find('.action:first').attr('onclick');
        } else if (m.find('input:first')) {
            return m.find('input:first');
        } else if (m.find('select:first')) {
            return m.find('select:first');
        } else if (m.find('.input:first')) {
            return m.find('.input:first');
        }
    };
    this.selected_item = function() {
        return $(this._select()[this.position]);
    };
    this.next = function() {
        l = this._select();
        if (this.position < l.length-1) { // simple case
            $(l.get(this.position)).removeClass(this.selection_class);
            this.position += 1;
            this.highlight( l[this.position] );
            this.select_next();
        } else if (this.lists[this.lists.length-1][0] != this.current_list[0]) { /* boundary limit, change the list */
            try {
                $(l.get(this.position)).removeClass(this.selection_class);
            } catch (typeError) {
            }
            this.current_list_pos += 1;
            this.current_list = this.lists[this.current_list_pos];
            this.highlight( this._select()[0] );
            this.position = 0;
        } else { /* end of the cycle */
            this.clear();
        }
    };
    this.prev = function() {
        l = this._select();
        if (this.position > 0) { // simple case
            $(l.get(this.position)).removeClass(this.selection_class);
            this.position -= 1;
            this.select_prev();
            this.highlight( l[this.position] );
        } else if (this.lists[0][0] != this.current_list[0]) { // boundary limit, change the list
            $(l.get(this.position)).removeClass(this.selection_class);
            this.current_list_pos -= 1;
            this.current_list = this.lists[this.current_list_pos];
            this.highlight( this._select()[this.position] );
            this.position = 0;
        } else { /* end of the cycle */
            $(l[this.position]).removeClass(this.selection_class);
            this.current_list_pos = this.lists.length-1;
            this.current_list = this.lists[this.current_list_pos];
            this.position = 0;
            this.highlight( this._select()[0] );
        }
    };
    this.highlight = function(item) {
        if (!item)
            return;
        var item = $(item);
        item.addClass(this.selection_class);
        item.focus();
        item.center();
    };
    this.select_prev = $.noop;
    this.select_next = $.noop;
    return this;
};

MainList = function(id) {
    this.id = id || "main_list";
    var me = this;

    this.list = $('#'+this.id);
    this.list.sortable({
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

    if ($('#'+this.id).length === 0) {
        if (debug) console.log('No list with name '+this.id);
    }
    return this;
};

// UI Object
ui = new Object({
  main_list: new MainList(),
  go_back: function() {
    /*
        if(!!document.location.pathname.match(/\/$/)) {document.location.href='../'} else{document.location.href='./'}
      */

        if (window.location.href != base_uri) {
            window.location = base_uri;
        } else {
            window.location = base_uri+'../';
        }
    },
  goto_object: function(obj, view) {
        if(!!!view)
            view = '';
        if (!!!obj) {
            window.location = base_uri+view;
        } else {
            window.location = obj.path+obj.id+'/'+view;
        }
    },
    // ADD an entry Popup
    add_entry: function() {
         if ( page_struct.classes.length < 1 ) {
            w = $('<div title="Ooops!">Nothing can be added here, sorry</div>').dialog({closeOnEscape:true});
            setTimeout(function(){w.fadeOut(function(){w.dialog('close');});}, 2000);
            return;
        }
        var template = '<div id="new_obj_form"  title="New item informations"><select class="obj_class" class="required" name="class"><option value="" label="Select one item type">Select one item type</option>';
        var tpl_ftr = '</select><div class="obj_name"><label for="new_obj_name">Name</label><input id="new_obj_name" type="text" name="name" class="obj_name required identifier" minlength="2" /></div></div>';
        for (t=0; t<page_struct.classes.length; t++) {
            template += '<option value="{0}" label="{0}">{0}</option>'.replace(/\{0\}/g, page_struct.classes[t]);
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
            $.post('add', item).success(page_struct.add_item);
        };

        new_obj.find('input.obj_name').keyup(check_fn);

        new_obj.dialog({
            closeOnEscape:true,
            modal: true,
            buttons: [ {text: 'OK', click: validate_fn} ]
        });

        if (page_struct.classes.length == 1) {
            new_obj.find(".obj_class").val(page_struct.classes[0]).attr('disabled', true);
            new_obj.find('input.obj_name').trigger('click').focus();
        }
    },

    edit: function(what) {
        ui.dialog('<div title="Edit"><iframe style="height: 100%" src="'+what+'edit?embedded=1"></iframe></div>');
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
                        (!elt.condition || eval(elt.condition) )  && (page_struct._perm.match('w') || page_struct._perm.match(elt.perm)) ) {
                        // if plain link
                        if (elt.action.match(/^[^\(\)\[\] ;]+$/)) {
                            if(!!elt.action.match(/\/$/)) {
                                var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
                            } else {
                                var text='<a class="action '+(elt.style || '')+'"  title="'+elt.title+'" href="'+base_uri+elt.action+'"><img  class="icon" src="/static/actions/'+elt.icon+'.png" alt="'+elt.title+' icon" /></a>';
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
    selection: new Position(-1, [
        ['items', '#main_body .entry'],
        ['actions',  '#commands a.action']
    ], 'highlighted')
    }
);

// KEYPRESS THINGS
var KeyHandler = function(o, options) {
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
                if (debug) ui.message("Don't know how to handle"+e);
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

// ADD ITEM THINGS

add_item_hooks = [];


function call_hook_add_item(data) {
   for(i=0; i<add_item_hooks.length; i++) {
        add_item_hooks[i](data);
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
        url = base_uri + "match?pattern=" + pattern;
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
    ui.main_list = new MainList();
    page_struct.reload();

    // extend validator (forms)

    $.validator.addMethod("identifier", function(value, element) {
        return this.optional(element) || ! RegExp('^[._$%/][$%/]*', 'i').test(value);
    }, 'No "$", "%" or "/" and don\' start with a dot or an underscore, please :)');

    // load main content

    // init keys
    // Some shortcuts
    keys.add('J', function() {
        ui.selection.next();
    });
    keys.add('K', function() {
        ui.selection.prev();
    });
    keys.add('ENTER', function() {
        var link = ui.selection.selected_link();
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
        ui.remove_entry( ui.selection.selected_item().data('item') );
    });
    keys.add('BACK', function() {
        ui.go_back();

    });
    keys.add('S', function() {
        // focus first entry
        $("input:text:visible:first").focus().center();
    });
    keys.add('ESC', function() {
        ui.selection.clear();
    });
    keys.add('E', function() {
        ui.goto_object(undefined, 'edit');
    });
    keys.add('L', function() {
        ui.goto_object(undefined, 'list');
    });
    keys.add('V', function() {
        ui.goto_object(undefined, 'view');
    });
    keys.add('H', function() {
        ui.dialog('<div title="Keyboard shortcuts"><ul><li>[E]dit</li><li>[S]earch / [S]elect first input field</li><li>[L]ist</li><li>[V]iew</li><li>BACKSPACE: one level up</li><li>UP/DOWN: change selection</li><li>[DEL]ete</li><li>[ENTER]</li><li>ESCAPE: close dialogs</li></ul></div>');
    });

    dom_initialize($(document));
// end of statup code
});
