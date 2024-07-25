from pytube import YouTube
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QGridLayout,
    QMessageBox
)

from PyQt6 import QtCore, QtGui
import yt_dlp as youtube_dl
from Worker import Worker

import os, sys


base_dir = os.path.dirname(__file__)
media_path = os.path.join(base_dir, 'Media')

class YoutubeDownloader(QWidget):
    download_slot = QtCore.pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.thread_pool = QtCore.QThreadPool()
        self.setMinimumSize(500, 200)
        self.setWindowTitle('ច្រៀងលេង')
        self.setObjectName('Body')
        self.setStyleSheet(
            '''
            #DownloadURL {height: 40px; border-radius: 10px}
            #DownloadButton {background: blue; border-radius: 10px; color: #fff; height: 40px; width: 100%}
            #ProgressBar {color: #fff; font-size: 18px; font-weight: bold}
            #LabelTitle {color: #fff; font-size: 12px;}
            '''
        )
        self.main_layout = QGridLayout()
        self.download_label = QLabel('តំណរ YouTube')
        self.main_layout.addWidget(self.download_label, 0, 0)
        
        self.download_url = QLineEdit('')
        self.download_url.setObjectName('DownloadURL')
        self.main_layout.addWidget(self.download_url, 0, 1)
        
        self.download_button = QPushButton('ទាញយក')
        self.download_button.setObjectName('DownloadButton')
        self.download_button.setDefault(True)
        self.main_layout.addWidget(self.download_button, 0, 2)
        self.download_button.clicked.connect(self.download)

        # Progress
        self.label_title = QLabel('')
        self.label_title.setObjectName('LabelTitle')
        self.label_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.label_title, 1, 0, 2, 3)
        self.progress = QLabel('')
        self.progress.setObjectName('ProgressBar')
        self.progress.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.progress, 3, 0, 2, 3)

        self.main_layout.setRowStretch(2, 1)

        self.setLayout(self.main_layout)

    def progress_hook(self, data):
        if data['status'] == 'downloading' and data['total_bytes'] > 0:
            fname = data['filename'].split('/')
            self.label_title.setText(fname[-1])
            value = data['downloaded_bytes'] / data['total_bytes'] * 100
            self.download_button.setDisabled(True)
            self.download_button.setText('Downloading...')
            self.progress.setText(f'{str(int(value))}%')

        if data['status'] == 'finished':
            self.progress.setText(f'{self.progress.text()}')
            # self.download_url.setText('')
            self.download_button.setText('Download')
            self.download_button.setEnabled(True)

        if os.path.exists(data['filename']):
            import time
            time.sleep(1)
            self.progress.setText('វីឌីអូបានទាញយករួចរាល់')
            self.download_slot.emit({'status': 'download_complete'})
            

    @QtCore.pyqtSlot()
    def download(self):
        w = Worker(self.do_download)
        self.thread_pool.start(w)
        
    def do_download(self):
        if not self.download_url.text() or (self.download_url.text() and not self.download_url.text().strip()): return
        try:
            opts = {
                'verbose': False,
                'format': 'best[ext=mp4]',
                'final_ext': 'mp4',
                'outtmpl': os.path.join(media_path, f'%(title)s.mp4'),
                'progress_hooks': [self.progress_hook]
            }
            with youtube_dl.YoutubeDL(opts) as yt:
                yt.download([self.download_url.text()])
        except (Exception) as e:
            dlg = QMessageBox()
            dlg.setWindowTitle('មិនស្គាល់')
            dlg.setText(f'តំណរហាក់ដូចជាមិនត្រឹមត្រូវ សូមពិនិត្យឡើងវិញ Error: {e}')
            dlg.exec()
            self.progress.setText('')
