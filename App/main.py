import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, \
    QMessageBox, QFileDialog, QSlider
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QImage, QPixmap



class VideoTrimmingWindow(QWidget):
    def __init__(self, video_path, folder_path):
        super().__init__()

        self.setWindowTitle("Video Trimming")
        self.setGeometry(200, 200, 800, 600)

        self.video_path = video_path
        self.folder_path = folder_path

        self.video_capture = cv2.VideoCapture(video_path)
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_index = 0

        self.labelImage = QLabel()
        self.labelIndex = QLabel()
        self.editStartIndex = QLineEdit()
        self.editEndIndex = QLineEdit()

        self.btnPrevFrame = QPushButton("Previous Frame")
        self.btnPrevFrame.clicked.connect(self.prevFrame)

        self.btnNextFrame = QPushButton("Next Frame")
        self.btnNextFrame.clicked.connect(self.nextFrame)

        self.btnTrim = QPushButton("Trim")
        self.btnTrim.clicked.connect(self.trimVideo)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.labelImage)
        self.layout.addWidget(self.labelIndex)
        self.layout.addWidget(self.btnPrevFrame)
        self.layout.addWidget(self.btnNextFrame)
        self.layout.addWidget(QLabel("Start Index:"))
        self.layout.addWidget(self.editStartIndex)
        self.layout.addWidget(QLabel("End Index:"))
        self.layout.addWidget(self.editEndIndex)
        self.layout.addWidget(self.btnTrim)
#
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.total_frames - 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.sliderValueChanged)
#

        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        self.displayFrame()

    def sliderValueChanged(self, value):
        self.frame_index = value
        self.displayFrame()
    def getFPS(self):
        return int(self.video_capture.get(cv2.CAP_PROP_FPS))

    def displayFrame(self):
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
        ret, frame = self.video_capture.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.labelImage.setPixmap(QPixmap.fromImage(q_image))

            self.labelIndex.setText("Index: {}".format(self.frame_index))
        else:
            self.video_capture.release()

    def prevFrame(self):
        if self.frame_index > 0:
            self.frame_index -= 1
            self.displayFrame()

    def nextFrame(self):
        if self.frame_index < self.total_frames - 1:
            self.frame_index += 1
            self.displayFrame()


    def trimVideo(self):
        start_index = int(self.editStartIndex.text())
        end_index = int(self.editEndIndex.text())

        fps = self.getFPS()

        start_time_ms = start_index * 1000 / fps
        end_time_ms = end_index * 1000 / fps

        video_capture = cv2.VideoCapture(self.video_path)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        trimmed_video_path = os.path.join(self.folder_path, "violence", os.path.basename(self.video_path))
        trimmed_video_writer = cv2.VideoWriter(trimmed_video_path, fourcc, fps, (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_index)

        while True:
            ret, frame = video_capture.read()
            if not ret or video_capture.get(cv2.CAP_PROP_POS_FRAMES) > end_index:
                break
            trimmed_video_writer.write(frame)

        video_capture.release()
        trimmed_video_writer.release()

        QMessageBox.information(self, "Information", "Video trimmed successfully.")

        self.close()


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.btnOpen = QPushButton("Open Folder")
        self.btnOpen.clicked.connect(self.openFolder)

        self.btnPlay = QPushButton("Play")
        self.btnPlay.clicked.connect(self.playVideo)

        self.btnNext = QPushButton("Next Video")
        self.btnNext.clicked.connect(self.nextVideo)

        self.btnPrev = QPushButton("Previous Video")
        self.btnPrev.clicked.connect(self.prevVideo)

        self.btnViolence = QPushButton("Violence")
        self.btnViolence.clicked.connect(self.openVideoTrimmingWindow)

        self.btnNotViolence = QPushButton("Not Violence")
        self.btnNotViolence.clicked.connect(self.moveVideoToNotViolenceFolder)

        self.btnDelete = QPushButton("Delete")
        self.btnDelete.clicked.connect(self.moveVideoToDeleteFolder)

        self.labelStatus = QLabel("Status: ")
        self.labelFile = QLabel("File: ")

        self.layoutControls = QHBoxLayout()
        self.layoutControls.addWidget(self.btnOpen)
        self.layoutControls.addWidget(self.btnPlay)
        self.layoutControls.addWidget(self.btnNext)
        self.layoutControls.addWidget(self.btnPrev)
        self.layoutControls.addWidget(self.btnViolence)
        self.layoutControls.addWidget(self.btnNotViolence)
        self.layoutControls.addWidget(self.btnDelete)
        self.layoutControls.addWidget(self.labelStatus)
        self.layoutControls.addWidget(self.labelFile)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.videoWidget)
        self.layout.addLayout(self.layoutControls)

        self.setLayout(self.layout)

        self.videoFiles = []
        self.currentVideoIndex = 0
        self.folderSelected = False


    def openFolder(self):
        if not self.folderSelected:
            folderPath = QFileDialog.getExistingDirectory(self, "Open Folder")
            if folderPath:
                self.videoFiles = [os.path.join(folderPath, file) for file in os.listdir(folderPath) if
                                   file.endswith((".mp4", ".avi", ".mkv"))]
                if not self.videoFiles:
                    QMessageBox.warning(self, "Warning", "No video files found in the selected folder.")
                else:
                    self.folderSelected = True
                    self.currentVideoIndex = 0
                    self.labelFile.setText("File: " + os.path.basename(self.videoFiles[self.currentVideoIndex]))
                    self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
        else:
            QMessageBox.warning(self, "Warning", "Folder already selected.")

    def moveVideoToDeleteFolder(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "delete")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))
            os.replace(src_file, dst_file)
            self.videoFiles.pop(self.currentVideoIndex)
            self.nextVideo()

    def playVideo(self):
        if not self.folderSelected:
            QMessageBox.warning(self, "Warning", "Please select a folder containing video files first.")
            return
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.btnPlay.setText("Play")
        else:
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            self.mediaPlayer.play()
            self.btnPlay.setText("Pause")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.nextVideo()
        elif event.key() == Qt.Key_Left:
            self.prevVideo()
        elif event.key() == Qt.Key_Right:
            self.nextVideo()
        elif event.key() == Qt.Key_Q and event.modifiers() & Qt.ControlModifier:
            self.close()

    def nextVideo(self):
        if self.folderSelected:
            if self.currentVideoIndex < len(self.videoFiles) - 1:
                self.currentVideoIndex += 1
                self.labelFile.setText("File: " + os.path.basename(self.videoFiles[self.currentVideoIndex]))
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
                self.playVideo()

    def prevVideo(self):
        if self.folderSelected:
            if self.currentVideoIndex > 0:
                self.currentVideoIndex -= 1
                self.labelFile.setText("File: " + os.path.basename(self.videoFiles[self.currentVideoIndex]))
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
                self.playVideo()

    def moveVideoToNotViolenceFolder(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "notviolence")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))
            os.rename(src_file, dst_file)
            self.videoFiles.pop(self.currentVideoIndex)
            self.nextVideo()

    def moveVideoToViolenceFolder(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "violence")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))
            os.rename(src_file, dst_file)
            self.videoFiles.pop(self.currentVideoIndex)
            self.nextVideo()

    def deleteVideo(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            src_file = self.videoFiles[self.currentVideoIndex]
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.stop()
            os.remove(src_file)
            self.videoFiles.pop(self.currentVideoIndex)
            self.nextVideo()

    def openVideoTrimmingWindow(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            msg_box = QMessageBox()
            msg_box.setText("Do you want to trim the video?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            response = msg_box.exec_()

            if response == QMessageBox.Yes:
                video_path = self.videoFiles[self.currentVideoIndex]
                self.trimming_window = VideoTrimmingWindow(video_path, os.path.dirname(video_path))
                self.trimming_window.show()
            else:
                self.moveVideoToViolenceFolder()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.showFullScreen()
    sys.exit(app.exec_())
