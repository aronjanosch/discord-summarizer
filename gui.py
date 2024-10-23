import sys
import os
import signal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QLabel, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QProcess, Qt


class MeetingSummarizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meeting Summarizer")
        self.setFixedSize(800, 500)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Button layout
        self.button_layout = QHBoxLayout()
        layout.addLayout(self.button_layout)

        self.start_button = QPushButton("Start Recording")
        self.start_button.setToolTip("Start recording a meeting")
        self.start_button.clicked.connect(self.start_recording)
        self.button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setToolTip("Stop the ongoing recording")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        self.button_layout.addWidget(self.stop_button)

        self.summarize_button = QPushButton("Summarize")
        self.summarize_button.setToolTip("Summarize an existing audio recording")
        self.summarize_button.clicked.connect(self.summarize_recording)
        layout.addWidget(self.summarize_button)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Transcript section
        self.transcript_label = QLabel("Transcript:")
        layout.addWidget(self.transcript_label)

        self.transcript_edit = QTextEdit()
        self.transcript_edit.setReadOnly(True)
        layout.addWidget(self.transcript_edit)

        # Summary section
        self.summary_label = QLabel("Summary:")
        layout.addWidget(self.summary_label)

        self.summary_edit = QTextEdit()
        self.summary_edit.setReadOnly(True)
        layout.addWidget(self.summary_edit)

        # Process management
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def start_recording(self):
        output_filename, _ = QFileDialog.getSaveFileName(self, "Save Meeting Recording", filter="MP3 Files (*.mp3)")
        if not output_filename:
            return

        if not output_filename.endswith(".mp3"):
            output_filename += ".mp3"

        self.output_filename = output_filename
        self.process.start("python", ["cli.py", "record", self.output_filename])
        self.status_label.setText("Status: Recording...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        try:
            os.kill(self.process.processId(), signal.SIGINT)
            self.process.waitForFinished(-1)
            self.status_label.setText("Status: Recording stopped.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while stopping the recording: {e}")
        finally:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def summarize_recording(self):
        audio_filename, _ = QFileDialog.getOpenFileName(self, "Select Audio File", filter="MP3 Files (*.mp3)")
        if not audio_filename:
            return

        self.transcript_edit.clear()
        self.summary_edit.clear()
        self.process.start("python", ["cli.py", "summarize", audio_filename])
        self.status_label.setText("Status: Summarizing...")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        lines = data.strip().splitlines()

        summary_flag = False
        summary_lines = []

        for line in lines:
            if line.startswith("TRANSCRIPT:"):
                transcript = line[len("TRANSCRIPT:"):].strip()
                current_transcript = self.transcript_edit.toPlainText()
                self.transcript_edit.setPlainText(current_transcript + transcript)
            elif line.startswith("SUMMARY_START"):
                summary_flag = True
            elif line.startswith("SUMMARY_END"):
                summary_flag = False
                summary = "\n".join(summary_lines)
                current_summary = self.summary_edit.toPlainText()
                self.summary_edit.setPlainText(current_summary + summary)
                summary_lines = []  # Clear summary_lines for next summary
            elif summary_flag:
                summary_lines.append(line)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        QMessageBox.warning(self, "Warning", f"An error occurred: {data.strip()}")

    def process_finished(self):
        self.status_label.setText("Status: Ready")
        QMessageBox.information(self, "Info", "Process finished.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeetingSummarizer()
    window.show()
    sys.exit(app.exec_())
