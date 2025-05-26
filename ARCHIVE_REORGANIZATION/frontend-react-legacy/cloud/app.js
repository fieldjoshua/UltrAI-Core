document.addEventListener('DOMContentLoaded', function () {
    // Elements
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const stepIndicator = document.getElementById('step-indicator');
    const steps = Array.from(document.querySelectorAll('.step'));
    const stepContents = Array.from(document.querySelectorAll('.step-content'));
    const prompt = document.getElementById('prompt');
    const promptError = document.getElementById('prompt-error');
    const backendUrlSelect = document.getElementById('backend-url');
    const testBackendBtn = document.getElementById('test-backend');
    const envIndicator = document.getElementById('env-indicator');
    const debugPanel = document.getElementById('debug-panel');
    const debugInfo = document.getElementById('debug-info');

    // State
    let currentStep = 1;
    let totalSteps = steps.length;
    let selectedModels = [];
    let selectedAnalysisType = null;
    let selectedAlacarteOptions = [];
    let selectedOutputFormat = null;
    let modelsLoaded = false;
    let analysisTypesLoaded = false;
    let alacarteOptionsLoaded = false;
    let outputFormatsLoaded = false;

    // Get backend URL
    function getBackendUrl() {
        return backendUrlSelect.value;
    }

    // Debug Logger
    function logDebug(message) {
        console.log(message);
        const logItem = document.createElement('div');
        logItem.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        debugInfo.appendChild(logItem);
        debugPanel.scrollTop = debugPanel.scrollHeight;
    }

    // Initialize the app
    function init() {
        // Set environment indicator
        if (window.location.hostname.includes('localhost') || window.location.hostname.includes('127.0.0.1')) {
            envIndicator.textContent = 'LOCAL';
            envIndicator.style.backgroundColor = 'var(--success)';
        } else {
            envIndicator.textContent = 'CLOUD';
            envIndicator.style.backgroundColor = 'var(--info)';
        }

        // Enable debug panel with ctrl+alt+d
        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.altKey && e.key === 'd') {
                debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
                logDebug('Debug panel toggled');
            }
        });

        updateStepIndicator();
        fetchModels();
        fetchAnalysisTypes();
        fetchAlacarteOptions();
        fetchOutputFormats();
    }

    // Navigation functions
    function goToStep(step) {
        if (step < 1 || step > totalSteps) return;

        // Validate current step before proceeding
        if (step > currentStep && !validateCurrentStep()) {
            return;
        }

        // Update current step
        currentStep = step;
        updateStepIndicator();
        updateStepContent();
        updateButtons();

        // If it's the models step and models haven't been loaded yet, load them
        if (currentStep === 3 && !modelsLoaded) {
            fetchModels();
        }

        // If it's the analysis types step and they haven't been loaded yet, load them
        if (currentStep === 4 && !analysisTypesLoaded) {
            fetchAnalysisTypes();
        }

        // If it's the a la carte options step and they haven't been loaded yet, load them
        if (currentStep === 5 && !alacarteOptionsLoaded) {
            fetchAlacarteOptions();
        }

        // If it's the output formats step and they haven't been loaded yet, load them
        if (currentStep === 6 && !outputFormatsLoaded) {
            fetchOutputFormats();
        }

        // If it's the results step, start processing
        if (currentStep === 7) {
            startProcessing();
        }
    }

    function validateCurrentStep() {
        switch (currentStep) {
            case 1:
                if (!prompt.value.trim()) {
                    promptError.classList.remove('hidden');
                    return false;
                }
                promptError.classList.add('hidden');
                return true;
            case 3:
                if (selectedModels.length === 0) {
                    document.getElementById('models-error').classList.remove('hidden');
                    return false;
                }
                document.getElementById('models-error').classList.add('hidden');
                return true;
            default:
                return true;
        }
    }

    function updateStepIndicator() {
        steps.forEach((step, index) => {
            const stepNumber = index + 1;
            if (stepNumber === currentStep) {
                step.classList.add('active');
                step.classList.remove('completed');
            } else if (stepNumber < currentStep) {
                step.classList.add('completed');
                step.classList.remove('active');
            } else {
                step.classList.remove('active', 'completed');
            }
        });
    }

    function updateStepContent() {
        stepContents.forEach((content, index) => {
            const stepNumber = index + 1;
            if (stepNumber === currentStep) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    function updateButtons() {
        prevBtn.disabled = currentStep === 1;

        if (currentStep === totalSteps) {
            nextBtn.textContent = 'Restart';
        } else {
            nextBtn.textContent = 'Next';
        }
    }

    // API functions
    async function fetchModels() {
        try {
            document.getElementById('models-loading').textContent = 'Loading models...';
            logDebug('Fetching models...');

            const response = await fetch(`${getBackendUrl()}/api/models`);
            if (!response.ok) throw new Error('Failed to fetch models');

            const models = await response.json();
            logDebug(`Fetched ${models.length} models`);

            renderModels(models);
            modelsLoaded = true;
        } catch (error) {
            logDebug(`Error fetching models: ${error.message}`);
            document.getElementById('models-loading').textContent = 'Error loading models. Please try again.';
        }
    }

    function renderModels(models) {
        const container = document.getElementById('models-container');
        container.innerHTML = '';

        models.forEach(model => {
            const modelCard = document.createElement('div');
            modelCard.className = 'model-card';
            modelCard.dataset.modelId = model.id;

            modelCard.innerHTML = `
                <div class="model-header">
                    <div class="model-name">${model.name}</div>
                    <div class="model-provider">${model.provider}</div>
                </div>
                <div class="model-description">${model.description}</div>
            `;

            modelCard.addEventListener('click', () => {
                const isSelected = modelCard.classList.toggle('selected');

                if (isSelected) {
                    selectedModels.push(model.id);
                } else {
                    selectedModels = selectedModels.filter(id => id !== model.id);
                }

                logDebug(`Selected models: ${selectedModels.join(', ')}`);
            });

            container.appendChild(modelCard);
        });
    }

    async function fetchAnalysisTypes() {
        try {
            document.getElementById('analysis-types-loading').textContent = 'Loading analysis types...';
            logDebug('Fetching analysis types...');

            const response = await fetch(`${getBackendUrl()}/api/analysis-types`);
            if (!response.ok) throw new Error('Failed to fetch analysis types');

            const analysisTypes = await response.json();
            logDebug(`Fetched ${analysisTypes.length} analysis types`);

            renderAnalysisTypes(analysisTypes);
            analysisTypesLoaded = true;
        } catch (error) {
            logDebug(`Error fetching analysis types: ${error.message}`);
            document.getElementById('analysis-types-loading').textContent = 'Error loading analysis types. Please try again.';
        }
    }

    function renderAnalysisTypes(analysisTypes) {
        const container = document.getElementById('analysis-types-container');
        container.innerHTML = '';

        analysisTypes.forEach(type => {
            const radioItem = document.createElement('div');
            radioItem.className = 'radio-item';

            radioItem.innerHTML = `
                <input type="radio" id="analysis-type-${type.id}" name="analysis-type" value="${type.id}">
                <label for="analysis-type-${type.id}">
                    <strong>${type.name}</strong>: ${type.description}
                </label>
            `;

            const radio = radioItem.querySelector('input');
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    selectedAnalysisType = type.id;
                    logDebug(`Selected analysis type: ${selectedAnalysisType}`);
                }
            });

            container.appendChild(radioItem);
        });

        // Select the first item by default
        if (analysisTypes.length > 0) {
            const firstRadio = container.querySelector('input');
            firstRadio.checked = true;
            selectedAnalysisType = analysisTypes[0].id;
        }
    }

    async function fetchAlacarteOptions() {
        try {
            document.getElementById('alacarte-options-loading').textContent = 'Loading options...';
            logDebug('Fetching a la carte options...');

            const response = await fetch(`${getBackendUrl()}/api/alacarte-options`);
            if (!response.ok) throw new Error('Failed to fetch a la carte options');

            const options = await response.json();
            logDebug(`Fetched ${options.length} a la carte options`);

            renderAlacarteOptions(options);
            alacarteOptionsLoaded = true;
        } catch (error) {
            logDebug(`Error fetching a la carte options: ${error.message}`);
            document.getElementById('alacarte-options-loading').textContent = 'Error loading options. Please try again.';
        }
    }

    function renderAlacarteOptions(options) {
        const container = document.getElementById('alacarte-options-container');
        container.innerHTML = '';

        options.forEach(option => {
            const checkboxItem = document.createElement('div');
            checkboxItem.className = 'checkbox-item';

            checkboxItem.innerHTML = `
                <input type="checkbox" id="option-${option.id}" value="${option.id}">
                <label for="option-${option.id}">
                    <strong>${option.name}</strong>: ${option.description}
                </label>
            `;

            const checkbox = checkboxItem.querySelector('input');
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    selectedAlacarteOptions.push(option.id);
                } else {
                    selectedAlacarteOptions = selectedAlacarteOptions.filter(id => id !== option.id);
                }

                logDebug(`Selected a la carte options: ${selectedAlacarteOptions.join(', ')}`);
            });

            container.appendChild(checkboxItem);
        });
    }

    async function fetchOutputFormats() {
        try {
            document.getElementById('output-formats-loading').textContent = 'Loading output formats...';
            logDebug('Fetching output formats...');

            const response = await fetch(`${getBackendUrl()}/api/output-formats`);
            if (!response.ok) throw new Error('Failed to fetch output formats');

            const formats = await response.json();
            logDebug(`Fetched ${formats.length} output formats`);

            renderOutputFormats(formats);
            outputFormatsLoaded = true;
        } catch (error) {
            logDebug(`Error fetching output formats: ${error.message}`);
            document.getElementById('output-formats-loading').textContent = 'Error loading output formats. Please try again.';
        }
    }

    function renderOutputFormats(formats) {
        const container = document.getElementById('output-formats-container');
        container.innerHTML = '';

        formats.forEach(format => {
            const radioItem = document.createElement('div');
            radioItem.className = 'radio-item';

            radioItem.innerHTML = `
                <input type="radio" id="format-${format.id}" name="output-format" value="${format.id}">
                <label for="format-${format.id}">
                    <strong>${format.name}</strong>: ${format.description}
                </label>
            `;

            const radio = radioItem.querySelector('input');
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    selectedOutputFormat = format.id;
                    logDebug(`Selected output format: ${selectedOutputFormat}`);
                }
            });

            container.appendChild(radioItem);
        });

        // Select the first item by default
        if (formats.length > 0) {
            const firstRadio = container.querySelector('input');
            firstRadio.checked = true;
            selectedOutputFormat = formats[0].id;
        }
    }

    function startProcessing() {
        logDebug('Starting processing...');

        // Reset the progress and results
        const progressFill = document.getElementById('progress-fill');
        const status = document.getElementById('status');
        const resultsContainer = document.getElementById('results-container');

        progressFill.style.width = '0%';
        status.textContent = 'Processing your request...';
        resultsContainer.classList.add('hidden');
        resultsContainer.innerHTML = '';

        // Gather the request parameters
        const requestData = {
            prompt: prompt.value.trim(),
            models: selectedModels,
            analysisType: selectedAnalysisType,
            alacarteOptions: selectedAlacarteOptions,
            outputFormat: selectedOutputFormat
        };

        logDebug(`Request data: ${JSON.stringify(requestData)}`);

        // Simulate progress for now
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            progressFill.style.width = `${progress}%`;

            if (progress >= 100) {
                clearInterval(progressInterval);
                status.textContent = 'Analysis complete!';
                showResults('This is a simulated result. In production, this would be the output from the backend API.');
            }
        }, 500);

        // In a real implementation, you would call the backend API here
        // processRequest(requestData);
    }

    async function processRequest(requestData) {
        try {
            logDebug('Sending request to backend...');

            const response = await fetch(`${getBackendUrl()}/api/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) throw new Error('Failed to process request');

            const result = await response.json();
            logDebug('Request processed successfully');

            document.getElementById('progress-fill').style.width = '100%';
            document.getElementById('status').textContent = 'Analysis complete!';

            showResults(result.content);
        } catch (error) {
            logDebug(`Error processing request: ${error.message}`);
            document.getElementById('status').textContent = `Error: ${error.message}`;
        }
    }

    function showResults(content) {
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.classList.remove('hidden');

        resultsContainer.innerHTML = `
            <div class="result-header">
                <div class="result-title">Analysis Results</div>
            </div>
            <div class="result-body">${content}</div>
        `;
    }

    // Test the backend connection
    testBackendBtn.addEventListener('click', async function () {
        logDebug(`Testing backend connection to ${getBackendUrl()}...`);

        try {
            const response = await fetch(`${getBackendUrl()}/api/health`);
            if (!response.ok) throw new Error('Backend health check failed');

            const data = await response.json();
            logDebug(`Backend is healthy: ${JSON.stringify(data)}`);
            alert(`Backend is healthy! Status: ${data.status}`);
        } catch (error) {
            logDebug(`Backend connection failed: ${error.message}`);
            alert(`Backend connection failed: ${error.message}`);
        }
    });

    // Event listeners
    prevBtn.addEventListener('click', () => goToStep(currentStep - 1));

    nextBtn.addEventListener('click', () => {
        if (currentStep === totalSteps) {
            // Restart the process
            currentStep = 0;
            selectedModels = [];
            selectedAnalysisType = null;
            selectedAlacarteOptions = [];
            selectedOutputFormat = null;
            prompt.value = '';
        }

        goToStep(currentStep + 1);
    });

    // Initialize the app
    init();
});
