url_regex = /^(\/|http).+/;
base_uri = document.location.href.replace(RegExp('[^/]*$'), '');
base_path = base_uri.replace(RegExp('http?://[^/]*'), '');

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
    // edit_entry
    this.popup_edit = function() {
       ui.dialog('<iframe title="'+me.title+'\'s properties" src="'+me.path+me.id+'/edit?embedded=1">No iframe support :(</iframe>', buttons=null, style='big');
    };
    this._get_html = function() {
        /* FIXME: ugly code */
        var expr = page_struct.get_from_factory('items', 'entry');
        var e = eval(expr)(me);
        //ui.focus.main_list.list.append(e);
        if (page_struct.get_from_factory('items', 'click')) {
            e.on('click', page_struct.get_from_factory('items', 'click'));
        } else if (page_struct.get_from_factory('items', 'dblclick')) {
            e.on('dblclick', eval(page_struct.get_from_factory('items', 'dblclick')));
        }
        // Html is element is prepared, now inject it
        e.data('item', me.id);
        e.data('item_url', me.path+encodeURI(me.id));
        if (page_struct.get_from_factory('items', 'hover')) {
            e.on('mouseenter mouseleave', eval(page_struct.get_from_factory('items', 'hover')));
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
    $('#main_list').append(e);
    me.elt = e;
    me.editable = new Editable(e, 'title', 'a', 'input_text');
    // add itself to main_list
    e.disableSelection();
    e.hide();
    e.fadeIn('slow');
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
                foot.append( $('<span id="dk_rate_btn" class="button" onclick="page_struct.change_rate()">I don\'t like it!</span>') );
            } else {
                foot.append( $('<span id="dk_rate_btn" class="button" onclick="page_struct.change_rate()">I like it!</span>') );
            }
            foot.append( $('<div id="comments" />') );
            $.post('comment').success( function(data) {
                page_struct.draw_comments(data.comments);
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
    this.change_rate = function() {
        if (page_struct.i_like) {
            var text="I like it!";
            var d={'unlike': 1};
        } else {
            var text="I don't like it !";
            var d={'like': 1};
        }
        page_struct.i_like = ! page_struct.i_like;
        $('#dk_rate_btn').text(text);
        console.log(text, d);
        $.post('rate', d);
    };
    this.validate_comment = function() {
        var e = $('#comments textarea');
        var txt = e.attr('value');
        $.post('comment', {text: txt}).
            success(function(d) {
                page_struct.draw_comments(d.comments);
            });
        $('#comments').html('');
    };
    this.draw_comments = function(comments) {
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
            txt.parent().append($('<span class="button" onclick="page_struct.validate_comment()">Send!</span>'));
            txt.attr('value', '');
        });
    };
    this.reload = function() {
        $.post('struct', {'childs': true, 'full': true}).
            success(me._fill).
            error(function() {
                ui.dialog('<div title="Error occured">Listing can\'t be loaded :(</div>');
        });
    };
    return this;
};
