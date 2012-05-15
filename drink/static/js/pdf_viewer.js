pdf_doc = function() {
	this.cur_page = 1;
	this.cur_scale = 1.2;
	this.zoom_in = function() {
		this.cur_scale += 0.2;
		this.showPage(this.cur_page);
	};
	this.zoom_out = function() {
		this.cur_scale -= 0.2;
		this.showPage(this.cur_page);
	};
	this.prev = function() {
		if(this.cur_page > 1) {
			this.cur_page -= 1;
			this.showPage(this.cur_page);
		} 
	}; 
    this.next = function() {
    	if (this.cur_page < this.obj.numPages) {
    		this.cur_page += 1;
    		this.showPage(this.cur_page);
		}
    };
	this.showPage = function(num) {
	  // Using promise to fetch the page
	  this.obj.getPage(num).then(function(page) {
		var viewport = page.getViewport(this.cur_scale);

		//
		// Prepare canvas using PDF page dimensions
		//
		var canvas = document.getElementById('pdf-canvas');
		var context = canvas.getContext('2d');
		canvas.height = viewport.height;
		canvas.width = viewport.width;

		//
		// Render PDF page into canvas context
		//
		var renderContext = {
		  canvasContext: context,
		  viewport: viewport
		};
		page.render(renderContext);
	  });
	}
	return this;
}();

PDFJS.getDocument('raw').then(function(pdf) {
  pdf_doc.obj = pdf;
  pdf_doc.showPage(1);

});
