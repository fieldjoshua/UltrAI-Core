// Analysis Manager
class AnalysisManager {
    static init() {
        this.bindEvents();
    }

    static bindEvents() {
        Utils.on($('#analysis-form'), 'submit', (e) => this.handleAnalysis(e));
    }

    static async handleAnalysis(e) {
        e.preventDefault();
        
        const documentId = $('#document-select').value;
        const prompt = $('#prompt-input').value.trim();
        const model = $('#model-select').value;

        if (!documentId) {
            NotificationManager.show('Please select a document', 'error');
            return;
        }

        if (!prompt) {
            NotificationManager.show('Please enter an analysis prompt', 'error');
            return;
        }

        try {
            LoadingManager.show($('#analyze-btn'), 'Analyzing...');
            this.showAnalyzing();

            const response = await api.createAnalysis(documentId, prompt, model);
            
            this.showResults(response);
            NotificationManager.show('Analysis completed!', 'success');
        } catch (error) {
            APIErrorHandler.handle(error, 'Analysis');
        } finally {
            LoadingManager.hide($('#analyze-btn'));
        }
    }

    static showAnalyzing() {
        const resultsContent = $('#results-content');
        resultsContent.innerHTML = '<div class="spinner"></div><p>Analyzing document...</p>';
        Utils.removeClass($('#results-container'), 'hidden');
    }

    static showResults(analysis) {
        const resultsContent = $('#results-content');
        resultsContent.textContent = analysis.response || 'No response received';
        
        Utils.removeClass($('#results-actions'), 'hidden');
        
        // Bind action buttons
        Utils.on($('#export-btn'), 'click', () => this.exportResults(analysis));
        Utils.on($('#save-btn'), 'click', () => this.saveResults(analysis));
    }

    static exportResults(analysis) {
        const blob = new Blob([analysis.response], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        NotificationManager.show('Results exported!', 'success');
    }

    static saveResults(analysis) {
        Utils.storage.set(`analysis-${Date.now()}`, analysis);
        NotificationManager.show('Results saved locally!', 'success');
    }
}

window.AnalysisManager = AnalysisManager;