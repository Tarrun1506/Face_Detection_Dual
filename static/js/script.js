// DOM Elements
const soloDropArea = document.getElementById('solo-drop-area');
const groupDropArea = document.getElementById('group-drop-area');
const soloInput = document.getElementById('solo-input');
const groupInput = document.getElementById('group-input');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const matchStatus = document.getElementById('match-status');
const resultImage = document.getElementById('result-image');
const matchDetails = document.getElementById('match-details');

// Form Data
let soloFile = null;
let groupFile = null;

// Setup drag & drop and file selection for Solo Photo
setupDragDrop(soloDropArea, soloInput, file => {
    soloFile = file;
    displayPreview(file, soloDropArea);
    validateForm();
});

// Setup drag & drop and file selection for Group Photo
setupDragDrop(groupDropArea, groupInput, file => {
    groupFile = file;
    displayPreview(file, groupDropArea);
    validateForm();
});

// Setup drag & drop functionality
function setupDragDrop(dropArea, fileInput, onFileSelected) {
    // Click to select file
    dropArea.addEventListener('click', () => fileInput.click());
    
    // Handle file selection
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            onFileSelected(fileInput.files[0]);
        }
    });
    
    // Drag & drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('highlight');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('highlight');
        }, false);
    });
    
    // Handle dropped files
    dropArea.addEventListener('drop', e => {
        if (e.dataTransfer.files.length) {
            onFileSelected(e.dataTransfer.files[0]);
        }
    }, false);
}

// Display image preview
function displayPreview(file, container) {
    const reader = new FileReader();
    reader.onload = e => {
        container.style.backgroundImage = `url(${e.target.result})`;
        
        // Hide default content
        const defaultContent = container.querySelector('.default-content');
        if (defaultContent) {
            defaultContent.classList.add('hidden');
        }
    };
    reader.readAsDataURL(file);
}

// Validate form to enable/disable analyze button
function validateForm() {
    analyzeBtn.disabled = !(soloFile && groupFile);
}

// Handle analyze button click
analyzeBtn.addEventListener('click', async () => {
    if (!(soloFile && groupFile)) return;
    
    // Show loading spinner
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    
    // Create form data
    const formData = new FormData();
    formData.append('solo_photo', soloFile);
    formData.append('group_photo', groupFile);
    
    try {
        // Send request to server
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Hide loading spinner
        loadingDiv.classList.add('hidden');
        
        // Display results
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.classList.add('hidden');
        alert('An error occurred during analysis. Please try again.');
    }
});

// Display analysis results
function displayResults(data) {
    resultsDiv.classList.remove('hidden');
    
    // Display match status
    if (data.error) {
        matchStatus.innerHTML = `<div class="error-message">Error: ${data.error}</div>`;
        return;
    }
    
    // Show match status
    if (data.match_found) {
        matchStatus.innerHTML = `
            <div class="success-message">
                <span class="bold">Match found!</span> The person from the solo photo was found in the group photo.
            </div>
        `;
    } else {
        matchStatus.innerHTML = `
            <div class="error-message">
                <span class="bold">No match found.</span> ${data.message}
            </div>
        `;
    }
    
    // Display result image with bounding box (only for matched face)
    if (data.result_image) {
        resultImage.src = data.result_image;
        document.getElementById('result-image-container').classList.remove('hidden');
    } else {
        document.getElementById('result-image-container').classList.add('hidden');
    }
    
    // Display match details - only show the best match if found
    if (data.results && data.results.length > 0) {
        let bestMatch = null;
        
        // Find the best match
        for (const result of data.results) {
            if (result.is_match) {
                bestMatch = result;
                break;
            }
        }
        
        if (bestMatch) {
            const similarityPercentage = bestMatch.similarity_percentage.toFixed(1);
            matchDetails.innerHTML = `
                <h3 class="match-details-title">Match Details:</h3>
                <div class="match-detail-box">
                    <div class="match-detail-row">
                        <span class="match-found">Found Match</span>
                        <span class="match-percentage">${similarityPercentage}% Similar</span>
                    </div>
                </div>
            `;
        } else {
            matchDetails.innerHTML = '';
        }
    } else {
        matchDetails.innerHTML = '';
    }
}