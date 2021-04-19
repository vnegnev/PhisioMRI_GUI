"""
Acquisition Manager
@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    19/06/2020

@summary:   Class for controlling the acquisition

@status:    Under development
@todo:      Subdivide "startAcquisition" routine into subroutines (modularity)

"""

import numpy as np
from PyQt5.QtCore import pyqtSlot
from plotview.spectrumplot import SpectrumPlot
from sequencemodes import defaultsequences
from sequencesnamespace import Namespace as nmpsc
from manager.acquisitionmanager import AcquisitionManager
from PyQt5.QtCore import QObject
from manager.datamanager import DataManager
from seq.radial import radial
from seq.gradEcho import grad_echo
from seq.turboSpinEcho import turbo_spin_echo

version_major = 0
version_minor = 0
version_debug = 8
version_full = (version_major << 16) | (version_minor << 8) | version_debug


class AcquisitionController(QObject):
    def __init__(self, parent=None, outputsection=None, sequencelist=None):
        super(AcquisitionController, self).__init__(parent)

        self.parent = parent
        self.outputsection = outputsection
        self.sequencelist = sequencelist
        self.acquisitionData = None

        parent.action_acquire.triggered.connect(self.startAcquisition)

    @pyqtSlot(bool)
    def startAcquisition(self):

        self.parent.clearPlotviewLayout()
        self.sequence = defaultsequences[self.sequencelist.getCurrentSequence()]
                
        if self.sequence.seq == 'R':
            self.sequence.plot_rx = True
            self.sequence.init_gpa = True
            self.rxd = radial(self.sequence)     
        elif self.sequence.seq == 'GE':
            self.sequence.plot_rx = True
            self.sequence.init_gpa = True
            self.rxd = grad_echo(self.sequence)   
        elif self.sequence.seq == 'TSE':
            self.sequence.plot_rx = True
            self.sequence.init_gpa = True
            self.sequence.rf_pi_duration=None, # us, rf pi pulse length  - if None then automatically gets set to 2 * rf_pi2_duration
            self.rxd = turbo_spin_echo(self.sequence)    
        
        dataobject: DataManager = DataManager(self.rxd, self.sequence.lo_freq, len(self.rxd))
        f_plotview = SpectrumPlot(dataobject.f_axis, dataobject.f_fftMagnitude, "frequency", "signal intensity")
        t_plotview = SpectrumPlot(dataobject.t_axis, dataobject.t_magnitude, "time", "signal intensity")
        #outputvalues = AcquisitionManager().getOutputParameterObject(dataobject, self.sequence.systemproperties)

        #self.outputsection.set_parameters(outputvalues)
        self.parent.plotview_layout.addWidget(t_plotview)
        self.parent.plotview_layout.addWidget(f_plotview)

        self.parent.rxd = self.rxd
        self.parent.lo_freq = self.sequence.lo_freq

    #    self.acquisitionData = dataobject

#        print("Operation: \n {}".format(operation))


# TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
