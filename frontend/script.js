document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const audioInput = document.getElementById('audio-file');
    const selectedFileInfo = document.getElementById('selected-file-info');
    const fileNameSpan = document.getElementById('file-name');
    const btnRemove = document.getElementById('btn-remove');
    const btnUpload = document.getElementById('btn-upload');
    
    const uploadSection = document.getElementById('upload-section');
    const pasteSection = document.getElementById('paste-section');
    const btnProcessText = document.getElementById('btn-process-text');
    const manualTranscript = document.getElementById('manual-transcript');
    const statusCard = document.getElementById('status-card');
    const progressFill = document.getElementById('progress-bar-fill');
    
    // Status Steps
    const stepTranscribe = document.getElementById('step-transcribe');
    const stepSummarize = document.getElementById('step-summarize');
    const stepActions = document.getElementById('step-actions');
    const stepDecisions = document.getElementById('step-decisions');
    
    // Results DOM
    const resultsSection = document.getElementById('results-section');
    const resultTitle = document.getElementById('result-title');
    const resultSummary = document.getElementById('result-summary');
    const resultDecisions = document.getElementById('result-decisions');
    const resultActions = document.getElementById('result-actions');
    const resultTranscript = document.getElementById('result-transcript');
    const resultTranscriptWrapper = document.getElementById('result-transcript-wrapper');
    const btnToggleTranscript = document.getElementById('btn-toggle-transcript');

    let selectedFile = null;

    // --- Drag & Drop Handlers ---
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'dragend', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // --- File Input Handlers ---
    dropZone.addEventListener('click', (e) => {
        // Prevent click trigger loop if clicking inner elements like label/button
        if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
            audioInput.click();
        }
    });

    audioInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation(); // Avoid triggering dropZone click
        resetFileSelection();
    });

    function handleFileSelection(file) {
        // Basic type validation
        if (!file.type.startsWith('audio/') && !['.mp3', '.wav', '.m4a', '.ogg', '.flac'].some(ext => file.name.endsWith(ext))) {
            alert('Please select an audio file (MP3, WAV, M4A, OGG, or FLAC).');
            return;
        }

        selectedFile = file;
        fileNameSpan.textContent = `${file.name} (${formatBytes(file.size)})`;
        selectedFileInfo.style.display = 'flex';
        btnUpload.disabled = false;
    }

    function resetFileSelection() {
        selectedFile = null;
        audioInput.value = '';
        selectedFileInfo.style.display = 'none';
        btnUpload.disabled = true;
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // --- Upload and Processing ---
    btnUpload.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Reset step text in case it was modified by manual transcript processing
        stepTranscribe.textContent = 'Transcribing audio (Whisper)...';

        // Show status card, hide upload and paste sections
        uploadSection.style.display = 'none';
        pasteSection.style.display = 'none';
        statusCard.style.display = 'block';
        resultsSection.style.display = 'none';

        // Initialize status steps
        updateStepState(stepTranscribe, 'active', 15);
        updateStepState(stepSummarize, 'pending');
        updateStepState(stepActions, 'pending');
        updateStepState(stepDecisions, 'pending');

        const transcriptionModel = document.getElementById('transcription-model').value;
        const llmModel = document.getElementById('llm-model').value;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('transcription_model', transcriptionModel);
        formData.append('llm_model', llmModel);

        // Simulated progression since upload + processing takes a variable time
        let progress = 15;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 5;
                progressFill.style.width = `${progress}%`;
                
                // Transition state messages based on progress thresholds for interactive feel
                if (progress > 45 && stepSummarize.classList.contains('pending')) {
                    updateStepState(stepTranscribe, 'completed');
                    updateStepState(stepSummarize, 'active');
                }
                if (progress > 65 && stepActions.classList.contains('pending')) {
                    updateStepState(stepSummarize, 'completed');
                    updateStepState(stepActions, 'active');
                }
                if (progress > 80 && stepDecisions.classList.contains('pending')) {
                    updateStepState(stepActions, 'completed');
                    updateStepState(stepDecisions, 'active');
                }
            }
        }, 3000);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to process audio.');
            }

            const data = await response.json();
            
            // Instantly transition loading bar to completion
            progressFill.style.width = '100%';
            updateStepState(stepTranscribe, 'completed');
            updateStepState(stepSummarize, 'completed');
            updateStepState(stepActions, 'completed');
            updateStepState(stepDecisions, 'completed');

            setTimeout(() => {
                renderResults(data);
                statusCard.style.display = 'none';
                uploadSection.style.display = 'block';
                pasteSection.style.display = 'block';
                resetFileSelection();
            }, 600);

        } catch (error) {
            clearInterval(progressInterval);
            alert(`Error: ${error.message}`);
            statusCard.style.display = 'none';
            uploadSection.style.display = 'block';
            pasteSection.style.display = 'block';
        }
    });

    // --- Manual Transcript Processing ---
    btnProcessText.addEventListener('click', async () => {
        let text = manualTranscript.value.trim();

        if (!text) {
            // High-premium UX: if textarea is empty, prefill it with the sample text so they can test instantly!
            text = `Today we discussed Kubernetes deployment, cloud optimization, and CI/CD improvements.

Rahul will configure SSL by Friday.

Priya will complete Terraform setup before Monday.

The team approved AWS EKS for production deployment.`;
            manualTranscript.value = text;
        }

        // Show status card, hide upload and paste sections
        uploadSection.style.display = 'none';
        pasteSection.style.display = 'none';
        statusCard.style.display = 'block';
        resultsSection.style.display = 'none';

        // Update step status for manual input: skip transcription phase
        stepTranscribe.textContent = 'Transcribing audio (Whisper) - Skipped (Text provided)';
        updateStepState(stepTranscribe, 'completed', 25);
        updateStepState(stepSummarize, 'active');
        updateStepState(stepActions, 'pending');
        updateStepState(stepDecisions, 'pending');

        const llmModel = document.getElementById('llm-model').value;

        const formData = new FormData();
        formData.append('transcript_text', text);
        formData.append('llm_model', llmModel);

        // Simulated progression for manual text analysis (runs faster)
        let progress = 25;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 8;
                progressFill.style.width = `${progress}%`;
                
                if (progress > 50 && stepActions.classList.contains('pending')) {
                    updateStepState(stepSummarize, 'completed');
                    updateStepState(stepActions, 'active');
                }
                if (progress > 75 && stepDecisions.classList.contains('pending')) {
                    updateStepState(stepActions, 'completed');
                    updateStepState(stepDecisions, 'active');
                }
            }
        }, 1500);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to process transcript.');
            }

            const data = await response.json();
            
            // Transition loading bar to completion
            progressFill.style.width = '100%';
            updateStepState(stepTranscribe, 'completed');
            updateStepState(stepSummarize, 'completed');
            updateStepState(stepActions, 'completed');
            updateStepState(stepDecisions, 'completed');

            setTimeout(() => {
                renderResults(data);
                statusCard.style.display = 'none';
                uploadSection.style.display = 'block';
                pasteSection.style.display = 'block';
                manualTranscript.value = ''; // clear input after successful summary
                resetFileSelection();
            }, 600);

        } catch (error) {
            clearInterval(progressInterval);
            alert(`Error: ${error.message}`);
            statusCard.style.display = 'none';
            uploadSection.style.display = 'block';
            pasteSection.style.display = 'block';
        }
    });

    function updateStepState(element, state, overrideProgress) {
        element.className = state;
        if (overrideProgress !== undefined) {
            progressFill.style.width = `${overrideProgress}%`;
        }
    }

    // --- Render Results ---
    function renderResults(data) {
        resultTitle.textContent = data.title || "Meeting Notes Summary";
        
        // Render Summary
        resultSummary.innerHTML = formatAIResponse(data.summary);
        
        // Render Decisions
        if (data.decisions && data.decisions.trim() !== "") {
            const parsedDecisions = data.decisions.split('\n')
                .map(d => d.trim())
                .filter(d => d.length > 0)
                .map(d => {
                    // Strip list characters like -, *, 1. etc.
                    let cleanD = d.replace(/^[-*•\d+.\s]+/, '');
                    return `<li class="decision-item">${cleanD}</li>`;
                })
                .join('');
            resultDecisions.innerHTML = parsedDecisions ? `<ul>${parsedDecisions}</ul>` : `<p>${data.decisions}</p>`;
        } else {
            resultDecisions.innerHTML = `<p>No decisions explicitly recorded in this meeting.</p>`;
        }

        // Render Action Items
        resultActions.innerHTML = '';
        if (data.action_items && data.action_items.length > 0) {
            data.action_items.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'action-item';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `action-${index}`;
                
                const span = document.createElement('span');
                span.className = 'action-text';
                span.textContent = item;
                
                li.appendChild(checkbox);
                li.appendChild(span);
                resultActions.appendChild(li);
            });
        } else {
            resultActions.innerHTML = '<li class="action-item"><span class="action-text">No action items detected in this meeting.</span></li>';
        }

        // Render Transcript
        resultTranscript.textContent = data.transcript;
        
        // Toggle Transcript Collapsing
        resultTranscriptWrapper.className = 'card-content collapsed';
        btnToggleTranscript.textContent = 'Show';

        // Show Results section
        resultsSection.style.display = 'grid';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Toggle Transcript visibility
    btnToggleTranscript.addEventListener('click', () => {
        if (resultTranscriptWrapper.classList.contains('collapsed')) {
            resultTranscriptWrapper.classList.remove('collapsed');
            resultTranscriptWrapper.classList.add('expanded');
            btnToggleTranscript.textContent = 'Hide';
        } else {
            resultTranscriptWrapper.classList.remove('expanded');
            resultTranscriptWrapper.classList.add('collapsed');
            btnToggleTranscript.textContent = 'Show';
        }
    });

    function formatAIResponse(text) {
        if (!text) return '';
        // Basic line break and paragraph formatting
        return text.split('\n\n')
            .map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`)
            .join('');
    }
});
