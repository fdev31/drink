// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// MarkDown tags example
// http://en.wikipedia.org/wiki/Markdown
// http://daringfireball.net/projects/markdown/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------
save_doc = function(h) {
    // fixme: use somethin' else
    var url = $("#auto_edit_form").attr('action');
    var text = h.textarea.value;
    $.post(url, {'_dk_fields': 'content', 'content': text})
        .success(function() {
            var m = $('#auto_edit_form').parent().data('mdown');
            if (m) { // children entry
                m.load_page(m.source);
            } else { /* main document edition */
                ui.goto_object();
            };
        })
    return false;
}

untabber = function(mid) {
      var textarea = mid.textarea,
      selStart = textarea.selectionStart,
      selEnd = textarea.selectionEnd,
      selText = textarea.value.substring(selStart, selEnd),
      lines = [],
      charsAdded = 0;

      lines = selText.split(/\r?\n/);
      for (var i = 0, len = lines.length; i < len; i++) {
          re = /^\s{4}/;
          if (lines[i].match(re)) {
              lines[i] = lines[i].replace(re, '');
              charsAdded -= 4;
          }
      }
      textarea.selectionEnd = selEnd + charsAdded;
      return lines.join('\n');
}

tabber = function(mid) {
      var textarea = mid.textarea,
      selStart = textarea.selectionStart,
      selEnd = textarea.selectionEnd,
      selText = textarea.value.substring(selStart, selEnd),
      lines = [],
      charsAdded = 0;

      lines = selText.split(/\r?\n/);
      for (var i = 0, len = lines.length; i < len; i++) {
          lines[i] = "    "+lines[i];
          charsAdded += 4;
      }
      textarea.selectionEnd = selEnd + charsAdded;
      return lines.join('\n');
}

mySettings = {
    nameSpace: "markdown",
    previewParserPath:  './process',
    previewAutoRefresh: true,
	//previewInWindow: true,
	onCtrlEnter:		{afterInsert: save_doc, keepDefault: false},
	markupSet: [
		{name:'First Level Heading', key:'1', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
		{name:'Second Level Heading', key:'2', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
		{name:'Heading 3', key:'3', openWith:'### ', placeHolder:'Your title here...' },
		{name:'Heading 4', key:'4', openWith:'#### ', placeHolder:'Your title here...' },
		{name:'Heading 5', key:'5', openWith:'##### ', placeHolder:'Your title here...' },
		{name:'Heading 6', key:'6', openWith:'###### ', placeHolder:'Your title here...' },
		{separator:'---------------' },
		{name:'Bold', key:'B', openWith:'**', closeWith:'**'},
		{name:'Italic', key:'I', openWith:'_', closeWith:'_'},
		{separator:'---------------' },

        {name:'Un-indent selection', replaceWith:function(miu) {
            return miu.selection.replace(/^    /mg, '');
        }, beforeInsert:function(miu) {
            var e = jQuery.Event("keydown");
            e.shiftKey = true;
            e.ctrlKey = true;
            $(miu.textarea).trigger(e);
        }},
        {name:'Indent selection', openWith:'    ', beforeInsert:function(miu) {
            var e = jQuery.Event("keydown");
            e.shiftKey = true;
            e.ctrlKey = true;
            $(miu.textarea).trigger(e);
        }},

/*
		{name:'Deindent', replaceWith: untabber},
		{name:'Indent', replaceWith: tabber},
*/
		{separator:'---------------' },
		{name:'Bulleted List', openWith:'- ' },
		{name:'Numeric List', openWith:function(markItUp) {
			return markItUp.line+'. ';
		}},
		{separator:'---------------' },
		{name:'Picture', key:'P', replaceWith:'![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'},
		{name:'Link', key:'L', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder:'Your text to link here...' },
		{separator:'---------------'},
		{name:'Quotes', openWith:'> '},
		{name:'Code Block / Code', openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'},
		{separator:'---------------'},
		{name:'Preview', call:'preview', className:"preview"}
	],
}

MarkDown = function(uuid) {
    var me = this;
    this.source = '';
	this.uuid = uuid || "markdown";
	this.edit_html = function(opts, source) {
        if (!source)
            source = this.source;
        else
            this.source = source;
        var o = {'cols': "80", 'rows': "25", 'data': ''}
        if (! opts)
            $.extend(o, opts)
        var apply_editor = function(data) {
            var html = $('<form id="auto_edit_form" action="'+source+'edit" method="post"><input type="hidden" name="_dk_fields" value="content" /><textarea id="md_'+me.uuid+'_editor" name="content" cols="'+o.cols+'" rows="'+o.rows+'">'+(data || o.data)+'</textarea></form>');
            $('#'+me.uuid).html(html);
//            $('#'+me.uuid).addClass('markItUp');
            var settings = new Object();
            $.extend(settings, mySettings);
            settings.previewParserPath = source+'process';
            $('#'+me.uuid+' textarea:first').markItUp(settings);
        }
        if (source) {
            $.post(source+'struct', {'full': '1'}).success(function(data) {apply_editor(data.content)});
        } else {
            apply_editor(opts.data || page_struct.content);
        }
	}
    this.attach = function(obj, source) {
        if (!source)
            source = this.source;
        else
            this.source = source;

        var obj = $(obj);

        var foc_out = function() {
            me.load_page(source);
            $(this).bind('click', click);
        };
        var click = function() {
            $(this).unbind('click');
            me.edit_html({}, source);
            new KeyHandler(obj, {forced: ['TEXTAREA']}).add('ESC', foc_out);
        };

        obj.data('path', source);

        obj.bind({
            'click': click,
            'focusout': foc_out,
        });
    }
    this.load_page = function(source) {
        if (!source) {
            source = this.source;
            me.remote_obj = false;
        } else {
            me.remote_obj = true;
            me.source = source;
        }

        $.post(source+'struct', {'full': '1'}).success(function(data) {
            if (!me.remote_obj) {
                page_struct.merge(data);
            }
            else { if(!page_struct.foreigners) page_struct.foreigners = new Object();
                page_struct.foreigners[source] = data;
            };
            if (data.subpages_blog) {
                url = source+'blog_content';
                var is_blog = true;
            } else {
                url = source+'process';
                var is_blog = false;
            };
            $.post(url).success(
                function(data) {
                    var e = $('#'+me.uuid);
                    e.html(data);
                    e.removeClass('markItUp');
                    if (is_blog) {
                        if (!$('.blog_entry:first').attr('id'))
                            $('.blog_entry').each( function(i, e) {
                            var e = $(e);
                            var n = 'blog_entry_'+i;
                            e.attr('id', n);
                            var m = new MarkDown(n);
                            m.attach(e, base_path+e.attr('entry_id')+'/');
                            e.data('mdown', m);
                        });
                    } else {
                        if (!$('#markdown.editable').attr('id')) {
                            var e = $('#markdown.editable');
                            var n = 'markdown.editable';
                            new MarkDown(n).attach(e, base_path);
                        }
                    }
                    dom_initialize(e);
                }
            ).error(
                function(){ui.dialog('data failed')}
            );
        }).error(function(){ui.dialog('struct failed')});
    }
	return this;
}
// mIu nameSpace to avoid conflict.
miu = {
	markdownTitle: function(markItUp, char) {
		heading = '';
		n = $.trim(markItUp.selection||markItUp.placeHolder).length;
		for(i = 0; i < n; i++) {
			heading += char;
		}
		return '\n'+heading;
	}
}
