url_regex = /^(\/|http).+/;
base_path = document.location.href.replace(RegExp('[^/]*$'), '')
    .replace(RegExp('http?://[^/]*'), ''); // only keep trailing path

var Drink = function() {
 	this.change_rate = function() {
        if (me.i_like) {
            var text="I like it!";
            var d={'unlike': 1};
        } else {
            var text="I don't like it !";
            var d={'like': 1};
        }
        me.i_like = ! me.i_like;
        $('#dk_rate_btn').text(text);
        $.post(base_path+'rate', d);
    };
	// item getter
	this.get_entry = function(id) {
		return me.entries.filter(function(e) {return e.id === id})[0];
	};
	// page switcher
	this.serve = function (obj, view) {
		if(debug) console.log('------------ drink.serve ------------');
        var action_to_take = view || me.d.default_action;
        var obj = obj;
        var view = view;
		var loader = me.d.loaders[view];
		
		if (!!me.cur_action)
	        $('#main_body , #footers').fadeOut();
	     
		if ( obj || action_to_take !== me.cur_action)
			setTimeout(function() {
			    if(!!!view)
			        view = '';
		        if (!!obj) {
		            if (typeof(obj) == 'string') {
		                var prefix = obj;
		            } else {
		                var prefix = obj.path+obj.id+'/';
		            }
		            base_path = prefix;
		        } else {
		            var prefix = '';
		        }
		        var fill_it = function() {
				}
		        if(debug) console.log("xxxxxxxxxxxxx=> "+view+" on "+obj);
				$.get(prefix+view)
		        .success(function(data) {
		        	if(debug) console.log('success '+action_to_take);
		            ui.load_html_content(data);
		            if(debug) console.log('view='+view);
		            me.cur_action = action_to_take;
		            $('#main_body, #footers').fadeIn();
		            if(debug) console.log('action '+me.cur_action);
					if(debug) console.log('Loader: '+loader, me.d.loaders);
					if (!!loader) {
						eval(loader);
					} else {
						if(debug) console.log('No hook!')
					}
		        })
		        .error(function(data, code) {
		        	if(debug) console.log(data, code);
			        $('#main_body , #footers').fadeOut();
		    	});
		    }, 300);
    };
        
    // XXX: change this to another place, in Entry ?
    this.get_from_factory = function(which, what) {
        var val = me.d[which+'_factory'][what];
        if (val && !!!val.match(/.*\./))
            val = "me."+val;
        return val;
    };
    this.add_item = function(data, focus) {
        var e = new Entry(data);
        me.entries.push( e );
        me.d.items.push( data );
        if (!!focus) e.elt.center();
        call_hook_add_item(data);
    };
	// self factory shortcuts
	this.write_footers = function() {
		var foot = $('#footers');
		// add comments		
		if (me.d._perm.match(/r/)) {
			if(debug) console.log('comments & rates...');
		    if (me.i_like) {
		        me.i_like = true;
		        foot.append( $('<span id="dk_rate_btn" class="button" onclick="drink.change_rate()">I don\'t like it!</span>') );
		    } else {
		    	me.i_like = false;
		        foot.append( $('<span id="dk_rate_btn" class="button" onclick="drink.change_rate()">I like it!</span>') );
		    }
		    foot.append( $('<div id="comments" />') );
		    $.post(base_path+'comment').success( function(data) {
		        ui.draw_comments(data.comments);
		    });
		}
		// add uploader
		if ( me.d._perm.match(/a/) ) {
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
	}
	// constructor
	var me = this;
	if(debug) console.log('==============DRINK CREATION==============');
	$.post(base_path+'struct', {'childs': true, 'full': true})
		.success(function(data, status, req) {
		    if(debug) console.log(data);
			me.d = data;			
		    if (!data._perm) return;
			me.entries = $.map(me.d.items, function(i) { return new Entry(i); });
			me.cur_action = undefined;
			// load actions		
		    ui.load_action_list(data.actions);
	    	me.i_like = data.i_like;
	    	//me.serve(undefined, me.d.default_action);
	        setTimeout(me.write_footers, 300);
			var loader = me.d.loaders[me.d.default_action];
			if(!!loader)
				eval(loader);
			me.cur_action = me.d.default_action; 
		})
		.error(function() {
			ui.dialog('<div title="Error occured">Listing can\'t be loaded :(</div>');
		});
	return me;
}

/* Entry Position & Page */


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

            var elt = drink.get_entry(me.data('item'));
            if (!elt) return;
            if(!elt._perm.match(/w/)) { return; }

            $(this).data('edit_called', setTimeout(function() {
                var item_name = me.data('item');
                var edit_span = $('<span class="actions"></span>');
                edit_span.append('<a title="Edit" onclick="drink.get_entry(\''+item_name+'\').popup_edit()"><img class="minicon" src="/static/actions/edit.png" /></a>');
                edit_span.append('<a title="Delete" onclick="drink.get_entry(\''+item_name+'\').popup_remove()" ><img class="minicon" src="/static/actions/delete.png" /></a>');
                edit_span.fadeIn('slow');
                me.append(edit_span);
            }, 500));
        } else if (event.type == "mouseleave") {
            clearTimeout($(this).data('edit_called'));
            $(this).data('edit_called', false);
            $(this).find('.actions').fadeOut('slow', function() {$(this).remove();});
        }
    };
    // edit_entry
    this.popup_edit = function() {
       ui.dialog('<iframe title="'+me.title+'\'s properties" src="'+me.path+me.id+'/edit?embedded=1">No iframe support :(</iframe>', buttons=null, style='big');
    };
    this._get_html = function() {
        /* FIXME: ugly code */
        if(debug) console.log("get_html");
        var expr = drink.get_from_factory('items', 'entry');
        var e = eval(expr)(me);
        //ui.focus.main_list.list.append(e);
        if (drink.get_from_factory('items', 'click')) {
            e.on('click', drink.get_from_factory('items', 'click'));
        } else if (drink.get_from_factory('items', 'dblclick')) {
            e.on('dblclick', eval(drink.get_from_factory('items', 'dblclick')));
        }
        // Html is element is prepared, now inject it
        e.data('item', me.id);
        e.data('item_url', base_path+encodeURI(me.id));
        if (drink.get_from_factory('items', 'hover')) {
            e.on('mouseenter mouseleave', eval(drink.get_from_factory('items', 'hover')));
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
        return $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+base_path+me.id+'/" title="'+me.description+'">'+(me.title || me.id)+'</a></li>');
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
        return $('<li class="entry"><img width="32px" src="'+mime+'" /><a class="item_name" href="'+base_path+me.id+'/" title="'+me.description+'"><img src="'+base_path+me.id+'/raw" /><div class="caption">'+(me.title || me.id)+'</a></div></li>');
    };

    $.extend(this, data);
    // make html entry
    var e = me._get_html();
    me.elt = e;
    me.editable = new Editable(e, 'title', 'a', 'input_text');
    // add itself to main_list
//    e.disableSelection();
//    e.hide();
//    e.fadeIn('slow');
    return this;
};
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

var validate = function(data) {
	if (!!data['error']) {
		ui.failure_dialog('Error', data['message']);
		return false;
	}
	return true;
};
