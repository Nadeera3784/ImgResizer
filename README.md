# ImgResizer

ImgResizer is a PyQt5-based desktop application for batch resizing images. 

![Preview](https://raw.githubusercontent.com/Nadeera3784/ImgResizer/main/preview.png)

Key features include:

## Technical Specifications:
- Built with PyQt5 and Pillow libraries
- Multi-threaded processing for responsiveness
- Maintains aspect ratio during resizing
- Supports PNG, JPG, JPEG, GIF, and BMP formats

## Core Functionality:
- Multiple image selection
- Customizable max width/height dimensions
- Progress tracking
- Background processing
- Error handling with user notifications
- Output quality preservation (95% quality setting)

## UI Components:
- Image selection button with file count display
- Dimension input fields
- Destination folder selector
- Progress bar
- Conditional button enabling based on user input
- Clean, intuitive interface matching the reference design

The application is particularly useful for photographers, web developers, or anyone needing to batch process images while maintaining quality and aspect ratios.


## Installation

```sh
pip install PyQt5
pip install pillow
python app.py
```