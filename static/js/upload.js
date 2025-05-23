// Document Upload Manager
class DocumentUploader {
    static init() {
        this.bindEvents();
        this.loadDocuments();
    }

    static bindEvents() {
        const uploadArea = $('#upload-area');
        const fileInput = $('#file-input');
        const fileSelectBtn = $('#file-select-btn');

        // File select button
        Utils.on(fileSelectBtn, 'click', () => fileInput.click());
        Utils.on(fileInput, 'change', (e) => this.handleFiles(e.target.files));

        // Drag and drop
        Utils.on(uploadArea, 'dragover', (e) => {
            e.preventDefault();
            Utils.addClass(uploadArea.querySelector('.upload-zone'), 'dragover');
        });

        Utils.on(uploadArea, 'dragleave', () => {
            Utils.removeClass(uploadArea.querySelector('.upload-zone'), 'dragover');
        });

        Utils.on(uploadArea, 'drop', (e) => {
            e.preventDefault();
            Utils.removeClass(uploadArea.querySelector('.upload-zone'), 'dragover');
            this.handleFiles(e.dataTransfer.files);
        });
    }

    static async handleFiles(files) {
        for (const file of files) {
            await this.uploadFile(file);
        }
    }

    static async uploadFile(file) {
        try {
            this.showProgress();
            
            const response = await api.uploadDocument(file, (progress) => {
                this.updateProgress(progress);
            });

            NotificationManager.show(`${file.name} uploaded successfully!`, 'success');
            this.loadDocuments();
        } catch (error) {
            APIErrorHandler.handle(error, 'File upload');
        } finally {
            this.hideProgress();
        }
    }

    static showProgress() {
        Utils.removeClass($('#upload-progress'), 'hidden');
    }

    static updateProgress(percent) {
        $('#progress-fill').style.width = `${percent}%`;
        $('#progress-text').textContent = `Uploading... ${Math.round(percent)}%`;
    }

    static hideProgress() {
        Utils.addClass($('#upload-progress'), 'hidden');
        $('#progress-fill').style.width = '0%';
    }

    static async loadDocuments() {
        try {
            const documents = await api.getDocuments();
            this.renderDocuments(documents);
        } catch (error) {
            console.warn('Failed to load documents:', error);
        }
    }

    static renderDocuments(documents) {
        const container = $('#documents-list');
        
        if (!documents || documents.length === 0) {
            container.innerHTML = '<p class="empty-state">No documents uploaded yet.</p>';
            return;
        }

        container.innerHTML = documents.map(doc => `
            <div class="document-item" data-id="${doc.id}">
                <div class="document-info">
                    <span class="document-name">${Utils.sanitizeHtml(doc.filename)}</span>
                    <span class="document-size">${Utils.formatDate(doc.created_at)}</span>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="DocumentUploader.selectDocument(${doc.id})">
                    Select
                </button>
            </div>
        `).join('');

        // Update document select dropdown
        this.updateDocumentSelect(documents);
    }

    static updateDocumentSelect(documents) {
        const select = $('#document-select');
        select.innerHTML = '<option value="">Choose a document...</option>' +
            documents.map(doc => 
                `<option value="${doc.id}">${Utils.sanitizeHtml(doc.filename)}</option>`
            ).join('');
    }

    static selectDocument(documentId) {
        $('#document-select').value = documentId;
        NotificationManager.show('Document selected for analysis', 'info');
    }
}

window.DocumentUploader = DocumentUploader;