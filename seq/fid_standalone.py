#!/usr/bin/env python3
import sys
sys.path.append('../../marcos_client')
import numpy as np
import experiment as ex
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt_seq
from local_config import fpga_clk_freq_MHz

import pdb
st = pdb.set_trace


def fid(plot_rx=False, init_gpa=False,
             dbg_sc=0.5, # set to 0 to avoid 2nd RF debugging pulse, otherwise amp between 0 or 1
             lo_freq=0.1, # MHz
             rf_amp=1, # 1 = full-scale
             rf_duration=50,
             rf_tstart = 100,  # us
             tr_wait=100, # delay after end of RX before start of next TR
             rx_period=10/3,  # us, 3.333us, 300 kHz rate
             readout_duration=500
             ):

    ## All times are in the context of a single TR, starting at time 0

#    phase_amps = np.linspace(phase_amp, -phase_amp, trs)
    rf_tend = rf_tstart + rf_duration # us

    rx_tstart = rf_tend+tr_wait # us
    rx_tend = rx_tstart + readout_duration  # us

    tx_gate_pre = 2 # us, time to start the TX gate before the RF pulse begins
    tx_gate_post = 1 # us, time to keep the TX gate on after the RF pulse ends


    def fid_tr(tstart):
        rx_tcentre = (rx_tstart + rx_tend) / 2
        value_dict = {
            # second tx0 pulse purely for loopback debugging
            'tx0': ( np.array([rf_tstart, rf_tend,   rx_tcentre - 10, rx_tcentre + 10]) + tstart,
                     np.array([rf_amp,0,  dbg_sc*(1 + 0.5j),0]) ),
            'rx0_en': ( np.array([rx_tstart, rx_tend]) + tstart, np.array([1, 0]) ),
             'tx_gate': ( np.array([rf_tstart - tx_gate_pre, rf_tend + tx_gate_post]) + tstart, np.array([1, 0]) )
        }

        return value_dict

    expt = ex.Experiment(lo_freq=lo_freq, rx_t=rx_period, init_gpa=init_gpa)
    # gpa_fhdo_offset_time in microseconds; offset between channels to
    # avoid parallel updates (default update rate is 0.2 Msps, so
    # 1/0.2 = 5us, 5 / 3.1 gives the offset between channels; extra
    # 0.1 for a safety margin)

    tr_t = 0 # start the first TR at 20us
    expt.add_flodict( fid_tr( tr_t) )

#    expt.close_server(True)

    rxd, msgs = expt.run()

    # Plot pulses
    idict = expt._seq
    tx0_i_t, tx0_i_a = idict['tx0_i']
    tx0_q_t, tx0_q_a = idict['tx0_q']
    tx0_t = tx0_i_t / fpga_clk_freq_MHz
    tx0_y = (tx0_i_a + 1j * tx0_q_a)/32767
    # plt_seq.plot(tx0_t, tx0_y)
    # plt_seq.show()



    print(msgs)

    expt.__del__()

    if plot_rx:

        plt.plot( rxd['rx0'].real )
        plt.plot( rxd['rx0'].imag )
#        plt.plot( rxd['rx1'].real )
#        plt.plot( rxd['rx1'].imag )
        # plt.show()

    return rxd


if __name__ == "__main__":

#        for k in range(20):
#            print(k)
    rxds = []

    for k in range(100):
        rxd = fid(lo_freq=0.5, plot_rx=True, init_gpa=True, dbg_sc=0.5)
        rxds.append(rxd)

    plt.show()
