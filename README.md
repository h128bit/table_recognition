<h1>Table recognition</h1>

For work need install the poppler-utils: <a href="https://pypi.org/project/pdf2image/">About install.</a>

<h2>Service REST API</h2>
Service API allows get coordinates cells received table and recognized table in 
json format. <br>
Service can process raster images and multi-page PDF files.<br>
All files must be converted to base64 string before sending to service. <br>
Body all requests must look like <b>{data: b64str}</b><br>

<h3>API for images:</h3>
for get coordinates cells in table<br>
<code>POST: /controller/tablestruct/img</code><br>

<b>return</b>: json like {page: [col1, col2, ...]}<br>
    - where col_i corresponds column in table and look like [bbox1, bbox2, ...] <br>
    - where bbox_i it bounding box cell.

for get recognized table <br>
<code>POST: /controller/recognise/easyocr/img </code> <br>
<b>return</b>: json like {col_title1: [val1, val2, ...], col_title2: ...} <br>


<h3>API for PDF:</h3>
for get coordinates cells in table<br>
<code>POST: /controller/tablestruct/pdf</code><br>

<b>return</b>: json like {pages: [page1, page2, ...]}<br>
    - where page_i it [col1, col2, ...] <br>
    - where col_i corresponds column in table and look like [bbox1, bbox2, ...] <br>
    - where bbox_i it bounding box cell.

for get recognized table <br>
<code>POST: /controller/recognise/easyocr/pdf</code> <br>
<b>return</b>:: json like {tables: [tab1, tab2, ...], col_title2: ...} <br>
    - where tab_i it json like {col_title1: [val1, val2, ...], col_title2: ...} <br>

<h2>Reader API documentation</h2>

<img src="table_reader_diagram.png" alt="">
<br>
OCR module based on EasyOCR <a href="https://www.jaided.ai/easyocr/documentation/">Doc</a>.<br>

<b><u>CLASS: EasyOcrProxy(read_param, **kwarg):</u></b><br>
Create instance easyocr, defines set allowed characters: [0..9, a..z, A..Z, а..я, А..Я, -, '.', ',']<br>
<b>parameters:</b><br>
    - read_param: look <a href="https://www.jaided.ai/easyocr/documentation/">EasyOCR doc</a> (readtext method) <br>
    - **kwarg: model parameters, look <a href="https://www.jaided.ai/easyocr/documentation/">EasyOCR doc</a> (Reader) <br>
    <b>methods</b>:<br>
    <b>read(img):</b> img -- ndarray<br>
    return: list like [([bbox_coord], text, confidence), ...] where <br>
    - <i>bbox_coord</i> is bounding box recognized text<br>
    - <i>test</i> is recognized text<br>
    - <i>confidence</i> is value between 0 and 1 -- confidence model<br>
    <b>read_like_num(img):</b> img -- ndarray. Can read only numbers.<br>
    return: string -- number recognized from image.<br>

<b><u>CLASS: CellExtractor():</u></b><br>
Class for work with table structure.<br>
<b>methods:</b><br>
<b>get_table_grid(image):</b> image -- ndarray. IMPORTANT! Image must be aligned! Lines of table must be parallel image borders<br>
return: grid, contours, where<br>
    - grid is ndarray -- binary image of table<br>
    - contours is list, look cv2 <a href="https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0">doc</a>
    (find contours)<br>
<b>extract_cells(img)</b>: img -- ndarray, bytes, base64 string. IMPORTANT! Image must be aligned! Lines of table must be parallel image borders<br>
    return: list like [col1, col3, ...], where each col is list of bounding boxs cells in table<br>

<b><u>CLASS Reader(**kwargs):</u></b><br>
Main class, get image with table, extracting table structure and recognize her.<br>
<b>parameters:</b><br>
    - **kwarg: model parameters, look <a href="https://www.jaided.ai/easyocr/documentation/">EasyOCR doc</a> (Reader) <br>
<b>methods:</b><br>
<b>read(img):</b> img -- ndarray or string in base64. <br>
return: recognize table like dictionary {col_title1: [val1, val2, ...], col_title2: ...} <br>

    