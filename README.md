# Glimpse: Intelligent Face Recognition Platform

## Overview

Glimpse is a web-based application that uses advanced face recognition technology to identify if a person from a solo photo appears in a group photo. The platform leverages MTCNN for face detection and FaceNet (VGGface2) for face recognition, providing accurate and efficient matching capabilities.

## Key Features

- **Dual Photo Analysis**: Upload a solo photo and a group photo for comparison
- **Advanced Face Recognition**: Uses MTCNN and FaceNet with VGGface2 weights
- **Visual Results**: Highlights matched faces in the group photo
- **Similarity Scoring**: Provides percentage-based similarity scores for matches
- **User-Friendly Interface**: Drag-and-drop functionality with responsive design
- **Privacy-Focused**: All processing happens on your server, no external API calls

## Technology Stack

- **Backend**: Python with Flask
- **Face Detection**: MTCNN
- **Face Recognition**: FaceNet (VGGface2) with PyTorch
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Image Processing**: OpenCV, Pillow

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/glimpse-face-recognition.git
   cd glimpse-face-recognition
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload Photos**:
   - Drag and drop or click to upload a solo photo (clear portrait of one person)
   - Drag and drop or click to upload a group photo (photo containing multiple people)

2. **Analyze**:
   - Click the "Analyze Photos" button
   - Wait for processing to complete (typically takes a few seconds)

3. **View Results**:
   - The system will display whether a match was found
   - Matched faces are highlighted with a green bounding box
   - Similarity percentage is shown for the best match

## Configuration

You can adjust the following parameters in `app.py`:

- `confidence_threshold`: Minimum confidence level for face detection (default: 0.8)
- `similarity_threshold`: Maximum cosine distance for a match (default: 0.6)

## Performance Notes

- The first run may take longer as models are loaded into memory
- Processing time depends on image size and number of faces detected
- For best results, use clear, well-lit photos with frontal faces

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## Acknowledgments

- Thanks to the developers of MTCNN and FaceNet for their excellent work
- Inspired by various open-source face recognition projects
- Built with Flask, PyTorch, and other amazing open-source tools
