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
    className = ''
}) => {
    const [exportFormat, setExportFormat] = useState<'pdf' | 'markdown' | 'json' | 'text'>('pdf');
    const [isExporting, setIsExporting] = useState(false);

    // Format the filename
    const getFilename = () => {
        const dateString = analysisData.timestamp || new Date().toISOString().split('T')[0];
        const titleSnippet = (analysisData.title || analysisData.prompt || 'analysis')
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
            const timesRomanBoldFont = await pdfDoc.embedFont(StandardFonts.TimesRomanBold);

            const page = pdfDoc.addPage([600, 800]);
            const { width, height } = page.getSize();
            const margin = 50;

            // Add title
            page.drawText('Ultra AI Analysis', {
                x: margin,
                y: height - margin,
                size: 24,
                font: timesRomanBoldFont,
                color: rgb(0, 0, 0)
            });

            // Add timestamp
            page.drawText(`Generated: ${analysisData.timestamp || new Date().toLocaleString()}`, {
                x: margin,
                y: height - margin - 30,
                size: 10,
                font: timesRomanFont,
                color: rgb(0.3, 0.3, 0.3)
            });

            // Add prompt
            page.drawText('Prompt:', {
                x: margin,
                y: height - margin - 60,
                size: 14,
                font: timesRomanBoldFont,
                color: rgb(0, 0, 0)
            });

            const promptLines = splitTextIntoLines(analysisData.prompt, 80);
            promptLines.forEach((line, index) => {
                page.drawText(line, {
                    x: margin,
                    y: height - margin - 80 - (index * 15),
                    size: 11,
                    font: timesRomanFont,
                    color: rgb(0, 0, 0)
                });
            });

            // Add result heading
            const promptYOffset = 80 + (promptLines.length * 15) + 20;
            page.drawText('Analysis Result:', {
                x: margin,
                y: height - margin - promptYOffset,
                size: 14,
                font: timesRomanBoldFont,
                color: rgb(0, 0, 0)
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
                        color: rgb(0.5, 0.5, 0.5)
                    });
                }

                currentPage.drawText(resultLines[i], {
                    x: margin,
                    y: currentY,
                    size: 11,
                    font: timesRomanFont,
                    color: rgb(0, 0, 0)
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
                    color: rgb(0.5, 0.5, 0.5)
                });
            }

            // Add page number to first page
            page.drawText(`Page 1${pageCount > 1 ? ` of ${pageCount}` : ''}`, {
                x: width - margin - 40,
                y: margin / 2,
                size: 10,
                font: timesRomanFont,
                color: rgb(0.5, 0.5, 0.5)
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
        const models = analysisData.models ? `\nModels used: ${analysisData.models.join(', ')}` : '';
        const pattern = analysisData.pattern ? `\nAnalysis pattern: ${analysisData.pattern}` : '';
        const ultraModel = analysisData.ultraModel ? `\nSynthesis model: ${analysisData.ultraModel}` : '';

        const markdownContent = `# Ultra AI Analysis
Generated: ${timestamp}${models}${pattern}${ultraModel}

## Prompt
${analysisData.prompt}

## Result
${analysisData.result}
`;

        const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
        saveAs(blob, `${getFilename()}.md`);
    };

    // Export to JSON
    const exportToJson = () => {
        const jsonContent = JSON.stringify({
            timestamp: analysisData.timestamp || new Date().toISOString(),
            title: analysisData.title || 'Ultra AI Analysis',
            prompt: analysisData.prompt,
            result: analysisData.result,
            models: analysisData.models || [],
            pattern: analysisData.pattern || null,
            ultraModel: analysisData.ultraModel || null
        }, null, 2);

        const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' });
        saveAs(blob, `${getFilename()}.json`);
    };

    // Export plain text
    const exportToText = () => {
        const timestamp = analysisData.timestamp || new Date().toLocaleString();
        const models = analysisData.models ? `\nModels used: ${analysisData.models.join(', ')}` : '';
        const pattern = analysisData.pattern ? `\nAnalysis pattern: ${analysisData.pattern}` : '';
        const ultraModel = analysisData.ultraModel ? `\nSynthesis model: ${analysisData.ultraModel}` : '';

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

    // Handle export click
    const handleExport = async () => {
        if (!analysisData?.result) {
            alert('No analysis results to export.');
            return;
        }

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
            }
        } catch (error) {
            console.error('Export failed:', error);
            alert('Export failed. Please try another format.');
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className={`export-results ${className}`}>
            <div className="export-format-options">
                <label className="export-format-label">
                    Export Format:
                    <select
                        value={exportFormat}
                        onChange={(e) => setExportFormat(e.target.value as any)}
                        className="export-format-select"
                        disabled={isExporting}
                    >
                        <option value="pdf">PDF Document</option>
                        <option value="markdown">Markdown (.md)</option>
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
