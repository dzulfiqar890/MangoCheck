/* script.js */

// Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const previewArea = document.getElementById('previewArea');
const loadingArea = document.getElementById('loadingArea');
const imagePreview = document.getElementById('imagePreview');

// Constants
const API_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:5000/api/predict' 
    : '/api/predict';
const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB

let selectedFile = null;

// Setup Event Listeners based on current page
function setupEvents() {
    // If we are on upload page
    if (dropzone && fileInput) {
        dropzone.addEventListener('click', (e) => {
            if (!e.target.closest('button')) {
                fileInput.click();
            }
        });

        fileInput.addEventListener('change', handleFileSelect);

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });
    }

    // If we are on result page
    if (document.querySelector('.page-hasil')) {
        loadResultsFromStorage();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return;

    // Validate file
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Format file tidak didukung. Harap unggah gambar JPG, PNG, atau WEBP.');
        fileInput.value = '';
        return;
    }

    if (file.size > MAX_FILE_SIZE) {
        alert('Ukuran file terlalu besar. Maksimal 4MB.');
        fileInput.value = '';
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        if (imagePreview) {
            imagePreview.src = e.target.result;
            // Save temporary image preview to session storage so we can show it on result page
            sessionStorage.setItem('mango_preview_image', e.target.result);
            
            if (uploadPlaceholder) uploadPlaceholder.classList.add('hidden');
            if (previewArea) previewArea.classList.remove('hidden');
        }
    };
    reader.readAsDataURL(file);
}

async function startAnalysisFromPreview() {
    if (!selectedFile) return;

    if (previewArea) previewArea.classList.add('hidden');
    if (loadingArea) loadingArea.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Store result in sessionStorage
            sessionStorage.setItem('mango_analysis_result', JSON.stringify(data.data));
            // Redirect to result page
            window.location.href = 'hasil.html';
        } else {
            throw new Error(data.error?.message || 'Terjadi kesalahan saat menganalisis gambar.');
        }
    } catch (error) {
        console.error('API Error:', error);
        alert(`Gagal menganalisis: ${error.message}\nPastikan backend sudah berjalan (python run_local.py).`);
        
        if (loadingArea) loadingArea.classList.add('hidden');
        if (previewArea) previewArea.classList.remove('hidden');
    }
}

function loadResultsFromStorage() {
    const resultString = sessionStorage.getItem('mango_analysis_result');
    const imageString = sessionStorage.getItem('mango_preview_image');
    
    if (!resultString) {
        // No result found, redirect back to upload
        window.location.href = 'upload.html';
        return;
    }

    const data = JSON.parse(resultString);
    const { prediction, recommendation } = data;
    
    // Set Image
    if (imageString) {
        document.getElementById('resultImage').src = imageString;
    }

    // Set Status Badge
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.className = 'status-badge ' + prediction.class_key;
    document.getElementById('statusText').innerText = prediction.label;
    
    const badgeIcon = statusBadge.querySelector('.badge-icon');
    if (prediction.class_key === 'ripe') badgeIcon.innerText = '✓';
    else if (prediction.class_key === 'rotten') badgeIcon.innerText = '⚠️';
    else badgeIcon.innerText = '⏳';
    
    // Format Confidence
    const pct = prediction.confidence_percentage.toFixed(2).replace('.', ',');
    document.getElementById('confidenceValue').innerText = pct + '%';
    
    const confidenceBar = document.getElementById('confidenceBar');
    setTimeout(() => {
        confidenceBar.style.width = prediction.confidence_percentage + '%';
        if (prediction.confidence_percentage < 70) {
            confidenceBar.style.backgroundColor = '#FFB300';
        } else {
            confidenceBar.style.backgroundColor = '#2E7D32';
        }
    }, 300);

    // Set Recommendation
    document.getElementById('actionRec').innerText = recommendation.message;

    // Handle low confidence warning
    const lowConfWarning = document.getElementById('lowConfidenceWarning');
    if (recommendation.status === 'manual_review_required') {
        lowConfWarning.classList.remove('hidden');
        if (recommendation.manual_review_note) {
            document.getElementById('lowConfidenceText').innerText = recommendation.manual_review_note;
        }
    } else {
        lowConfWarning.classList.add('hidden');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', setupEvents);
