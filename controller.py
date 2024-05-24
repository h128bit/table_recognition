from flask import Flask
from flask import request
from file_handler import FileHandler

app = Flask(__name__)
file_handler = FileHandler()


@app.route('/controller/tablestruct/pdf', methods=['POST'])
def get_table_structure_pdf():
    # file = request.form['data']
    file = request.form.get('data', False)
    print(type(file))
    pages = file_handler.extract_cells_from_pdf(file)
    d = {'pages': pages}
    return d


@app.route('/controller/tablestruct/img', methods=['POST'])
def get_table_struct_img():
    file = request.form['data']
    page = file_handler.extract_cells_from_img(file)
    d = {'page': page}
    return d


@app.route('/controller/recognise/easyocr/img', methods=['POST'])
def recognise_table_img():
    file = request.form['data']
    return file_handler.read_from_img(file)


@app.route('/controller/recognise/easyocr/pdf', methods=['POST'])
def recognise_table_pdf():
    file = request.form['data']
    tables = file_handler.read_from_pdf(file)
    d = {'tables': tables}
    return d


if __name__ == "__main__":
    app.run(debug=True)
