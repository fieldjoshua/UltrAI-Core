const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const app = express();
const port = 8000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  },
});

// Create uploads directory if it doesn't exist
const fs = require('fs');
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const upload = multer({ storage: storage });

// Enable CORS for all routes
app.use(cors());

// Parse JSON request bodies
app.use(express.json());

// Parse URL-encoded form bodies
app.use(express.urlencoded({ extended: true }));

// Mock data for documents
const mockDocuments = [
  {
    id: '1',
    name: 'Sample Document 1.pdf',
    size: 1024000,
    type: 'application/pdf',
    status: 'uploaded',
    uploadDate: '2023-05-15T12:30:00Z',
  },
  {
    id: '2',
    name: 'Research Paper.docx',
    size: 512000,
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    status: 'uploaded',
    uploadDate: '2023-05-14T10:15:00Z',
  },
  {
    id: '3',
    name: 'Data Analysis.xlsx',
    size: 256000,
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    status: 'processing',
    uploadDate: '2023-05-13T09:45:00Z',
  },
];

// Mock available models
const availableModels = [
  'gpt4o',
  'gpt4turbo',
  'claude37',
  'claude3opus',
  'gemini15',
  'llama3',
];

// Mock analysis history
const analysisHistory = [
  {
    id: '1',
    prompt:
      'Compare the differences between transformers and RNNs for NLP tasks.',
    timestamp: '2023-06-10T14:30:00Z',
    models: ['gpt4o', 'claude37'],
    pattern: 'consensus',
  },
  {
    id: '2',
    prompt: 'Explain quantum computing in simple terms.',
    timestamp: '2023-06-09T10:15:00Z',
    models: ['gpt4turbo', 'gemini15', 'claude3opus'],
    pattern: 'debate',
  },
];

// GET /api/documents - List all documents
app.get('/api/documents', (req, res) => {
  console.log('GET /api/documents requested');
  res.json(mockDocuments);
});

// GET /api/documents/:id - Get a single document
app.get('/api/documents/:id', (req, res) => {
  const document = mockDocuments.find((doc) => doc.id === req.params.id);
  if (!document) {
    return res.status(404).json({ error: 'Document not found' });
  }
  res.json(document);
});

// POST /api/upload-document - Upload a new document
app.post('/api/upload-document', upload.single('file'), (req, res) => {
  console.log('Upload document request received', req.file, req.body);

  // Create a mock uploaded document
  const newDocument = {
    id: (mockDocuments.length + 1).toString(),
    name: req.file ? req.file.originalname : `Document-${Date.now()}.pdf`,
    size: req.file ? req.file.size : 1024000,
    type: req.file ? req.file.mimetype : 'application/pdf',
    status: 'uploaded',
    uploadDate: new Date().toISOString(),
  };

  mockDocuments.push(newDocument);
  res.status(201).json(newDocument);
});

// DELETE /api/documents/:id - Delete a document
app.delete('/api/documents/:id', (req, res) => {
  const index = mockDocuments.findIndex((doc) => doc.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: 'Document not found' });
  }

  mockDocuments.splice(index, 1);
  res.status(200).json({ message: 'Document deleted successfully' });
});

// GET /api/available-models - Get available models
app.get('/api/available-models', (req, res) => {
  console.log('GET /api/available-models requested');
  res.json({ available_models: availableModels });
});

// GET /api/analysis/history - Get analysis history
app.get('/api/analysis/history', (req, res) => {
  console.log('GET /api/analysis/history requested');
  res.json(analysisHistory);
});

// POST /api/analyze - Perform analysis
app.post('/api/analyze', (req, res) => {
  console.log('POST /api/analyze requested', req.body);

  // Create mock analysis response based on the prompt
  const prompt = req.body.prompt || '';
  const selectedModels = req.body.selected_models || [];
  const pattern = req.body.pattern || 'standard';

  // Generate a response based on the pattern
  let response = '';

  if (pattern === 'debate') {
    response = `# Debate on: "${prompt}"\n\n`;

    if (selectedModels.includes('gpt4o')) {
      response += `## GPT-4o Perspective\nThe answer to this question has multiple facets. On one hand...\n\n`;
    }

    if (selectedModels.includes('claude37')) {
      response += `## Claude 3.7 Perspective\nI'd like to offer a slightly different view. While I agree with some points...\n\n`;
    }

    response += `## Ultra Analysis\nAfter analyzing the different perspectives, we can conclude that...\n`;
  } else if (pattern === 'consensus') {
    response = `# Consensus Analysis: "${prompt}"\n\n`;
    response += `Based on inputs from ${selectedModels.join(
      ', '
    )}, the consensus view is that...\n\n`;
    response += `Key points of agreement:\n- Point one\n- Point two\n- Point three\n\n`;
    response += `Areas where models differ slightly:\n- Minor difference one\n- Minor difference two\n`;
  } else {
    response = `# Standard Analysis: "${prompt}"\n\n`;
    response += `Based on the analysis from ${selectedModels.length} different models, the most comprehensive answer is:\n\n`;
    response += `The answer to your question involves several key aspects. First, consider that...\n\n`;
    response += `Additionally, it's important to note that...\n\n`;
    response += `In conclusion, the evidence suggests that...`;
  }

  // Add a short delay to simulate processing time
  setTimeout(() => {
    res.json({
      id: Math.floor(Math.random() * 1000).toString(),
      prompt: prompt,
      ultra_response: response,
      selected_models: selectedModels,
      pattern: pattern,
      timestamp: new Date().toISOString(),
    });
  }, 1500);
});

// POST /api/analyze-with-docs - Perform analysis with documents
app.post('/api/analyze-with-docs', (req, res) => {
  console.log('POST /api/analyze-with-docs requested', req.body);

  const prompt = req.body.prompt || '';
  const selectedModels = req.body.selected_models || [];
  const pattern = req.body.pattern || 'standard';
  const documentIds = req.body.document_ids || [];

  // Get document names for the response
  const documents = documentIds.map((id) => {
    const doc = mockDocuments.find((d) => d.id === id);
    return doc ? doc.name : `Document ${id}`;
  });

  let response = `# Analysis with Documents: "${prompt}"\n\n`;
  response += `## Referenced Documents\n`;
  documents.forEach((doc) => {
    response += `- ${doc}\n`;
  });

  response += `\n## Analysis\n`;
  response += `Based on the documents provided and analysis from ${selectedModels.join(
    ', '
  )}, here's what I found:\n\n`;
  response += `The documents reveal several key insights related to your query...\n\n`;
  response += `Document "${
    documents[0] || 'Sample'
  }" specifically mentions that...\n\n`;
  response += `In conclusion, the analysis of these documents suggests that...`;

  // Add a slightly longer delay to simulate document processing
  setTimeout(() => {
    res.json({
      id: Math.floor(Math.random() * 1000).toString(),
      prompt: prompt,
      ultra_response: response,
      selected_models: selectedModels,
      pattern: pattern,
      documents: documents,
      timestamp: new Date().toISOString(),
    });
  }, 2500);
});

// GET /api/analysis/:id - Get specific analysis
app.get('/api/analysis/:id', (req, res) => {
  const id = req.params.id;
  console.log(`GET /api/analysis/${id} requested`);

  // Look up in history first
  const analysis = analysisHistory.find((a) => a.id === id);

  if (analysis) {
    // Add a mock response
    const fullAnalysis = {
      ...analysis,
      ultra_response: `This is a detailed response for analysis id ${id} about "${analysis.prompt}".\n\nThe analysis includes multiple perspectives and considerations...`,
    };
    res.json(fullAnalysis);
  } else {
    // Generate a mock analysis
    res.json({
      id: id,
      prompt: 'This is a mock prompt for the requested analysis',
      ultra_response: `This is a mock response for analysis id ${id}.\n\nThe analysis includes multiple sections and detailed explanations...`,
      selected_models: ['gpt4o', 'claude37'],
      pattern: 'standard',
      timestamp: new Date().toISOString(),
    });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Mock API server running at http://localhost:${port}`);
  console.log(
    `Test documents endpoint at http://localhost:${port}/api/documents`
  );
  console.log(
    `Test analysis endpoints at http://localhost:${port}/api/available-models and /api/analyze`
  );
});
