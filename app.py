# app.py - Main Flask Application with only matched face highlighting
from flask import Flask, request, jsonify, render_template, url_for
import os
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
import base64
from PIL import Image
from mtcnn import MTCNN
from facenet_pytorch import InceptionResnetV1
from scipy.spatial.distance import cosine
from io import BytesIO
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize MTCNN & FaceNet
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
detector = MTCNN()
facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Tensor Transform
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((160, 160)),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def extract_faces(img_array, confidence_threshold=0.8):
    """Extract faces using MTCNN, keeping original image resolution."""
    if img_array is None:
        return [], []

    rgb_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_img)

    face_images, face_positions = [], []
    for face in faces:
        if face['confidence'] >= confidence_threshold:
            x, y, w, h = face['box']
            x1, y1, x2, y2 = max(0, x), max(0, y), min(rgb_img.shape[1], x + w), min(rgb_img.shape[0], y + h)
            face_img = rgb_img[y1:y2, x1:x2]
            if face_img.size > 0:
                face_images.append(face_img)
                face_positions.append((x1, y1, x2, y2))

    return face_images, face_positions

def extract_features(face_img):
    """Extract 512D FaceNet embedding with correct input processing."""
    face_img = Image.fromarray(face_img)
    face_tensor = transform(face_img).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = facenet(face_tensor).cpu().numpy()
    return embedding / np.linalg.norm(embedding)

def find_best_match(solo_img_array, group_img_array, confidence_threshold=0.8, similarity_threshold=0.6):
    """Match solo face in a group photo using Cosine Similarity."""
    
    solo_faces, solo_positions = extract_faces(solo_img_array, confidence_threshold)
    group_faces, group_positions = extract_faces(group_img_array, confidence_threshold)

    if not solo_faces or not group_faces:
        return {
            "match_found": False,
            "message": "No faces detected in one or both images",
            "results": []
        }

    solo_features = extract_features(solo_faces[0])
    
    results = []
    for i, group_face in enumerate(group_faces):
        group_features = extract_features(group_face)
        # For similarity, lower is better with cosine distance
        similarity_score = float(cosine(solo_features.flatten(), group_features.flatten()))
        
        # Convert to percentage (inverse the cosine distance)
        similarity_percentage = float((1 - similarity_score) * 100)
        
        match = bool(similarity_score < similarity_threshold)
        
        results.append({
            "face_index": int(i),
            "position": [int(x) for x in group_positions[i]],
            "similarity_score": similarity_score,
            "similarity_percentage": similarity_percentage,
            "is_match": match
        })
    
    # Sort by similarity (lowest cosine distance first)
    results.sort(key=lambda x: x["similarity_score"])
    
    best_match = results[0] if results else None
    match_found = best_match and best_match["is_match"] if best_match else False
    
    return {
        "match_found": bool(match_found),
        "message": "Analysis complete",
        "results": results
    }

def create_result_image(img_array, matches):
    """Create result image with only matched face bounding box."""
    result_img = img_array.copy()
    
    # Find the best match (if any)
    best_match = None
    for match in matches:
        if match["is_match"]:
            best_match = match
            break
    
    # If there's a match, draw only its bounding box
    if best_match:
        x1, y1, x2, y2 = best_match["position"]
        color = (0, 255, 0)  # Green for match
        
        # Draw rectangle for the matched face
        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
    
    return result_img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'solo_photo' not in request.files or 'group_photo' not in request.files:
        return jsonify({"error": "Both solo and group photos are required"}), 400
    
    try:
        # Read images
        solo_photo = request.files['solo_photo']
        group_photo = request.files['group_photo']
        
        # Convert to OpenCV format
        solo_img_data = np.frombuffer(solo_photo.read(), np.uint8)
        solo_img_array = cv2.imdecode(solo_img_data, cv2.IMREAD_COLOR)
        
        group_img_data = np.frombuffer(group_photo.read(), np.uint8)
        group_img_array = cv2.imdecode(group_img_data, cv2.IMREAD_COLOR)
        
        # Find matches
        match_results = find_best_match(
            solo_img_array, 
            group_img_array,
            confidence_threshold=0.8,
            similarity_threshold=0.6
        )
        
        # Create result image with only matched face bounding box
        if match_results["results"]:
            result_img = create_result_image(group_img_array, match_results["results"])
            
            # Convert result image to base64 for display
            _, buffer = cv2.imencode('.jpg', result_img)
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            
            match_results["result_image"] = f"data:image/jpeg;base64,{img_b64}"
        
        # Use the custom JSON encoder
        return app.response_class(
            response=json.dumps(match_results, cls=NumpyEncoder),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)