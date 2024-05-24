from .image_process_tools import align_image, image_decoder
from .cells_extractor import CellExtractor
from .easyocr_proxy import EasyOcrProxy


class Reader:
    def __init__(self, **kwargs):
        self._cell_extractor = CellExtractor()
        self._model_proxy = EasyOcrProxy(**kwargs)

    def _mapping(self, recognize_list, cells_list):
        """
        Doing mapping results recognize on found coordinates cells table
        :param recognize_list: list, where each element is ([bbox_text], text, confident)
        :param cells_list: 2d list, where lines is columns, each column contains bbox table cell
        :return: list, where each line is column in recognize part table
        """
        def in_cell_check(val, cell, eps=5):
            a, b, c, d = val[0]
            x, y, w, h = cell
            return x - eps <= a[0] <= x + w + eps and y - eps - 5 <= a[1] <= y + h + eps

        # making an image of the table of read cells
        image_table = [[] for _ in range(len(cells_list))]

        # run by columns in columns list
        for idx_col, col in enumerate(cells_list):
            # run by elements in current column
            for idx_cell, cell in enumerate(col):
                #  find all read strings in current cell
                in_cell_list = [val[1] for idx, val in enumerate(recognize_list) if in_cell_check(val, cell) and val[2] >= 0.55]
                # if in current cell not found string
                if len(in_cell_list) == 0:
                    image_table[idx_col].append(None)
                else:
                    s = ' '.join(in_cell_list)
                    image_table[idx_col].append(s)

        #  making result table
        table = [[] for _ in range(len(cells_list))]
        for idx_col, col in enumerate(cells_list):
            for idx_cell, cell in enumerate(col):
                val = image_table[idx_col][idx_cell]
                table[idx_col].append(val)

        # table = [[] for _ in range(len(cells_list))]
        # for idx_col, col in enumerate(cells_list):
        #     for idx_cell, cell in enumerate(col):
        #         #  if in an image table in current cell no element, then read it separately
        #         if (val := image_table[idx_col][idx_cell]) is None:
        #             x, y, w, h = cell
        #             im = img[y: y + h, x:x + w]
        #             s = ' '.join(model.read_advance(im, detail=0, allowlist=self.allow_list_num, min_size=0))
        #             table[idx_col].append(s)
        #         else:
        #             table[idx_col].append(val)

        return table

    def _to_dict(self, table_like_list):
        d = {}
        for col in table_like_list:
            head = col[0]
            d[head] = col[1::]
        return d

    def read(self, img):
        if isinstance(img, str) or isinstance(img, bytes):
            img = image_decoder(img)
        img = align_image(img)
        recognize_list = self._model_proxy.read(img)
        cells_list = self._cell_extractor.extract_cells(img)
        # each line in list is column in source table
        table = self._mapping(recognize_list, cells_list)
        return self._to_dict(table)

