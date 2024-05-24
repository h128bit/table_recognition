from reader.image_process_tools import align_image, image_decoder
from reader.cells_extractor import CellExtractor
from reader.reader import Reader
import numpy as np
import pdf2image
import base64


class FileHandler:
    def __init__(self, **kwargs):
        self._cell_extractor = CellExtractor()
        self._reader = Reader(**kwargs)

    def _list_with_numpy_to_native(self, list_with_numpy):
        new_col_list = []
        for col in list_with_numpy:
            new_col_list.append([])
            for bbox in col:
                x, y, w, h = bbox
                new_col_list[-1].append((x.item(), y.item(), w.item(), h.item()))
        return new_col_list

    def extract_cells_from_img(self, file):
        file = image_decoder(file)
        file = align_image(file)
        columns_list = self._cell_extractor.extract_cells(file)
        return self._list_with_numpy_to_native(columns_list)

    def extract_cells_from_pdf(self, file):
        file = base64.b64decode(file)
        file = pdf2image.convert_from_bytes(file)

        res = []
        for page in file:
            page = align_image(np.array(page))
            columns_list = self._cell_extractor.extract_cells(page)
            res.append(self._list_with_numpy_to_native(columns_list))
        return res

    def read_from_img(self, file):
        return self._reader.read(file)

    def read_from_pdf(self, file):
        file = base64.b64decode(file)
        file = pdf2image.convert_from_bytes(file)

        res = []
        for page in file:
            res.append(self._cell_extractor.extract_cells(page))
        return res
