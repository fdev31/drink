from __future__ import absolute_import
import drink
import logging
log = logging.getLogger('spreadsheet')

class SpreadSheet(drink.Page):

    drink_name = 'SpreadSheet'

    mime = u"markdown"

    content = '''<table class="jSheet ui-widget-content" id="jSheet_0_0" border="1px" cellpadding="0" cellspacing="0" style="width: 1200px; "><colgroup><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"><col style="width: 120px; " width="120px"></colgroup><tbody><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r0"></td><td id="0_table0_cell_c1_r0"></td><td id="0_table0_cell_c2_r0"></td><td id="0_table0_cell_c3_r0"></td><td id="0_table0_cell_c4_r0"></td><td id="0_table0_cell_c5_r0"></td><td id="0_table0_cell_c6_r0"></td><td id="0_table0_cell_c7_r0"></td><td id="0_table0_cell_c8_r0"></td><td id="0_table0_cell_c9_r0"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r1"></td><td id="0_table0_cell_c1_r1"></td><td id="0_table0_cell_c2_r1"></td><td id="0_table0_cell_c3_r1"></td><td id="0_table0_cell_c4_r1"></td><td id="0_table0_cell_c5_r1"></td><td id="0_table0_cell_c6_r1"></td><td id="0_table0_cell_c7_r1"></td><td id="0_table0_cell_c8_r1"></td><td id="0_table0_cell_c9_r1"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r2"></td><td id="0_table0_cell_c1_r2"></td><td id="0_table0_cell_c2_r2"></td><td id="0_table0_cell_c3_r2"></td><td id="0_table0_cell_c4_r2"></td><td id="0_table0_cell_c5_r2"></td><td id="0_table0_cell_c6_r2"></td><td id="0_table0_cell_c7_r2"></td><td id="0_table0_cell_c8_r2"></td><td id="0_table0_cell_c9_r2"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r3"></td><td id="0_table0_cell_c1_r3"></td><td id="0_table0_cell_c2_r3"></td><td id="0_table0_cell_c3_r3"></td><td id="0_table0_cell_c4_r3"></td><td id="0_table0_cell_c5_r3"></td><td id="0_table0_cell_c6_r3"></td><td id="0_table0_cell_c7_r3"></td><td id="0_table0_cell_c8_r3"></td><td id="0_table0_cell_c9_r3"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r4"></td><td id="0_table0_cell_c1_r4"></td><td id="0_table0_cell_c2_r4"></td><td id="0_table0_cell_c3_r4"></td><td id="0_table0_cell_c4_r4"></td><td id="0_table0_cell_c5_r4"></td><td id="0_table0_cell_c6_r4"></td><td id="0_table0_cell_c7_r4"></td><td id="0_table0_cell_c8_r4"></td><td id="0_table0_cell_c9_r4"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r5"></td><td id="0_table0_cell_c1_r5"></td><td id="0_table0_cell_c2_r5"></td><td id="0_table0_cell_c3_r5"></td><td id="0_table0_cell_c4_r5"></td><td id="0_table0_cell_c5_r5"></td><td id="0_table0_cell_c6_r5"></td><td id="0_table0_cell_c7_r5"></td><td id="0_table0_cell_c8_r5"></td><td id="0_table0_cell_c9_r5"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r6"></td><td id="0_table0_cell_c1_r6"></td><td id="0_table0_cell_c2_r6"></td><td id="0_table0_cell_c3_r6"></td><td id="0_table0_cell_c4_r6"></td><td id="0_table0_cell_c5_r6"></td><td id="0_table0_cell_c6_r6"></td><td id="0_table0_cell_c7_r6"></td><td id="0_table0_cell_c8_r6"></td><td id="0_table0_cell_c9_r6"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r7"></td><td id="0_table0_cell_c1_r7"></td><td id="0_table0_cell_c2_r7"></td><td id="0_table0_cell_c3_r7"></td><td id="0_table0_cell_c4_r7"></td><td id="0_table0_cell_c5_r7"></td><td id="0_table0_cell_c6_r7"></td><td id="0_table0_cell_c7_r7"></td><td id="0_table0_cell_c8_r7"></td><td id="0_table0_cell_c9_r7"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r8"></td><td id="0_table0_cell_c1_r8"></td><td id="0_table0_cell_c2_r8"></td><td id="0_table0_cell_c3_r8"></td><td id="0_table0_cell_c4_r8"></td><td id="0_table0_cell_c5_r8"></td><td id="0_table0_cell_c6_r8"></td><td id="0_table0_cell_c7_r8"></td><td id="0_table0_cell_c8_r8"></td><td id="0_table0_cell_c9_r8"></td></tr><tr style="height: 18px; " height="18px"><td id="0_table0_cell_c0_r9"></td><td id="0_table0_cell_c1_r9"></td><td id="0_table0_cell_c2_r9"></td><td id="0_table0_cell_c3_r9"></td><td id="0_table0_cell_c4_r9"></td><td id="0_table0_cell_c5_r9"></td><td id="0_table0_cell_c6_r9"></td><td id="0_table0_cell_c7_r9"></td><td id="0_table0_cell_c8_r9"></td><td id="0_table0_cell_c9_r9"></td></tr><tr style="height: 18px; "><td id="0_table0_cell_c0_r10"></td><td id="0_table0_cell_c1_r10"></td><td id="0_table0_cell_c2_r10"></td><td id="0_table0_cell_c3_r10"></td><td id="0_table0_cell_c4_r10"></td><td id="0_table0_cell_c5_r10"></td><td id="0_table0_cell_c6_r10"></td><td id="0_table0_cell_c7_r10"></td><td id="0_table0_cell_c8_r10"></td><td id="0_table0_cell_c9_r10"></td></tr><tr style="height: 18px; "><td id="0_table0_cell_c0_r11"></td><td id="0_table0_cell_c1_r11"></td><td id="0_table0_cell_c2_r11"></td><td id="0_table0_cell_c3_r11"></td><td id="0_table0_cell_c4_r11"></td><td id="0_table0_cell_c5_r11"></td><td id="0_table0_cell_c6_r11"></td><td id="0_table0_cell_c7_r11"></td><td id="0_table0_cell_c8_r11"></td><td id="0_table0_cell_c9_r11"></td></tr><tr style="height: 18px; "><td id="0_table0_cell_c0_r12"></td><td id="0_table0_cell_c1_r12"></td><td id="0_table0_cell_c2_r12"></td><td id="0_table0_cell_c3_r12"></td><td id="0_table0_cell_c4_r12"></td><td id="0_table0_cell_c5_r12"></td><td id="0_table0_cell_c6_r12"></td><td id="0_table0_cell_c7_r12"></td><td id="0_table0_cell_c8_r12"></td><td id="0_table0_cell_c9_r12"></td></tr><tr style="height: 18px; "><td id="0_table0_cell_c0_r13"></td><td id="0_table0_cell_c1_r13"></td><td id="0_table0_cell_c2_r13"></td><td id="0_table0_cell_c3_r13"></td><td id="0_table0_cell_c4_r13"></td><td id="0_table0_cell_c5_r13"></td><td id="0_table0_cell_c6_r13"></td><td id="0_table0_cell_c7_r13"></td><td id="0_table0_cell_c8_r13"></td><td id="0_table0_cell_c9_r13"></td></tr><tr style="height: 18px; "><td id="0_table0_cell_c0_r14"></td><td id="0_table0_cell_c1_r14"></td><td id="0_table0_cell_c2_r14"></td><td id="0_table0_cell_c3_r14"></td><td id="0_table0_cell_c4_r14"></td><td id="0_table0_cell_c5_r14"></td><td id="0_table0_cell_c6_r14"></td><td id="0_table0_cell_c7_r14"></td><td id="0_table0_cell_c8_r14"></td><td id="0_table0_cell_c9_r14"></td></tr></tbody></table>'''

    default_action = "view"

    js = drink.Page.js + ['/static/js/raphael-min.js',
            '/static/js/g.raphael-min.js',
            '/static/js/parser.js',
            '/static/js/jquery.sheet.min.js',
            '/static/js/jquery.colorPicker.min.js',
    '''

        //This function builds the inline menu to make it easy to interact with each sheet instance
        function inlineMenu(I){
            I = (I ? I.length : 0);

            //we want to be able to edit the html for the menu to make them multi-instance
            var html = $('#inlineMenu').html().replace(/sheetInstance/g, "$.sheet.instance[" + I + "]");

            var menu = $(html);

            //The following is just so you get an idea of how to style cells
            menu.find('.colorPickerCell').colorPicker().change(function(){
                $.sheet.instance[I].cellChangeStyle('background-color', $(this).val());
            });

            menu.find('.colorPickerFont').colorPicker().change(function(){
                $.sheet.instance[I].cellChangeStyle('color', $(this).val());
            });

            menu.find('.colorPickers').children().eq(1).css('background-image', "url('/static/actions/spreadsheet/palette.png')");
            menu.find('.colorPickers').children().eq(3).css('background-image', "url('/static/actions/spreadsheet/palette_bg.png')");

            return menu;
        }


    $(document).ready(function(){
        console.log('pwal');
        $('.spreadsheet').sheet({
            title: "foinfoin",
//            urlGet: "/static/sheet.doc.html",
            urlGet: "content",
            urlMenu: "/static/sheet.menu.html",
            inlineMenu: inlineMenu($.sheet.instance),
//            urlSave: "save",
            autoFiller: true,
            });
    });
    ''']

    html = ''' <a target="_blank" href="http://visop-dev.com/lib/jquery.sheet/jquery.sheet.html#">Online help</a>

    <div class="spreadsheet" />

        <span id="inlineMenu" style="display: none;">
            <span>
                <a href="#" onclick="sheetInstance.controlFactory.addRow(); return false;" title="Insert Row After Selected">
                    <img alt="Insert Row After Selected" src="/static/actions/spreadsheet/sheet_row_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addRow(null, true); return false;" title="Insert Row Before Selected">
                    <img alt="Insert Row Before Selected" src="/static/actions/spreadsheet/sheet_row_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addRow(null, null, ':last'); return false;" title="Add Row At End">
                    <img alt="Add Row" src="/static/actions/spreadsheet/sheet_row_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addRowMulti(); return false;" title="Add Multi-Rows">
                    <img alt="Add Multi-Rows" src="/static/actions/spreadsheet/sheet_row_add_multi.png"/></a>
                <a href="#" onclick="sheetInstance.deleteRow(); return false;" title="Delete Row">
                    <img alt="Delete Row" src="/static/actions/spreadsheet/sheet_row_delete.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addColumn(); return false;" title="Insert Column After Selected">
                    <img alt="Insert Column After Selected" src="/static/actions/spreadsheet/sheet_col_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addColumn(null, true); return false;" title="Insert Column Before Selected">
                    <img alt="Insert Column Before Selected" src="/static/actions/spreadsheet/sheet_col_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addColumn(null, null, ':last'); return false;" title="Add Column At End">
                    <img alt="Add Column At End" src="/static/actions/spreadsheet/sheet_col_add.png"/></a>
                <a href="#" onclick="sheetInstance.controlFactory.addColumnMulti(); return false;" title="Insert Multi-Columns">
                    <img alt="Add Multi-Columns" src="/static/actions/spreadsheet/sheet_col_add_multi.png"/></a>
                <a href="#" onclick="sheetInstance.deleteColumn(); return false;" title="Delete Column">
                    <img alt="Delete Column" src="/static/actions/spreadsheet/sheet_col_delete.png"/></a>
                <a href="#" onclick="sheetInstance.getTdRange(null, sheetInstance.obj.formula().val()); return false;" title="Get Cell Range">
                    <img alt="Get Cell Range" src="/static/actions/spreadsheet/sheet_get_range.png"/></a>
                <a href="#" onclick="sheetInstance.s.fnSave(); return false;" title="Save Sheets">
                    <img alt="Save Sheet" src="/static/actions/spreadsheet/disk.png"/></a>
                <a href="#" onclick="sheetInstance.deleteSheet(); return false;" title="Delete Current Sheet">
                    <img alt="Delete Current Sheet" src="/static/actions/spreadsheet/table_delete.png"/></a>
                <a href="#" onclick="sheetInstance.calc(sheetInstance.i); return false;" title="Refresh Calculations">
                    <img alt="Refresh Calculations" src="/static/actions/spreadsheet/arrow_refresh.png"/></a>
                <a href="#" onclick="sheetInstance.cellFind(); return false;" title="Find">
                    <img alt="Find" src="/static/actions/spreadsheet/find.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleBold'); return false;" title="Bold">
                    <img alt="Bold" src="/static/actions/spreadsheet/text_bold.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleItalics'); return false;" title="Italic">
                    <img alt="Italic" src="/static/actions/spreadsheet/text_italic.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleUnderline', 'styleLineThrough'); return false;" title="Underline">
                    <img alt="Underline" src="/static/actions/spreadsheet/text_underline.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleLineThrough', 'styleUnderline'); return false;" title="Strikethrough">
                    <img alt="Strikethrough" src="/static/actions/spreadsheet/text_strikethrough.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleLeft', 'styleCenter styleRight'); return false;" title="Align Left">
                    <img alt="Align Left" src="/static/actions/spreadsheet/text_align_left.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleCenter', 'styleLeft styleRight'); return false;" title="Align Center">
                    <img alt="Align Center" src="/static/actions/spreadsheet/text_align_center.png"/></a>
                <a href="#" onclick="sheetInstance.cellStyleToggle('styleRight', 'styleLeft styleCenter'); return false;" title="Align Right">
                    <img alt="Align Right" src="/static/actions/spreadsheet/text_align_right.png"/></a>
                <a href="#" onclick="sheetInstance.fillUpOrDown(); return false;" title="Fill Down">
                    <img alt="Fill Down" src="/static/actions/spreadsheet/arrow_down.png"/></a>
                <a href="#" onclick="sheetInstance.fillUpOrDown(true); return false;" title="Fill Up">
                    <img alt="Fill Up" src="/static/actions/spreadsheet/arrow_up.png"/></a>
                <span class="colorPickers">
                    <input title="Foreground color" class="colorPickerFont" style="background-image: url('/static/actions/spreadsheet/palette.png') ! important; width: 16px; height: 16px;"/>
                    <input title="Background Color" class="colorPickerCell" style="background-image: url('/static/actions/spreadsheet/palette_bg.png') ! important; width: 16px; height: 16px;"/>
                </span>
                <a href="#" onclick="sheetInstance.obj.formula().val('=HYPERLINK(\'' + prompt('Enter Web Address', 'http://www.visop-dev.com/') + '\')').keydown(); return false;" title="HyperLink">
                    <img alt="Web Link" src="/static/actions/spreadsheet/page_link.png"/></a>
                <a href="#" onclick="sheetInstance.toggleFullScreen(); $('#lockedMenu').toggle(); return false;" title="Toggle Full Screen">
                    <img alt="Web Link" src="/static/actions/spreadsheet/arrow_out.png"/></a><!--<a href="#" onclick="insertAt('jSheetControls_formula', '~np~text~'+'/np~');return false;" title="Non-parsed"><img alt="Non-parsed" src="/static/actions/spreadsheet/noparse.png"/></a>-->
            </span>
        </span>
    '''

    css = [
            '/static/css/jquery.sheet.css',
            '/static/css/jquery.colorPicker.css',
            ] + drink.Page.css

    def save(self):
        data = drink.request.params['data']
        if data:
            self.content = '<table class="jSheet ui-widget-content" id="jSheet_0_0" border="1px" cellpadding="0" cellspacing="0" style="width: 1200px; ">'+data+'</table>'

