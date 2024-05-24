import numpy as np
import cv2
from scipy.stats import mode
from .image_process_tools import image_decoder


class CellExtractor:
    def __init__(self):
        None

    def _morph(self, img_bin: np.array,
               kernel: np.array,
               iterations: int = 3) -> np.array:
        # morph opening
        img_temp = cv2.erode(img_bin, kernel, iterations=iterations)
        img_lines = cv2.dilate(img_temp, kernel, iterations=iterations)
        return img_lines

    def _over_draw_boxes(self, img_bin: np.array) -> np.array:
        """
        strengthening the borders of table cells
        """
        lines = cv2.HoughLinesP(image=img_bin,
                                rho=1,
                                theta=np.pi / 180,
                                threshold=100,
                                minLineLength=100,
                                maxLineGap=50)

        for i in range(lines.shape[0]):
            cv2.line(img_bin,
                     (lines[i][0][0], lines[i][0][1]),
                     (lines[i][0][2], lines[i][0][3]),
                     (255, 255, 255),
                     2, cv2.LINE_AA)
        return img_bin

    def _get_boxes(self, bin_im: np.array, it: int = 1) -> np.array:
        """
        This method find vertical and horizontal line binary on image table,
        after strengthening the borders of table via morphological open
        """
        kernel_length = np.array(bin_im).shape[1] // 100

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))

        # find vertical lines on image
        bin_im_v = self._morph(bin_im, kernel=vertical_kernel, iterations=it)
        # find horizontal lines on image
        bin_im_h = self._morph(bin_im, kernel=horizontal_kernel, iterations=it)

        v = self._over_draw_boxes(bin_im_v)
        h = self._over_draw_boxes(bin_im_h)

        # get table grid
        boxes = cv2.add(v, h)

        return boxes

    def _get_cells(self,
                   contours: list,
                   min_w: int = 15,
                   min_h: int = 15) -> tuple:
        """
        This method filtering got contours,
        if size fined contour less then min_w * min_h it noise
        """
        cntr = []
        cells_list = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > min_w and h > min_h:
                # cropped cell
                cells_list.append((x, y, w, h))
                cntr.append(cnt)
        return cells_list, cntr

    def _get_columns(self,
                     cells_list: list,
                     epsilon: int = 20) -> list:
        """
        This method find all cells which are on the same line with +- error
        """

        cells_list.sort(key=lambda x: (x[0], x[1]))

        columns_list = []

        val = -1
        index = 0

        for cell in cells_list:
            x = cell[0]
            if val == -1:
                val = x
                columns_list.append([])
                columns_list[index].append(cell)
                continue
            if val - epsilon <= x <= val + epsilon:
                columns_list[index].append(cell)
            elif val < x:
                val = x
                columns_list.append([])
                index += 1
                columns_list[index].append(cell)

        res_list = []
        for col in columns_list:
            res_list.append(sorted(col, key=lambda x: x[1]))

        return res_list

    def _get_list_uniform_columns(self, list_col: list) -> list:
        """
        This method remove columns with a very small or a very small amount cells
        """
        lengths_col = [len(col) for col in list_col]
        m = mode(lengths_col)[0]

        new_col_list = []
        for col in list_col:
            if m - m / 2 <= len(col) <= m + m / 2:
                new_col_list.append(col)
        return new_col_list

    def _complete_table(self, columns_list: list) -> list:
        """
        This method refind cells if on last steps been find not all cells
        (note: in columns list cells was sorted, 0 cell in column it upper recognized cell on image)
        """
        new_columns_list = [[] for _ in range(len(columns_list))]
        cache = [[] for _ in range(len(columns_list))]

        # add to the end tuple with -1 so that the lengths columns are equal (need for numpy)
        def supplement(l, m):
            for i, c in enumerate(l):
                if (k := len(c)) < m:
                    l[i] = l[i] + [(-1, -1, -1, -1)] * (m - k)
            return l

        max_len_col = len(max(columns_list, key=len))
        columns_list = supplement(columns_list, max_len_col)

        # for columns slice
        columns_list = np.array(columns_list)

        for idx in range(max_len_col):
            slice_ = columns_list[:, idx]

            # get upper cell in the slice_
            _, up_y, _, h = min(
                list(filter(lambda x: x[0] != -1, slice_)),
                key=lambda x: x[1])  # upper cell
            eps = h // 2

            # i th element of slice match i th column
            for index, cell in enumerate(slice_):
                cell = tuple(cell)
                x, y, w, _ = cell
                # if the cell place on one line with the upper cell in the slice_, add her in new list
                if up_y <= y <= up_y + eps:
                    new_columns_list[index].append(cell)
                # if current cell locate on below the upper cell
                else:
                    # extract fit cell
                    cache_val = list(filter(lambda x: up_y <= x[1] <= up_y + eps, cache[index]))
                    # if in cache no fit cells
                    if len(cache_val) == 0:
                        # if current cell not (-1, -1, -1, -1) tuple,
                        # then get x, w from current cell and y, h from upper cell
                        # and make new cell from these properties cells
                        # current cell add to cache
                        if x != -1:
                            new_columns_list[index].append((x, up_y, w, h))
                            cache[index].append(cell)
                        # if current cell (-1, -1, -1, -1) tuple,
                        #  get x, w from 0 cell in [index] columns and y, h from upper cell
                        else:
                            x, _, w, _ = columns_list[index][0]  # get some cell
                            new_columns_list[index].append((x, up_y, w, h))
                    else:
                        # if fit cell was in cache, extract her
                        cache_val = tuple(cache_val[0])
                        new_columns_list[index].append(cache_val)
                        cache[index].remove(cache_val)

        return new_columns_list

    def get_table_grid(self, image: np.array) -> tuple:
        """
        This method find table grid via morphology open

        input image must be aligned!!!
        """

        img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bin_im = cv2.adaptiveThreshold(img_grey, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        # table grid
        grid = self._get_boxes(bin_im, it=5)

        contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return grid, contours

    def extract_cells(self, img) -> list:
        """
        :param img: numpy array or b64 string
        :return: list like [col1, col3, ...], where each col is bbox cell in table

        input image must be aligned!!!
        """
        if isinstance(img, str) or isinstance(img, bytes):
            img = image_decoder(img)

        _, contours = self.get_table_grid(img)

        bbox_list, _ = self._get_cells(contours)

        columns_list = self._get_columns(bbox_list)  # list of list with tuples (x, y, w, h) -- cells properties
        columns_list[0] = columns_list[0][1::]  # remove image of the table from list with cells

        # remove columns with small or large number cells
        columns_list = self._get_list_uniform_columns(columns_list)

        columns_list = self._complete_table(columns_list)
        return columns_list
