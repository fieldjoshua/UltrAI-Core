import React, { useState } from 'react';
import { saveAs } from 'file-saver';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

interface ExportResultsProps {
  analysisData: {
    title?: string;
    prompt: string;
    result: string;
    timestamp?: string;
    models?: string[];
    pattern?: string;
    ultraModel?: string;
  };
  className?: string;
}

/**
 * ExportResults component provides options to export analysis results in various formats
 * Supports: PDF, Markdown, JSON, and plaintext
 */
const ExportResults: React.FC<ExportResultsProps> = ({
  analysisData,
  className = '',
}) => {
  const [exportFormat, setExportFormat] = useState<
    'pdf' | 'markdown' | 'json' | 'text' | 'google_docs' | 'word' | 'rtf'
  >('pdf');
  const [isExporting, setIsExporting] = useState(false);

  // Format the filename
  const getFilename = () => {
    const dateString =
      analysisData.timestamp || new Date().toISOString().split('T')[0];
    const titleSnippet = (
      analysisData.title ||
      analysisData.prompt ||
      'analysis'
    )
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .substring(0, 30);
    return `ultra_${titleSnippet}_${dateString}`;
  };

  // Create and download PDF
  const exportToPdf = async () => {
    try {
      const pdfDoc = await PDFDocument.create();
      const timesRomanFont = await pdfDoc.embedFont(StandardFonts.TimesRoman);
      const timesRomanBoldFont = await pdfDoc.embedFont(
        StandardFonts.TimesRomanBold
      );

      const page = pdfDoc.addPage([600, 800]);
      const { width, height } = page.getSize();
      const margin = 50;

      // Add title
      page.drawText('Ultra AI Analysis', {
        x: margin,
        y: height - margin,
        size: 24,
        font: timesRomanBoldFont,
        color: rgb(0, 0, 0),
      });

      // Add timestamp
      page.drawText(
        `Generated: ${analysisData.timestamp || new Date().toLocaleString()}`,
        {
          x: margin,
          y: height - margin - 30,
          size: 10,
          font: timesRomanFont,
          color: rgb(0.3, 0.3, 0.3),
        }
      );

      // Add prompt
      page.drawText('Prompt:', {
        x: margin,
        y: height - margin - 60,
        size: 14,
        font: timesRomanBoldFont,
        color: rgb(0, 0, 0),
      });

      const promptLines = splitTextIntoLines(analysisData.prompt, 80);
      promptLines.forEach((line, index) => {
        page.drawText(line, {
          x: margin,
          y: height - margin - 80 - index * 15,
          size: 11,
          font: timesRomanFont,
          color: rgb(0, 0, 0),
        });
      });

      // Add result heading
      const promptYOffset = 80 + promptLines.length * 15 + 20;
      page.drawText('Analysis Result:', {
        x: margin,
        y: height - margin - promptYOffset,
        size: 14,
        font: timesRomanBoldFont,
        color: rgb(0, 0, 0),
      });

      // Add result content
      const resultLines = splitTextIntoLines(analysisData.result, 80);
      let currentPage = page;
      let currentY = height - margin - promptYOffset - 20;
      let pageCount = 1;

      for (let i = 0; i < resultLines.length; i++) {
        // If we're about to hit the bottom margin, create a new page
        if (currentY < margin + 40) {
          currentPage = pdfDoc.addPage([600, 800]);
          currentY = height - margin;
          pageCount++;

          // Add page number
          currentPage.drawText(`Page ${pageCount}`, {
            x: width - margin - 40,
            y: margin / 2,
            size: 10,
            font: timesRomanFont,
            color: rgb(0.5, 0.5, 0.5),
          });
        }

        currentPage.drawText(resultLines[i], {
          x: margin,
          y: currentY,
          size: 11,
          font: timesRomanFont,
          color: rgb(0, 0, 0),
        });

        currentY -= 15;
      }

      // Add model information as footer
      if (analysisData.models && analysisData.models.length > 0) {
        page.drawText(`Models: ${analysisData.models.join(', ')}`, {
          x: margin,
          y: margin / 2,
          size: 8,
          font: timesRomanFont,
          color: rgb(0.5, 0.5, 0.5),
        });
      }

      // Add page number to first page
      page.drawText(`Page 1${pageCount > 1 ? ` of ${pageCount}` : ''}`, {
        x: width - margin - 40,
        y: margin / 2,
        size: 10,
        font: timesRomanFont,
        color: rgb(0.5, 0.5, 0.5),
      });

      const pdfBytes = await pdfDoc.save();
      const blob = new Blob([pdfBytes], { type: 'application/pdf' });
      saveAs(blob, `${getFilename()}.pdf`);
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      alert('Failed to generate PDF. Please try another format.');
    }
  };

  // Helper function to split text into lines for PDF
  const splitTextIntoLines = (text: string, charsPerLine: number): string[] => {
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      if (currentLine.length + word.length + 1 <= charsPerLine) {
        currentLine += (currentLine.length > 0 ? ' ' : '') + word;
      } else {
        lines.push(currentLine);
        currentLine = word;
      }
    }

    if (currentLine.length > 0) {
      lines.push(currentLine);
    }

    return lines;
  };

  // Export to markdown
  const exportToMarkdown = () => {
    const timestamp = analysisData.timestamp || new Date().toLocaleString();
    const models = analysisData.models
      ? `\nModels used: ${analysisData.models.join(', ')}`
      : '';
    const pattern = analysisData.pattern
      ? `\nAnalysis pattern: ${analysisData.pattern}`
      : '';
    const ultraModel = analysisData.ultraModel
      ? `\nSynthesis model: ${analysisData.ultraModel}`
      : '';

    const markdownContent = `# Ultra AI Analysis
Generated: ${timestamp}${models}${pattern}${ultraModel}

## Prompt
${analysisData.prompt}

## Result
${analysisData.result}
`;

    const blob = new Blob([markdownContent], {
      type: 'text/markdown;charset=utf-8',
    });
    saveAs(blob, `${getFilename()}.md`);
  };

  // Export to JSON
  const exportToJson = () => {
    const jsonContent = JSON.stringify(
      {
        timestamp: analysisData.timestamp || new Date().toISOString(),
        title: analysisData.title || 'Ultra AI Analysis',
        prompt: analysisData.prompt,
        result: analysisData.result,
        models: analysisData.models || [],
        pattern: analysisData.pattern || null,
        ultraModel: analysisData.ultraModel || null,
      },
      null,
      2
    );

    const blob = new Blob([jsonContent], {
      type: 'application/json;charset=utf-8',
    });
    saveAs(blob, `${getFilename()}.json`);
  };

  // Export plain text
  const exportToText = () => {
    const timestamp = analysisData.timestamp || new Date().toLocaleString();
    const models = analysisData.models
      ? `\nModels used: ${analysisData.models.join(', ')}`
      : '';
    const pattern = analysisData.pattern
      ? `\nAnalysis pattern: ${analysisData.pattern}`
      : '';
    const ultraModel = analysisData.ultraModel
      ? `\nSynthesis model: ${analysisData.ultraModel}`
      : '';

    const textContent = `ULTRA AI ANALYSIS
Generated: ${timestamp}${models}${pattern}${ultraModel}

PROMPT:
${analysisData.prompt}

RESULT:
${analysisData.result}
`;

    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, `${getFilename()}.txt`);
  };

  // Handle export based on selected format
  const handleExport = async () => {
    setIsExporting(true);
    try {
      switch (exportFormat) {
        case 'pdf':
          await exportToPdf();
          break;
        case 'markdown':
          exportToMarkdown();
          break;
        case 'json':
          exportToJson();
          break;
        case 'text':
          exportToText();
          break;
        case 'rtf':
          exportToRtf();
          break;
        case 'google_docs':
          exportToGoogleDocs();
          break;
        case 'word':
          exportToWord();
          break;
        default:
          throw new Error(`Unsupported export format: ${exportFormat}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      // Optionally show an error notification here
    } finally {
      setIsExporting(false);
    }
  };

  // Download a file from a URL
  const downloadFile = (url: string, filename: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  };

  // Export to RTF format
  const exportToRtf = () => {
    const filename = `${getFilename()}.rtf`;
    const content = convertToRtf(analysisData.result || '');
    const blob = new Blob([content], { type: 'application/rtf' });
    const url = URL.createObjectURL(blob);
    downloadFile(url, filename);
  };

  // Export to Google Docs optimized format
  const exportToGoogleDocs = () => {
    const filename = `${getFilename()}_for_google_docs.html`;
    const content = convertToGoogleDocsHtml(analysisData.result || '');
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    downloadFile(url, filename);
  };

  // Export to Word optimized format
  const exportToWord = () => {
    const filename = `${getFilename()}_for_word.html`;
    const content = convertToWordHtml(analysisData.result || '');
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    downloadFile(url, filename);
  };

  // Convert text to RTF format
  const convertToRtf = (text: string) => {
    // Simple RTF conversion - this would be more complex in a real implementation
    let rtf = '{\\rtf1\\ansi\\ansicpg1252\\cocoartf2580\\cocoasubrtf230\n';
    rtf += '{\\fonttbl\\f0\\fswiss\\fcharset0 Helvetica;}\n';
    rtf += '{\\colortbl;\\red0\\green0\\blue0;}\n';
    rtf += '\\margl1440\\margr1440\\vieww11520\\viewh8400\\viewkind0\n';
    rtf +=
      '\\pard\\tx720\\tx1440\\tx2160\\tx2880\\tx3600\\tx4320\\tx5040\\tx5760\\tx6480\\tx7200\\tx7920\\tx8640\\pardirnatural\\partightenfactor0\n\n';
    rtf += '\\f0\\fs24 \\cf0 ';

    // Convert markdown to RTF
    const lines = text.split('\n');
    for (const line of lines) {
      // Handle headers
      if (line.startsWith('# ')) {
        rtf += `\\f0\\b\\fs36 ${line.substring(2)}\\b0\\fs24 \\par\n`;
      } else if (line.startsWith('## ')) {
        rtf += `\\f0\\b\\fs32 ${line.substring(3)}\\b0\\fs24 \\par\n`;
      } else if (line.startsWith('### ')) {
        rtf += `\\f0\\b\\fs28 ${line.substring(4)}\\b0\\fs24 \\par\n`;
      } else if (line.trim() === '') {
        rtf += '\\par\n';
      } else {
        // Escape \ and { and }
        let escapedLine = line
          .replace(/\\/g, '\\\\')
          .replace(/\{/g, '\\{')
          .replace(/\}/g, '\\}');
        rtf += `${escapedLine}\\par\n`;
      }
    }

    rtf += '}';
    return rtf;
  };

  // Convert text to Google Docs optimized HTML
  const convertToGoogleDocsHtml = (text: string) => {
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${getFilename()}</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #1a73e8; }
    h2 { color: #185abc; }
    h3 { color: #1967d2; }
    pre { background-color: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
    code { font-family: "Courier New", monospace; font-size: 0.9em; }
    blockquote { border-left: 4px solid #dadce0; padding-left: 16px; margin-left: 0; color: #5f6368; }
  </style>
</head>
<body>
  ${formatMarkdownToHtml(text)}
</body>
</html>`;

    return html;
  };

  // Convert text to Word optimized HTML
  const convertToWordHtml = (text: string) => {
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${getFilename()}</title>
  <style>
    body { font-family: "Calibri", sans-serif; line-height: 1.5; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2b579a; }
    h2 { color: #4472c4; }
    h3 { color: #5b9bd5; }
    pre { background-color: #f2f2f2; padding: 10px; border: 1px solid #d9d9d9; overflow-x: auto; }
    code { font-family: "Consolas", monospace; font-size: 0.9em; }
    blockquote { border-left: 4px solid #e6e6e6; padding-left: 16px; margin-left: 0; color: #666666; }
    table { border-collapse: collapse; width: 100%; }
    table, th, td { border: 1px solid #d9d9d9; }
    th, td { padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  ${formatMarkdownToHtml(text)}
</body>
</html>`;

    return html;
  };

  // Convert markdown to HTML
  const formatMarkdownToHtml = (markdown: string) => {
    // This is a simplified conversion - a real implementation would use a markdown parser
    let html = '';
    const lines = markdown.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith('# ')) {
        html += `<h1>${line.substring(2)}</h1>\n`;
      } else if (line.startsWith('## ')) {
        html += `<h2>${line.substring(3)}</h2>\n`;
      } else if (line.startsWith('### ')) {
        html += `<h3>${line.substring(4)}</h3>\n`;
      } else if (line.startsWith('- ')) {
        html += `<ul><li>${line.substring(2)}</li></ul>\n`;
      } else if (line.match(/^\d+\. /)) {
        html += `<ol><li>${line.replace(/^\d+\. /, '')}</li></ol>\n`;
      } else if (line.startsWith('> ')) {
        html += `<blockquote>${line.substring(2)}</blockquote>\n`;
      } else if (line.trim() === '') {
        html += '<p></p>\n';
      } else {
        html += `<p>${line}</p>\n`;
      }
    }

    return html;
  };

  return (
    <div className={`export-results ${className}`}>
      <div className="export-format-options">
        <label className="export-format-label">
          Export Format:
          <select
            value={exportFormat}
            onChange={e => setExportFormat(e.target.value as any)}
            className="export-format-select"
            disabled={isExporting}
          >
            <option value="pdf">PDF Document</option>
            <option value="markdown">Markdown (.md)</option>
            <option value="rtf">Rich Text Format (.rtf)</option>
            <option value="google_docs">Google Docs Optimized</option>
            <option value="word">Microsoft Word Optimized</option>
            <option value="json">JSON Data</option>
            <option value="text">Plain Text</option>
          </select>
        </label>
      </div>

      <button
        onClick={handleExport}
        disabled={isExporting || !analysisData?.result}
        className="export-button"
      >
        {isExporting ? 'Exporting...' : 'Export Results'}
      </button>
    </div>
  );
};

export default ExportResults;
