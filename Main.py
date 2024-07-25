from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QApplication,
    QGridLayout,
    QPushButton,
    QSlider,
    QLineEdit,
    QListWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSplitter
)

from PyQt6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput,
    QAudio,
)

from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6 import QtCore, QtGui
from Downloader import YoutubeDownloader
import os, sys


base_dir = os.path.dirname(__file__)
media_path = os.path.join(base_dir, 'Media')


def get_videos():
    from os import walk
    videos = []
    for (path, name, fname) in walk(media_path):
        for n in fname:
            videos.append(n)
    return videos


def reload_videos(playing_videos):
    from os import walk
    videos = []
    for (path, name, fname) in walk(media_path):
        for n in fname:
            if n in playing_videos: continue
            videos.append(n)
    return videos


class MainApp(QMainWindow):
    main_slot = QtCore.pyqtSignal(dict)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('ច្រៀងលេង')
        self.setStyleSheet(
            '''
            #DownloadButton {background: blue; color: #fff; width: 10px; height: 40px; border-radius: 5px}
            #SearchBox {background: #fff; border-radius: 5px; height: 30px; color: #000; font-size: 14px}
            #ControlButton {background: blue; color: #fff; font-size: 16px; height: 40px; border-radius: 5px}
            '''
        )
        self.player_position = 0
        self.videos = get_videos()
        self.old_contents = self.videos.copy()
        self.video_selected_row = 0
        self.setMinimumSize(800, 400)
        
        self.player = QMediaPlayer()
        self.main_layout = QHBoxLayout()
        self.left_vlayout = QVBoxLayout()
        self.control_layout = QHBoxLayout()
        self.audio_output = QAudioOutput()
        self.media_widget = QVideoWidget()
        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal)

        self.left_vlayout.addWidget(self.media_widget)
        if self.videos:
            self.source = QtCore.QUrl.fromLocalFile(f'{media_path}/{self.videos[0]}')
            self.player.setSource(self.source)
        self.player.mediaStatusChanged.connect(self.auto_play_video)

        self.player.setVideoOutput(self.media_widget)
        self.player.setAudioOutput(self.audio_output)

        self.left_vlayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

            
        self.slider.sliderMoved.connect(self.slider_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.left_vlayout.addWidget(self.slider)
        # Control
        self.play_button = QPushButton('ចាក់')
        self.play_button.setObjectName('ControlButton')
        self.control_layout.addWidget(self.play_button)

        self.pause_button = QPushButton('ផ្អាក')
        self.pause_button.setObjectName('ControlButton')
        self.control_layout.addWidget(self.pause_button)

        self.volume_slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.control_layout.addWidget(self.volume_slider)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setToolTip('Volume')
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        # Join layout
        self.left_vlayout.addLayout(self.control_layout)
        self.main_layout.addLayout(self.left_vlayout)

        self.right_vlayout = QVBoxLayout()
        # Content Manager
        self.download_button = QPushButton('ទាញពី YouTube')
        self.download_button.setObjectName('DownloadButton')
        self.right_vlayout.addWidget(self.download_button)
        yt = YoutubeDownloader()
        self.download_button.clicked.connect(lambda: yt.show())
        self.search = QLineEdit()
        self.search.setPlaceholderText('ស្វែងរកវីឌីអូ')
        self.search.setObjectName('SearchBox')
        self.right_vlayout.addWidget(self.search)
        self.search.textChanged.connect(self.searching)
        
        self.total_label = QLabel(f'សរុប: {str(len(self.videos))}')
        self.right_vlayout.addWidget(self.total_label)
        self.contents = QListWidget()
        self.contents.addItems(self.videos)
        self.right_vlayout.addWidget(self.contents)
        if self.videos:
            self.contents.item(self.video_selected_row).setSelected(True)
        self.contents.clicked.connect(self.select_video)
        self.contents.itemSelectionChanged.connect(self.select_video)

        self.main_layout.addLayout(self.right_vlayout)
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 1)

        # Control commander
        self.play_button.clicked.connect(self.play)
        # self.stop_button.clicked.connect(self.stop)
        self.pause_button.clicked.connect(self.pause)

        # Default play
        self.player.play()

        # Connect slot between widgets
        yt.download_slot.connect(self.get_signal)
        self.main_slot.connect(yt.download)
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def searching(self):
        keyword = self.search.text()
        filtered_contents = []
        for v in reload_videos([]):
            if v.startswith(keyword):
                filtered_contents.append(v)
        
        self.videos.clear()
        self.contents.clear()
        if len(filtered_contents) > 0:
            self.videos = filtered_contents
        else:
            self.videos = self.old_contents = reload_videos(self.videos)

        self.total_label.setText(f'សរុប: {len(self.videos)}')
        if not keyword:
            self.videos = self.old_contents = reload_videos([])

        if len(self.videos) > 0:
            self.video_selected_row = 0
            self.contents.addItems(self.videos)
            QtCore.QTimer.singleShot(1, lambda: self.set_local_source(f'{media_path}/{self.videos[self.video_selected_row]}'))
        else:
            self.stop()

    def slider_changed(self, pos):
        # self.slider.setValue(pos)
        self.player.setPosition(pos)


    def position_changed(self, pos):
        self.slider.setValue(pos)


    def duration_changed(self, duration):
        self.slider.setRange(0, duration)


    def play(self):
        self.player.play()


    def stop(self):
        self.player.stop()


    def pause(self):
        self.player.pause()


    def set_volume(self):
        volume = QAudio.convertVolume(
            self.volume_slider.value() * .1,
            QAudio.VolumeScale.LogarithmicVolumeScale,
            QAudio.VolumeScale.LinearVolumeScale
        )
        self.audio_output.setVolume(volume)


    def set_local_source(self, source):
        source = QtCore.QUrl.fromLocalFile(source)
        self.player.setSource(source)
        self.play()

    def refresh_video_list(self):
        new_videos = reload_videos(self.videos)
        if new_videos:
            self.videos.extend(new_videos)
            self.total_label.setText(f'សរុប: {len(self.videos)}')
            for v in new_videos:
                self.contents.addItem(v)

    def auto_play_video(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.refresh_video_list()
            self.video_selected_row += 1
            self.contents.setCurrentRow(self.video_selected_row)
            item = self.videos[self.video_selected_row]
            QtCore.QTimer.singleShot(1, lambda: self.set_local_source(f'{media_path}/{item}'))
            

    def select_video(self):
        self.refresh_video_list()
        if self.video_selected_row == self.contents.currentRow(): return
        self.video_selected_row = self.contents.currentRow()
        self.stop()
        if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            item = self.videos[self.video_selected_row]
            QtCore.QTimer.singleShot(1, lambda: self.set_local_source(f'{media_path}/{item}'))


    @QtCore.pyqtSlot(dict)
    def get_signal(self, data):
        if data['status'] == 'download_complete':
            self.refresh_video_list()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    app.exec()