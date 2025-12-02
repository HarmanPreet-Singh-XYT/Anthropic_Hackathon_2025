// app/actions/export.ts
'use server'

import puppeteer from "puppeteer";
import { remark } from "remark";
import html from "remark-html";

export async function exportMarkdownToPDF(markdown: string) {
    try {
        // Convert markdown to HTML
        const processed = await remark().use(html).process(markdown);
        const htmlContent = processed.toString();

        // Launch Puppeteer
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox'], // Needed for some hosting environments
        });

        const page = await browser.newPage();

        // Set content with styling
        await page.setContent(`
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                            padding: 40px;
                            line-height: 1.6;
                            font-size: 14px;
                            color: #333;
                        }
                        h1, h2, h3, h4, h5, h6 {
                            margin-top: 24px;
                            margin-bottom: 12px;
                            font-weight: 600;
                            color: #1a1a1a;
                        }
                        h1 {
                            font-size: 2em;
                            border-bottom: 2px solid #e5e7eb;
                            padding-bottom: 8px;
                        }
                        h2 {
                            font-size: 1.5em;
                        }
                        h3 {
                            font-size: 1.25em;
                        }
                        p {
                            margin-bottom: 12px;
                        }
                        ul, ol {
                            margin-bottom: 12px;
                            padding-left: 24px;
                        }
                        li {
                            margin-bottom: 6px;
                        }
                        code {
                            background-color: #f3f4f6;
                            padding: 2px 6px;
                            border-radius: 3px;
                            font-family: 'Courier New', monospace;
                            font-size: 0.9em;
                        }
                        pre {
                            background-color: #f3f4f6;
                            padding: 12px;
                            border-radius: 6px;
                            overflow-x: auto;
                        }
                        pre code {
                            background-color: transparent;
                            padding: 0;
                        }
                        blockquote {
                            border-left: 4px solid #e5e7eb;
                            padding-left: 16px;
                            margin-left: 0;
                            color: #6b7280;
                        }
                        a {
                            color: #2563eb;
                            text-decoration: none;
                        }
                        a:hover {
                            text-decoration: underline;
                        }
                        table {
                            border-collapse: collapse;
                            width: 100%;
                            margin-bottom: 16px;
                        }
                        th, td {
                            border: 1px solid #e5e7eb;
                            padding: 8px 12px;
                            text-align: left;
                        }
                        th {
                            background-color: #f9fafb;
                            font-weight: 600;
                        }
                    </style>
                </head>
                <body>${htmlContent}</body>
            </html>
        `, {
            waitUntil: 'networkidle0'
        });

        // Generate PDF
        const pdfBytes = await page.pdf({
            format: "A4",
            printBackground: true,
            margin: {
                top: '20mm',
                right: '20mm',
                bottom: '20mm',
                left: '20mm'
            }
        });

        await browser.close();

        // Convert to base64 for transmission
        return {
            success: true,
            data: Buffer.from(pdfBytes).toString('base64')
        };

    } catch (error) {
        console.error('PDF generation error:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Failed to generate PDF'
        };
    }
}