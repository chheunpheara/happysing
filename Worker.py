from PyQt6 import QtCore


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs) -> None:
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs


    @QtCore.pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)