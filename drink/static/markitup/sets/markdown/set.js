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
    $("#auto_edit_form").submit();
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
