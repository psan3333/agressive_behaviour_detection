import csv
import sys
import os
import cv2
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, \
    QMessageBox, QFileDialog, QSlider
from PyQt5.QtCore import Qt, QUrl, QEventLoop
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QImage, QPixmap

current_video_usage = 0

class VideoTrimmingWindow(QWidget):
    def __init__(self, video_path: str, folder_path: str, violence_or_not: str):
        global current_video_usage
        
        super().__init__()

        self.setWindowTitle("Video Trimming")
        self.setGeometry(200, 200, 800, 600)

        self.video_path = video_path
        self.folder_path = folder_path
        self.violence_or_not = violence_or_not

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
        self.btnClose = QPushButton("Close")
        self.btnClose.clicked.connect(self.close)

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

    def closeEvent(self, event):
        self.video_capture.release()
        event.accept()

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
        global current_video_usage

        if not self.editStartIndex.text().isdigit():
            start_index = 0
        else:
            start_index = int(self.editStartIndex.text())
        if not self.editEndIndex.text().isdigit():
            end_index = self.total_frames
        else:
            end_index = int(self.editEndIndex.text())

        fps = self.getFPS()

        start_time_ms = start_index * 1000 / fps
        end_time_ms = end_index * 1000 / fps

        video_capture = cv2.VideoCapture(self.video_path)

        csv_filename = 'file_with_time.csv'

        video_filename = os.path.basename(self.video_path)
        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['videopath', 'start_index', 'end_index'])
            writer.writerow([video_filename, start_index, end_index])

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        trimmed_video_path = os.path.join(self.folder_path, self.violence_or_not, f'{current_video_usage}_{os.path.basename(self.video_path)}')
        trimmed_video_writer = cv2.VideoWriter(trimmed_video_path, fourcc, fps, (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_index)

        while True:
            ret, frame = video_capture.read()
            if not ret or video_capture.get(cv2.CAP_PROP_POS_FRAMES) > end_index:
                break
            trimmed_video_writer.write(frame)

        current_video_usage += 1
        video_capture.release()
        trimmed_video_writer.release()
        self.slider.setValue(0)
        self.editStartIndex.setText('')
        self.editEndIndex.setText('')
        QMessageBox.information(self, "Information", "Video trimmed successfully.")


class PreviewWindow(QWidget):
    def __init__(self, video_path, folder_path):
        super().__init__()

        self.setWindowTitle("Video Trimming")
        self.setGeometry(200, 200, 800, 600)

        self.video_path = video_path
        self.folder_path = folder_path

        self.video_capture = cv2.VideoCapture(video_path)
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        self.video_duration_string = datetime.timedelta(seconds=round(self.total_frames / self.video_fps))

        self.frame_index = 0
        self.frame_time_string = datetime.timedelta(seconds=round(self.frame_index / self.video_fps))

        self.labelImage = QLabel()
        self.labelIndex = QLabel()
        self.labelCurrFrameTime = QLabel()
        self.labelVideoDuration = QLabel()
        self.labelVideoDuration.setText(f'Video duration: {self.video_duration_string}')

        self.btnPrevFrame = QPushButton("Previous Frame")
        self.btnPrevFrame.clicked.connect(self.prevFrame)
        self.btnNextFrame = QPushButton("Next Frame")
        self.btnNextFrame.clicked.connect(self.nextFrame)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.labelImage)
        self.layout.addWidget(self.labelIndex)
        self.layout.addWidget(self.labelCurrFrameTime)
        self.layout.addWidget(self.labelVideoDuration)
        self.layout.addWidget(self.btnPrevFrame)
        self.layout.addWidget(self.btnNextFrame)
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

    def closeEvent(self, event):
        self.video_capture.release()
        event.accept()

    def sliderValueChanged(self, value):
        self.frame_index = value
        self.frame_time_string = datetime.timedelta(seconds=round(self.frame_index / self.video_fps))
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
            self.labelIndex.setText(f"Index: {self.frame_index}")
            self.labelCurrFrameTime.setText(f'Current video time for current frame: {self.frame_time_string}')
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

        self.videoPreviewBtn = QPushButton("Frame Preview")
        self.videoPreviewBtn.clicked.connect(self.previewVideo)

        self.btnNext = QPushButton("Next Video")
        self.btnNext.clicked.connect(self.nextVideo)

        self.btnPrev = QPushButton("Previous Video")
        self.btnPrev.clicked.connect(self.prevVideo)

        self.btnViolence = QPushButton("Violence")
        self.btnViolence.clicked.connect(self.moveVideoToViolenceFolder)

        self.btnNotViolence = QPushButton("Not Violence")
        self.btnNotViolence.clicked.connect(self.moveVideoToNotViolenceFolder)

        self.btnDelete = QPushButton("Delete")
        self.btnDelete.clicked.connect(self.moveVideoToDeleteFolder)

        self.labelStatus = QLabel("Status: ")
        self.labelFile = QLabel("File: ")

        self.labelVideoDuration = QLabel()
        self.labelVideoDuration.setText('Video duration: 00:00:00')

        self.layoutControls = QHBoxLayout()
        self.layoutControls.addWidget(self.btnOpen)
        self.layoutControls.addWidget(self.btnPlay)
        self.layoutControls.addWidget(self.videoPreviewBtn)
        self.layoutControls.addWidget(self.btnNext)
        self.layoutControls.addWidget(self.btnPrev)
        self.layoutControls.addWidget(self.btnViolence)
        self.layoutControls.addWidget(self.btnNotViolence)
        self.layoutControls.addWidget(self.btnDelete)
        self.layoutControls.addWidget(self.labelStatus)
        self.layoutControls.addWidget(self.labelFile)
        self.layoutControls.addWidget(self.labelVideoDuration)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.videoWidget)
        self.layout.addLayout(self.layoutControls)

        self.setLayout(self.layout)

        self.videoFiles = []
        self.currentVideoIndex = 0
        self.folderSelected = False
        # self.trimming_window = VideoTrimmingWindow('', '', '')
        # self.preview_window = PreviewWindow('', '')

    def previewVideo(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            msg_box = QMessageBox()
            msg_box.setText("Do you want to preview the video?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            response = msg_box.exec_()
            
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "violence")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)

            if response == QMessageBox.Yes:
                video_path = self.videoFiles[self.currentVideoIndex]
                self.preview_window = PreviewWindow(video_path, os.path.dirname(video_path))
                self.preview_window.show()
                loop = QEventLoop()
                self.preview_window.destroyed.connect(loop.quit)
                loop.exec()
        else: 
            msg_box = QMessageBox()
            msg_box.setText("There is no video folder selected now!")
            response = msg_box.exec_()

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
                    video_capture = cv2.VideoCapture(self.videoFiles[self.currentVideoIndex])
                    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                    video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))
                    video_duration_string = datetime.timedelta(seconds=round(total_frames / video_fps))
                    self.labelVideoDuration.setText(f'Video duration: {video_duration_string}')
                    video_capture.release()
        else:
            QMessageBox.warning(self, "Warning", "Folder already selected.")

    def moveVideoToDeleteFolder(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            global current_video_usage
            current_video_usage = 0
            # self.trimming_window.close()
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "delete")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))
            os.remove(src_file)
            #os.rename(src_file, dst_file)
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
            self.folderSelected = False
            self.close()

    def nextVideo(self):
        global current_video_usage
        current_video_usage = 0
        if self.folderSelected:
            if self.currentVideoIndex < len(self.videoFiles) - 1:
                self.currentVideoIndex += 1
                self.labelFile.setText("File: " + os.path.basename(self.videoFiles[self.currentVideoIndex]))
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
                video_capture = cv2.VideoCapture(self.videoFiles[self.currentVideoIndex])
                total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))
                video_duration_string = datetime.timedelta(seconds=round(total_frames / video_fps))
                self.labelVideoDuration.setText(f'Video duration: {video_duration_string}')
                video_capture.release()
                self.playVideo()

    def prevVideo(self):
        global current_video_usage
        current_video_usage = 0
        if self.folderSelected:
            if self.currentVideoIndex > 0:
                self.currentVideoIndex -= 1
                self.labelFile.setText("File: " + os.path.basename(self.videoFiles[self.currentVideoIndex]))
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
                video_capture = cv2.VideoCapture(self.videoFiles[self.currentVideoIndex])
                total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))
                video_duration_string = datetime.timedelta(seconds=round(total_frames / video_fps))
                self.labelVideoDuration.setText(f'Video duration: {video_duration_string}')
                video_capture.release()
                self.playVideo()

    def moveVideoToNotViolenceFolder(self):
        if self.folderSelected and self.currentVideoIndex < len(self.videoFiles):
            msg_box = QMessageBox()
            msg_box.setText("Do you want to trim the video?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            response = msg_box.exec_()
            
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "notviolence")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)

            if response == QMessageBox.Yes:
                video_path = self.videoFiles[self.currentVideoIndex]
                self.trimming_window = VideoTrimmingWindow(video_path, os.path.dirname(video_path), "notviolence")
                self.trimming_window.show()
                loop = QEventLoop()
                self.trimming_window.destroyed.connect(loop.quit)
                loop.exec()
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
            elif response == QMessageBox.No:
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
            msg_box = QMessageBox()
            msg_box.setText("Do you want to trim the video?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            response = msg_box.exec_()
            
            src_file = self.videoFiles[self.currentVideoIndex]
            dst_folder = os.path.join(os.path.dirname(src_file), "violence")
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)

            if response == QMessageBox.Yes:
                video_path = self.videoFiles[self.currentVideoIndex]
                self.trimming_window = VideoTrimmingWindow(video_path, os.path.dirname(video_path), "violence")
                self.trimming_window.show()
                loop = QEventLoop()
                self.trimming_window.destroyed.connect(loop.quit)
                loop.exec()
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.videoFiles[self.currentVideoIndex])))
            elif response == QMessageBox.No:
                src_file = self.videoFiles[self.currentVideoIndex]
                dst_folder = os.path.join(os.path.dirname(src_file), "violence")
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                dst_file = os.path.join(dst_folder, os.path.basename(src_file))
                os.rename(src_file, dst_file)
                self.videoFiles.pop(self.currentVideoIndex)
                self.nextVideo()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
