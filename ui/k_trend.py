from . import k, trend
from stock import name

NAME = 'k_trend'


class KWatch(k.Watch):
    x_text_offset = 0.2

    def plot_info(self):
        pass

    # 副圖
    def _sup_axes(self):
        return {
            'ma': MA(),
            'max_min': k.MaxMin(),
            'marker_date': k.MarkerDate(),
        }


class MA(k.MA):
    x_text_offset = 0.45


class TrendWatch(trend.Watch):
    x_text_offset = 0.2

    # 副圖
    def _sup_axes(self):
        return {
            name.AVG: trend.Avg(),
            'max_min_text': MaxMinText(),
        }


class MaxMinText(trend.MaxMinText):
    len = {
        3: 10,
        4: 20,
        5: 25,
        6: 30,
    }
