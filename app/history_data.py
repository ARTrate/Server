from enum import Enum


class HistoryDataType(Enum):
    BPM = 1
    RR = 2


class HistoryData:

    def __init__(self, type, id, data):
        if type not in [t for t in HistoryDataType]:
            raise ValueError("Unknown history data type")

        self._type = type
        self._id = id
        self._data = data

    def get_type(self):
        return self._type

    def get_id(self):
        return self._id

    def get_data(self):
        return self._data

