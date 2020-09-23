from . import k, trend

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
        }


class MA(k.MA):
    x_text_offset = 0.45


class TrendWatch(trend.Watch):
    x_text_offset = 0.2
