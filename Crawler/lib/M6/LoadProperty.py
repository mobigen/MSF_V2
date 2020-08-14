import json

class LoadProperty():
    def __init__(self):
        self._is_csv_dat = False
        self._is_unique_load = False
        self._unique_load_name = False
        self._use_zlib = False
        self._skip_rows = 0

    def set_csv_data(self, is_csv_dat=True):
        self._is_csv_dat = is_csv_dat

    def set_unique_load(self, unique_load_name, is_unique_load=True):
        self._is_unique_load = is_unique_load
        self._unique_load_name = unique_load_name

    def set_zlib(self, use_zlib=True):
        self._use_zlib = use_zlib

    def set_skip_rows(self, skip_rows):
        self._skip_rows = skip_rows

    def is_csv_dat(self):
        return self._is_csv_dat

    def is_unique_load(self):
        return self._is_unique_load

    def is_zlib(self):
        return self._use_zlib

    def get_skip_rows(self):
        return self._skip_rows

    def to_str(self):
        dump_data = {
            'is_csv_dat': self._is_csv_dat,
            'is_unique_load': self._is_unique_load,
            'unique_load_name': self._unique_load_name,
            'use_zlib': self._use_zlib,
            'skip_rows': self._skip_rows
        }

        return json.dumps(dump_data)

