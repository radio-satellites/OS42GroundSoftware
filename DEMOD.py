#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Demodulator Spectrum View
# Author: ve3svf
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import gnuradio.lora_sdr as lora_sdr
import osmosdr
import time



from gnuradio import qtgui

class DEMOD(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Demodulator Spectrum View", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demodulator Spectrum View")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "DEMOD")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.sf = sf = 7
        self.bw = bw = 250000
        self.target_freq = target_freq = 434e6
        self.symbols_per_sec = symbols_per_sec = float(bw) / (2**sf)
        self.samp_rate = samp_rate = int(2.56e6)
        self.rfgain_slider = rfgain_slider = 36
        self.ifgain_slider = ifgain_slider = 23
        self.capture_freq = capture_freq = 434.0e6
        self.bitrate = bitrate = sf * (1 / (2**sf / float(bw)))
        self.bbgain_slider = bbgain_slider = 20

        ##################################################
        # Blocks
        ##################################################
        self._rfgain_slider_range = Range(0, 40, 1, 36, 200)
        self._rfgain_slider_win = RangeWidget(self._rfgain_slider_range, self.set_rfgain_slider, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rfgain_slider_win)
        self._ifgain_slider_range = Range(0, 40, 1, 23, 200)
        self._ifgain_slider_win = RangeWidget(self._ifgain_slider_range, self.set_ifgain_slider, "IF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ifgain_slider_win)
        self._bbgain_slider_range = Range(0, 40, 1, 20, 200)
        self._bbgain_slider_win = RangeWidget(self._bbgain_slider_range, self.set_bbgain_slider, "BB Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._bbgain_slider_win)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + "rtl_tcp=127.0.0.1:1234"
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(434e6, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(rfgain_slider, 0)
        self.rtlsdr_source_0.set_if_gain(ifgain_slider, 0)
        self.rtlsdr_source_0.set_bb_gain(bbgain_slider, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=25,
                decimation=32,
                taps=[],
                fractional_bw=0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.network_tcp_sink_0_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 3006,2)
        self.network_tcp_sink_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 2000,2)
        self.lora_rx_1 = lora_sdr.lora_sdr_lora_rx( bw=125000, cr=1, has_crc=True, impl_head=False, pay_len=255, samp_rate=int(2e6), sf=7, soft_decoding=True, ldro_mode=2, print_rx=[False,True])
        self.lora_rx_0 = lora_sdr.lora_sdr_lora_rx( bw=int(bw), cr=1, has_crc=True, impl_head=False, pay_len=255, samp_rate=int(2e6), sf=sf, soft_decoding=True, ldro_mode=2, print_rx=[False,True])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_correctiq_0 = blocks.correctiq()


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_correctiq_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.lora_rx_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.lora_rx_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.lora_rx_0, 0), (self.network_tcp_sink_0, 0))
        self.connect((self.lora_rx_1, 0), (self.network_tcp_sink_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_correctiq_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.rational_resampler_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "DEMOD")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.set_bitrate(self.sf * (1 / (2**self.sf / float(self.bw))))
        self.set_symbols_per_sec(float(self.bw) / (2**self.sf))

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_bitrate(self.sf * (1 / (2**self.sf / float(self.bw))))
        self.set_symbols_per_sec(float(self.bw) / (2**self.sf))

    def get_target_freq(self):
        return self.target_freq

    def set_target_freq(self, target_freq):
        self.target_freq = target_freq

    def get_symbols_per_sec(self):
        return self.symbols_per_sec

    def set_symbols_per_sec(self, symbols_per_sec):
        self.symbols_per_sec = symbols_per_sec

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_rfgain_slider(self):
        return self.rfgain_slider

    def set_rfgain_slider(self, rfgain_slider):
        self.rfgain_slider = rfgain_slider
        self.rtlsdr_source_0.set_gain(self.rfgain_slider, 0)

    def get_ifgain_slider(self):
        return self.ifgain_slider

    def set_ifgain_slider(self, ifgain_slider):
        self.ifgain_slider = ifgain_slider
        self.rtlsdr_source_0.set_if_gain(self.ifgain_slider, 0)

    def get_capture_freq(self):
        return self.capture_freq

    def set_capture_freq(self, capture_freq):
        self.capture_freq = capture_freq

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate

    def get_bbgain_slider(self):
        return self.bbgain_slider

    def set_bbgain_slider(self, bbgain_slider):
        self.bbgain_slider = bbgain_slider
        self.rtlsdr_source_0.set_bb_gain(self.bbgain_slider, 0)




def main(top_block_cls=DEMOD, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
