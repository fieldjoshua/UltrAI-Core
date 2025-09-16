document.addEventListener('DOMContentLoaded', function () {
  // DOM elements
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const steps = Array.from(document.querySelectorAll('.step'));
  const stepIndicators = Array.from(
    document.querySelectorAll('.step-indicator')
  );
  const prompt = document.getElementById('prompt');
  const promptError = document.getElementById('prompt-error');
  const backendUrl = document.getElementById('backend-url');

  // State
  let currentStep = 1;
  let totalSteps = steps.length;
  let selectedModels = [];
  let selectedAnalysisType = null;
  let selectedAlacarteOptions = [];
  let selectedOutputFormat = null;

  // Get backend URL
  function getBackendUrl() {
    return backendUrl.value;
  }

  // Initialize the app
  function init() {
    fetchModels();
    fetchAnalysisTypes();
    fetchAlacarteOptions();
    fetchOutputFormats();
  }

  // Step navigation
  function goToStep(step) {
    // Validate step
    if (step < 1 || step > totalSteps) return;

    // Validate current step before proceeding
    if (step > currentStep && !validateCurrentStep()) {
      return;
    }

    // Update current step
    currentStep = step;

    // Update UI
    updateSteps();
    updateButtons();

    // Load data if needed
    loadDataForCurrentStep();

    // Special handling for final step
    if (currentStep === totalSteps) {
      startProcessing();
    }
  }

  function updateSteps() {
    // Update step content visibility
    steps.forEach((step, index) => {
      if (index + 1 === currentStep) {
        step.classList.add('active');
      } else {
        step.classList.remove('active');
      }
    });

    // Update step indicators
    stepIndicators.forEach((indicator, index) => {
      const stepNumber = index + 1;
      indicator.classList.remove('active', 'completed');

      if (stepNumber === currentStep) {
        indicator.classList.add('active');
      } else if (stepNumber < currentStep) {
        indicator.classList.add('completed');
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

  function loadDataForCurrentStep() {
    switch (currentStep) {
      case 3: // Models
        if (document.getElementById('models-container').children.length <= 1) {
          fetchModels();
        }
        break;
      case 4: // Analysis Types
        if (
          document.getElementById('analysis-types-container').children.length <=
          1
        ) {
          fetchAnalysisTypes();
        }
        break;
      case 5: // A La Carte Options
        if (
          document.getElementById('alacarte-options-container').children
            .length <= 1
        ) {
          fetchAlacarteOptions();
        }
        break;
      case 6: // Output Formats
        if (
          document.getElementById('output-formats-container').children.length <=
          1
        ) {
          fetchOutputFormats();
        }
        break;
    }
  }

  function validateCurrentStep() {
    switch (currentStep) {
      case 1: // Prompt
        if (!prompt.value.trim()) {
          promptError.classList.remove('hidden');
          return false;
        }
        promptError.classList.add('hidden');
        return true;

      case 3: // Models
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

  // Data fetch functions
  async function fetchModels() {
    try {
      document.getElementById('models-loading').textContent =
        'Loading models...';

      const response = await fetch(`${getBackendUrl()}/api/models`);
      if (!response.ok) throw new Error('Failed to fetch models');

      const models = await response.json();
      renderModels(models);
    } catch (error) {
      console.error('Error fetching models:', error);
      document.getElementById('models-loading').textContent =
        'Error loading models. Try again later.';
    }
  }

  function renderModels(models) {
    const container = document.getElementById('models-container');
    container.innerHTML = ''; // Clear container

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
      });

      container.appendChild(modelCard);
    });
  }

  async function fetchAnalysisTypes() {
    try {
      document.getElementById('analysis-types-loading').textContent =
        'Loading analysis types...';

      const response = await fetch(`${getBackendUrl()}/api/analysis-types`);
      if (!response.ok) throw new Error('Failed to fetch analysis types');

      const analysisTypes = await response.json();
      renderAnalysisTypes(analysisTypes);
    } catch (error) {
      console.error('Error fetching analysis types:', error);
      document.getElementById('analysis-types-loading').textContent =
        'Error loading analysis types. Try again later.';
    }
  }

  function renderAnalysisTypes(analysisTypes) {
    const container = document.getElementById('analysis-types-container');
    container.innerHTML = '';

    analysisTypes.forEach((type, index) => {
      const radioItem = document.createElement('div');
      radioItem.className = 'radio-item';

      radioItem.innerHTML = `
                <input type="radio" id="analysis-type-${type.id}" name="analysis-type" value="${type.id}" ${index === 0 ? 'checked' : ''}>
                <label for="analysis-type-${type.id}">
                    <strong>${type.name}</strong>: ${type.description}
                </label>
            `;

      const radio = radioItem.querySelector('input');
      radio.addEventListener('change', () => {
        if (radio.checked) {
          selectedAnalysisType = type.id;
        }
      });

      container.appendChild(radioItem);
    });

    // Set default selected analysis type
    if (analysisTypes.length > 0) {
      selectedAnalysisType = analysisTypes[0].id;
    }
  }

  async function fetchAlacarteOptions() {
    try {
      document.getElementById('alacarte-options-loading').textContent =
        'Loading options...';

      const response = await fetch(`${getBackendUrl()}/api/alacarte-options`);
      if (!response.ok) throw new Error('Failed to fetch a la carte options');

      const options = await response.json();
      renderAlacarteOptions(options);
    } catch (error) {
      console.error('Error fetching a la carte options:', error);
      document.getElementById('alacarte-options-loading').textContent =
        'Error loading options. Try again later.';
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
          selectedAlacarteOptions = selectedAlacarteOptions.filter(
            id => id !== option.id
          );
        }
      });

      container.appendChild(checkboxItem);
    });
  }

  async function fetchOutputFormats() {
    try {
      document.getElementById('output-formats-loading').textContent =
        'Loading output formats...';

      const response = await fetch(`${getBackendUrl()}/api/output-formats`);
      if (!response.ok) throw new Error('Failed to fetch output formats');

      const formats = await response.json();
      renderOutputFormats(formats);
    } catch (error) {
      console.error('Error fetching output formats:', error);
      document.getElementById('output-formats-loading').textContent =
        'Error loading output formats. Try again later.';
    }
  }

  function renderOutputFormats(formats) {
    const container = document.getElementById('output-formats-container');
    container.innerHTML = '';

    formats.forEach((format, index) => {
      const radioItem = document.createElement('div');
      radioItem.className = 'radio-item';

      radioItem.innerHTML = `
                <input type="radio" id="format-${format.id}" name="output-format" value="${format.id}" ${index === 0 ? 'checked' : ''}>
                <label for="format-${format.id}">
                    <strong>${format.name}</strong>: ${format.description}
                </label>
            `;

      const radio = radioItem.querySelector('input');
      radio.addEventListener('change', () => {
        if (radio.checked) {
          selectedOutputFormat = format.id;
        }
      });

      container.appendChild(radioItem);
    });

    // Set default selected output format
    if (formats.length > 0) {
      selectedOutputFormat = formats[0].id;
    }
  }

  function startProcessing() {
    // Reset progress
    const progressFill = document.getElementById('progress-fill');
    const status = document.getElementById('status');
    const resultsContainer = document.getElementById('results-container');

    progressFill.style.width = '0%';
    status.textContent = 'Processing your request...';
    resultsContainer.classList.add('hidden');
    resultsContainer.innerHTML = '';

    // Gather data for request
    const requestData = {
      prompt: prompt.value.trim(),
      models: selectedModels,
      analysisType: selectedAnalysisType,
      alacarteOptions: selectedAlacarteOptions,
      outputFormat: selectedOutputFormat,
    };

    // Send request
    processRequest(requestData);
  }

  async function processRequest(requestData) {
    try {
      // Simulate progression
      simulateProgress();

      const response = await fetch(`${getBackendUrl()}/api/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) throw new Error('Failed to process request');

      const result = await response.json();

      // Complete progress
      document.getElementById('progress-fill').style.width = '100%';
      document.getElementById('status').textContent = 'Analysis complete!';

      // Display results
      displayResults(result.content);
    } catch (error) {
      console.error('Error processing request:', error);
      document.getElementById('status').textContent = `Error: ${error.message}`;
    }
  }

  function simulateProgress() {
    const progressFill = document.getElementById('progress-fill');
    let width = 0;

    const interval = setInterval(() => {
      if (width >= 90) {
        clearInterval(interval);
      } else {
        width += 5;
        progressFill.style.width = width + '%';
      }
    }, 300);
  }

  function displayResults(content) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.classList.remove('hidden');

    // Convert markdown to HTML (simple version)
    const htmlContent = content
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');

    resultsContainer.innerHTML = `
            <div class="result-header">
                <div class="result-title">Analysis Results</div>
            </div>
            <div class="result-body">${htmlContent}</div>
        `;
  }

  // Event listeners
  prevBtn.addEventListener('click', () => {
    goToStep(currentStep - 1);
  });

  nextBtn.addEventListener('click', () => {
    if (currentStep === totalSteps) {
      // Restart
      currentStep = 0;
      selectedModels = [];
      selectedAnalysisType = null;
      selectedAlacarteOptions = [];
      selectedOutputFormat = null;
      prompt.value = '';

      // Clear results
      document.getElementById('results-container').innerHTML = '';
    }

    goToStep(currentStep + 1);
  });

  // Initialize the app
  init();
});
