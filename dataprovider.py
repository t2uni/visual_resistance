from PyQt5.QtCore import pyqtSignal, QObject
import time
import random
from threading import Thread


class DataProvider(QObject):
    """ Emits a Qt signal whenever a connection has been detected. 

    Call start() to begin listening for connection detection,
    stop() to terminate thread.

    Attributes:
        _listen_loop  Event loop to receive detection data
        _should_run  Control loop run time
    """

    def __init__(self):
        super().__init__()
        
        self._listen_thread = Thread(target=self._listen)
        self._should_run = False  # type: bool

    def start(self):
        self._should_run = True
        self._listen_thread.start()

    def stop(self):
        self._should_run = False
        self._listen_thread.join()
        
    def _listen(self):
        while self._should_run:
            # TODO: listen for signals from easy2point process, remove following dummy code
            time.sleep(2)
            
            first_connection = random.randint(1, 24)
            second_connection = first_connection
            while second_connection == first_connection:
                second_connection = random.randint(1, 24)
            self.connection_detected.emit(
                "{:02d}".format(first_connection),
                "{:02d}".format(second_connection)
            )
    
    # Arguments: name of contact on which a connection was detected; resistance value measured
    connection_detected = pyqtSignal(str, str)  # TODO: pass resistance value
