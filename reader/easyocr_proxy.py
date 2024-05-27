import easyocr


class EasyOcrProxy:
    def __init__(self, read_param=None, **kwargs):
        self._model = easyocr.Reader(lang_list=['ru', 'en'], **kwargs)
        self._allow_list_ru = [' ']
        self._allow_list_en = [' ']
        self._allow_list_num = ['-', '.', ',']

        for i in range(0, ord('я') - ord('а') + 1):
            self._allow_list_ru.append(chr(ord('а') + i))
            self._allow_list_ru.append(chr(ord('А') + i))
        for i in range(0, ord('z') - ord('a') + 1):
            self._allow_list_en.append(ord('a') + i)
            self._allow_list_en.append(ord('A') + i)
        self._allow_list_num.extend([str(i) for i in range(10)])

        if read_param is None:
            self._read_param = {'decoder': 'greedy',
                               'beamWidth': 5,
                               'batch_size': 1,
                               'workers': 0,
                               'detail': 1,
                               'paragraph': False,
                               'min_size': 10,
                               'rotation_info': None}
        else:
            if isinstance(read_param, dict):
                if 'allowlist' in read_param: read_param.pop('read_param', None)
                self._read_param = read_param
            else:
                raise RuntimeError(f'read_param must be dict not {type(read_param)}')

    def change_read_param(self, new_read_param):
        if isinstance(new_read_param, dict):
            if 'allowlist' in new_read_param: new_read_param.pop('read_param', None)
            self._read_param = new_read_param
        else:
            raise RuntimeError(f'read_param must be dict not {type(new_read_param)}')

    def get_read_param(self):
        return self._read_param

    def read(self, img):
        # several launches model needed for improved recognition results
        res_ru = self._model.readtext(img, allowlist=self._allow_list_ru, **self._read_param)
        res_en = self._model.readtext(img, allowlist=self._allow_list_en, **self._read_param)
        res_num = self._model.readtext(img, allowlist=self._allow_list_num, **self._read_param)

        # align lengths lists recognitions
        max_len_recognized_list = len(max(res_ru, res_num, res_en, key=len))
        res_ru.extend([None for _ in range(max_len_recognized_list - len(res_ru))])
        res_en.extend([None for _ in range(max_len_recognized_list - len(res_en))])
        res_num.extend([None for _ in range(max_len_recognized_list - len(res_num))])

        res = []
        for vals in zip(res_ru, res_en, res_num):
            # vals contain results recognitions model
            # each value vals is tuple: ([bbox_coord], text, confidence)
            vals = list(filter(lambda x: x is not None, vals))
            res.append(max(vals, key=lambda x: x[2]))
        return res

    def read_like_num(self, img):
        read_param = self._read_param.copy()
        read_param['detail'] = 0
        return self._model.readtext(img, allowlist=self._allow_list_num, **read_param)


