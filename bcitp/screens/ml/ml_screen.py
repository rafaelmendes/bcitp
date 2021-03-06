# DEPENDENCIES-------------------------
# Generic:

# Project's:
from bcitp.utils.standards import PATH_TO_SESSION, FONT_SIZE
from bcitp.signal_processing.approach import Approach

# KIVY modules:
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


######################################################################


class MlMenu(Screen):

    # layout
    def __init__(self, session_header, **kwargs):
        super(MlMenu, self).__init__(**kwargs)
        self.sh = session_header

    def change_to_calsettings(self, *args):
        self.manager.current = 'PreCalSettings'
        self.manager.transition.direction = 'left'

    def change_to_bci(self, *args):
        self.manager.current = 'BCIMenu'
        self.manager.transition.direction = 'right'

    def save_config(self):

        ids = self.ids

        self.sh.ml.epoch_start = ids.epoch_start.value
        self.sh.ml.epoch_end = ids.epoch_end.value
        self.sh.ml.nei = ids.csp_nei.value
        self.sh.ml.class_ids = map(int, ids.class_ids.value.split(' '))

        self.sh.ml.n_iter = ids.n_iter.value
        self.sh.ml.test_perc = ids.test_perc.value

        self.sh.ml.max_amp = ids.max_amp.value
        # self.sh.ml.max_mse = ids.max_mse.value

        # Dataprocessing settings

        self.sh.dp.buf_len = ids.buf_len.value
        self.sh.dp.f_low = ids.f_low.value
        self.sh.dp.f_high = ids.f_high.value
        self.sh.dp.f_order = ids.f_order.value

        if ':' in ids.channels.value:
            limits = map(int, ids.channels.value.split(':'))
            ch_idx = range(limits[0], limits[1])
        else:
            ch_idx = map(int, ids.channels.value.split(' '))

        self.sh.dp.channels = ch_idx

        self.sh.ml.flag = True
        self.sh.saveToPkl()

    def get_ml_model(self, *args):

        self.save_config()

        pup = popupMl(self.sh)

        popup = Popup(title='Machine Learning Results', content=pup,
                      size_hint=(None, None), size=(400, 200))

        popup.open()

    def update_settings(self):
        ids = self.ids

        ids.epoch_start.value = self.sh.ml.epoch_start
        ids.epoch_end.value = self.sh.ml.epoch_end
        ids.csp_nei.value = self.sh.ml.nei
        ids.class_ids.value = str(self.sh.ml.class_ids).replace(
            ',', '').replace('[', '').replace(']', '')

        ids.n_iter.value = self.sh.ml.n_iter
        ids.test_perc.value = self.sh.ml.test_perc

        ids.max_amp.value = self.sh.ml.max_amp
        # ids.max_mse.value = self.sh.ml.max_mse

        # Data processing Settings

        ids.buf_len.value = self.sh.dp.buf_len
        ids.f_low.value = self.sh.dp.f_low
        ids.f_high.value = self.sh.dp.f_high
        ids.f_order.value = self.sh.dp.f_order

        # not the best option but it works
        ids.channels.value = str(self.sh.dp.channels).replace(
            ',', '').replace('[', '').replace(']', '')


class popupMl(BoxLayout):

    def __init__(self, session_header, **kwargs):
        super(popupMl, self).__init__(**kwargs)

        sh = session_header

        ap = Approach()

        ap.define_approach(
            sh.acq.sample_rate,
            sh.dp.f_low,
            sh.dp.f_high,
            sh.dp.f_order,
            sh.ml.nei,
            sh.ml.class_ids,
            sh.ml.epoch_start,
            sh.ml.epoch_end
        )

        ap.set_cal_path(sh.cal.data_cal_path, sh.cal.events_cal_path)

        ap.set_valid_channels(sh.dp.channels)

        autoscore = ap.train_model()
        autoscore = round(autoscore, 3)

        crossvalscore = ap.cross_validate_model(sh.ml.n_iter, sh.ml.test_perc)
        crossvalscore = round(crossvalscore, 3)

        try:
            ap.set_val_path(sh.cal.data_val_path, sh.cal.events_val_path)
            valscore = ap.validate_model()
            valscore = round(valscore, 3)
            ap.accuracy = valscore
        except Exception as e:
            print(e)
            ap.accuracy = crossvalscore
            valscore = 'NA'

        ap.save_to_pkl(PATH_TO_SESSION + sh.info.name)

        self.orientation = 'vertical'

        autoBox = BoxLayout()
        l1 = Label(text='Self Val Acc: %', font_size=FONT_SIZE)
        l2 = Label(text=str(autoscore), font_size=FONT_SIZE)
        autoBox.add_widget(l1)
        autoBox.add_widget(l2)

        crossvalBox = BoxLayout()
        l3 = Label(text='Cross Val Acc: %', font_size=FONT_SIZE)
        l4 = Label(text=str(crossvalscore), font_size=FONT_SIZE)
        crossvalBox.add_widget(l3)
        crossvalBox.add_widget(l4)

        valBox = BoxLayout()
        l3 = Label(text=' Val Acc: %', font_size=FONT_SIZE)
        l4 = Label(text=str(valscore), font_size=FONT_SIZE)
        valBox.add_widget(l3)
        valBox.add_widget(l4)

        self.add_widget(autoBox)
        self.add_widget(valBox)
        self.add_widget(crossvalBox)
