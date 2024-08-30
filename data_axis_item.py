import pyqtgraph as pg
import datetime

class DateAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):

        x = [datetime.fromtimestamp(value).strftime("%d/%m/%Y-%H:%M:%S") for value in values]
        time_list = [datetime.split('-')[1] for datetime in x]

        new_time_list = [t.split(':')[1] + ':' + t.split(':')[2] for t in time_list]

        return new_time_list
