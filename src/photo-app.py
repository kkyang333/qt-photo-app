# Import all the needed classes and modules
import os
import sys
from PySide6.QtWidgets import QLineEdit, QLabel, QPushButton, QApplication, QVBoxLayout, QDialog, QHBoxLayout, QSpinBox, QMessageBox, QFileDialog, QGridLayout
from PySide6.QtCore import QIODevice, QFile, QTextStream, Qt
from PySide6.QtGui import QPixmap, QImage

class Main(QDialog):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        # Set layouts for app
        self.layout = QVBoxLayout()
        self.layout2 = QGridLayout() # Grid layout is to display the photos
        self.numRemove = QSpinBox(self)  # This number is for the user to choose which picture they will remove
        self.photoListFileName = "QTPhotoFile.txt"
        self.tempPhotoListFileName = "QTPhotoFile.txt.tmp"
        self.read = QFile(self.photoListFileName) # File that stores all the photo directories
        self.maxRange = self.fileCount() # Variable that stores the number of pictures in the file
        self.numRemove.setRange(1, self.maxRange)

        # Create buttons
        self.removeButton = QPushButton("Remove")
        self.uploadButton = QPushButton("Upload Photo")        
        self.dialog = QFileDialog(self) # to upload the photo

        # Add widgets to the layout
        self.layout.addWidget(self.numRemove)
        self.layout.addWidget(self.removeButton)
        self.layout.addWidget(self.uploadButton)

        # Set dialog layout for the buttons and spinbox
        self.setLayout(self.layout)
        
        # Connect buttons to the respective functions
        self.uploadButton.clicked.connect(self.upload)
        self.removeButton.clicked.connect(self.remove)
        
        # Add layout2 for the grid
        self.layout.addLayout(self.layout2)

        #Call on the function to display the pictures
        self.display()      

    def display(self):
        '''
        This function is used to display all the pictures stored in the text file.
        '''
        self.count = 0 # Keeps count for the pictures
        self.row = self.count / 5 # Each row has 5 pictures
        self.column = 0
        
        if (self.read.open(QIODevice.ReadOnly)):
            i = QTextStream(self.read)
            # Reads through each line of the file
            while not(i.atEnd()):
                line = i.readLine()
                pictures = QLabel() # Used to display the photo
                number = QLabel() # Used to display the number of the photo
                number.setText(str(self.count + 1)) # The +1 is because the count starts at 0
                pixmap1 = QPixmap(str(line)) # Set the QPixmap to the current picture directory
                pixmap1 = pixmap1.scaled(100, 100, Qt.KeepAspectRatio) # Scales photo without ruining the aspect ratio
                pictures.setPixmap(pixmap1) 
                self.column = self.count % 5 # This is because each row has 5 pictures
                # The program alternates the rows between the number and the picture 
                self.row = 2 * int((self.count / 5)) + 1  
                self.layout2.addWidget(pictures, *(self.row+1, self.column)) # Adds the picture to the layout
                self.layout2.addWidget(number, *(self.row, self.column)) # Adds the number count to the grid layout
                self.count += 1

            self.read.close()

    def fileCount(self):
        '''
        This function counts the number of lines in the text file.
        '''
        count = 0 # Variable to store the number of lines
        if (self.read.open(QIODevice.ReadOnly)):
            i = QTextStream(self.read)
            while not(i.atEnd()):
                line = i.readLine()
                count += 1
            self.read.close()
        return count

    def upload(self):
        '''
        This function allows user to upload a picture
        '''
        # Set the filters to images only, so they don't upload something that can't be displayed
        filters = "Images (*.png *.xpm *.jpg *.jpeg *.gif)" 
        name1= self.dialog.getOpenFileName(
            filter = filters # Set the filters
            )

        if name1[0] !="": # To prevent errors, in the case that the user clicked cancel instead of selecting an image
            write = QFile(self.photoListFileName)
            if not(write.open(QIODevice.Append)):
                return
            # Add the new picture directory
            QTextStream(write)<<  str(name1[0]) << "\n" 
            write.close()

            label = QLabel()
            pixmap = QPixmap(name1[0]) # name1 is a tuple and the second element is  "All Files (*)"
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio) # Scales photo without ruining the aspect ratio
            number = QLabel()
            number.setText(str(self.count + 1)) # The +1 is because the count starts at 0
            label.setPixmap(pixmap)
            self.column = self.count % 5 # This is because each row has 5 pictures
            # The program alternates the rows between the number and the picture 
            self.row = 2 * int((self.count / 5)) + 1 
            self.layout2.addWidget(label, *(self.row + 1, self.column)) # Adds the picture to the layout
            self.layout2.addWidget(number, *(self.row, self.column)) # Adds the number count to the grid layout
            # Since the user uploaded a photo, add to the range of the number of photos there are
            self.maxRange += 1
            self.numRemove.setRange(1, self.maxRange)
            self.count += 1

    def remove(self):
        '''
        This function removes a line from the file
        '''        
        self.tempFile= QFile(self.tempPhotoListFileName) # File that stores all the photo directories

        count = 0 # Keeps track of the line

        # Picks the line that user wants to remove
        if (self.read.open(QIODevice.ReadWrite)):
            if(self.tempFile.open(QIODevice.ReadWrite)):

                i = QTextStream(self.read)
                while not(i.atEnd()):
                    count += 1
                    line = i.readLine()
                    if count != int(self.numRemove.text()): # If it's not the selected line add it to the temp
                        QTextStream(self.tempFile) << line

            self.tempFile.close()
            self.read.close()

        os.replace(self.tempPhotoListFileName, self.photoListFileName)

        # To make sure the number doesn't go negative (e.g. user clicks remove when there's nothing there)
        if self.maxRange > 0:
            # Change range of spinbox, as there has been one removed
            self.maxRange -= 1
            self.numRemove.setRange(1, self.maxRange)
        # Remove all the pictures to display them again
        for i in reversed(range(self.layout2.count())):
            self.layout2.itemAt(i).widget().deleteLater()
        self.display()
        
if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    main = Main()
    main.show()
    # Run the main Qt loop
    sys.exit(app.exec())