import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                           QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image

class ResizeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, source_files, dest_dir, max_width, max_height):
        super().__init__()
        self.source_files = source_files
        self.dest_dir = dest_dir
        self.max_width = max_width
        self.max_height = max_height

    def run(self):
        try:
            for i, source_path in enumerate(self.source_files):
                try:
                    filename = os.path.basename(source_path)
                    dest_path = os.path.join(self.dest_dir, filename)
                    
                    with Image.open(source_path) as img:
                        width_ratio = self.max_width / img.width
                        height_ratio = self.max_height / img.height
                        ratio = min(width_ratio, height_ratio)
                        
                        if ratio < 1:
                            new_size = (int(img.width * ratio), int(img.height * ratio))
                            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                            resized_img.save(dest_path, quality=95, optimize=True)
                        else:
                            img.save(dest_path)
                            
                    progress = int((i + 1) / len(self.source_files) * 100)
                    self.progress.emit(progress)
                
                except Exception as e:
                    self.error.emit(f"Error processing {filename}: {str(e)}")
                    
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class ImgResizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.source_files = []
        self.initUI()
        self.resize_btn.setEnabled(False)
        
    def initUI(self):
        self.setWindowTitle('ImgResizer')
        self.setFixedSize(400, 280)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        
        # Source files section
        source_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText('Selected images...')
        self.source_input.setReadOnly(True)
        browse_btn = QPushButton('Browse...')
        browse_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(self.source_input)
        source_layout.addWidget(browse_btn)
        
        # Dimensions section
        dim_layout = QHBoxLayout()
        self.width_input = QLineEdit('200')
        self.height_input = QLineEdit('200')
        width_label = QLabel('Max. Width')
        height_label = QLabel('Max. Height')
        dim_layout.addWidget(self.width_input)
        dim_layout.addWidget(width_label)
        dim_layout.addWidget(self.height_input)
        dim_layout.addWidget(height_label)
        
        # Destination folder section
        dest_layout = QHBoxLayout()
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText('Destination folder...')
        select_btn = QPushButton('Select...')
        select_btn.clicked.connect(self.browse_destination)
        dest_layout.addWidget(self.dest_input)
        dest_layout.addWidget(select_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton('Cancel')
        self.resize_btn = QPushButton('Resize')
        self.cancel_btn.clicked.connect(self.close)
        self.resize_btn.clicked.connect(self.start_resize)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.resize_btn)
        
        layout.addStretch()
        layout.addLayout(source_layout)
        layout.addLayout(dim_layout)
        layout.addLayout(dest_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
        
        self.resize_worker = None
        
    def browse_source(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if files:
            self.source_files = files
            self.source_input.setText(f"{len(files)} images selected")
            
    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.dest_input.setText(folder)
            self.resize_btn.setEnabled(True)
            
    def validate_inputs(self):
        if not self.source_files:
            QMessageBox.warning(self, "Error", "Please select images")
            return False
            
        if not self.dest_input.text():
            QMessageBox.warning(self, "Error", "Please select a destination folder")
            return False
            
        try:
            max_width = int(self.width_input.text())
            max_height = int(self.height_input.text())
            if max_width <= 0 or max_height <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid dimensions")
            return False
            
        return True
        
    def start_resize(self):
        if not self.validate_inputs():
            return
            
        self.resize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.resize_worker = ResizeWorker(
            self.source_files,
            self.dest_input.text(),
            int(self.width_input.text()),
            int(self.height_input.text())
        )
        
        self.resize_worker.progress.connect(self.update_progress)
        self.resize_worker.finished.connect(self.resize_completed)
        self.resize_worker.error.connect(self.show_error)
        self.resize_worker.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def resize_completed(self):
        self.resize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Success", "Image resizing completed!")
        
    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.resize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImgResizer()
    window.show()
    sys.exit(app.exec_())