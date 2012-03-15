var Editable = function(dom, tag, orig, type, opt_validator) {
    var type = type || 'input_text';

    this.input_text = function(val) {
        return '<input class="inline" type="text" value="'+val+'" />';
    };
    this.textarea = function(val) {
        return '<textarea class="inline">'+val+'</textarea>';
    };
    this.edit = function () {
        var me = me || $(this).data('editable');

        me.elt.off('dblclick');
        if(!drink.d._perm.match(/w/)) { return; }

        // set an input field up, with focus
        me.old_text = me.orig.text();
        if (!!!me.input)
            me.input = $(me[me.type](me.old_text));
        var form = $('<form class="inline_form" id="temp_edit_form" action="xx" onsubmit="return false;" />');
        form.append(me.input);
        me.orig.replaceWith(form);
        form.css('display', 'inline');
        form.css('padding', '0');
        me.input.css('display', 'inline');
        me.input.css('padding', '0');
        me.input.select();
        // on entry input blur
        me.input.on('blur', me._exit_edit);
        // trigger blur on ENTER keyup

        if (me.type != 'textarea') {
            me.input.on('keyup', me._blur_on_validate);
        } else {
            me.input.on('change', me._blur_on_validate);
        }
    };

    this._blur_on_validate = function (e) {
        if (e.keyCode == 27) {
             $(this).data('canceled', true);
             $(this).trigger('blur');
        } else if (e.keyCode == 13) {
             $(this).trigger('blur');
        }
    };
    this._init = function() {
        me.elt.on('dblclick', me.edit);
    };
    this._exit_edit = function () {
        var txt = null;
        if ( !!!$(this).data('canceled') && $(this).val() != me.old_text ) {
            txt = $(this).val().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            me.validate_fn(txt);
            if (!!opt_validator)
                opt_validator(txt);
        } else {
            txt = me.old_text;
        }
        inp = me.input;
        me.orig.text(txt);
        inp.parent().replaceWith(me.orig);
        me.orig.center();
        me._init();
    };
    this.validate_fn = function(text) {
        if(debug) console.log(tag, me.field);
        var o = {_dk_fields: tag}
        o[tag] = text;
        $.post(me.elt.data('item_url')+'/edit', o);
    };
    var me = this;
    me.type = type;
    me.field = tag;
    me.elt = $(dom);
    me.orig = me.elt.find(orig+':first');
    me.elt.data('editable', me);
    me._init();
    return this;
}