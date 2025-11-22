import { NextRequest, NextResponse } from "next/server";
import puppeteer from "puppeteer";
import { remark } from "remark";
import html from "remark-html";

export async function POST(req: NextRequest) {
    const { markdown } = await req.json();

    // Convert markdown to HTML
    const processed = await remark().use(html).process(markdown);
    const htmlContent = processed.toString();

    const browser = await puppeteer.launch({
        headless: true, // FIX #1
    });

    const page = await browser.newPage();

    await page.setContent(`
        <html>
            <head>
                <style>
                    body {
                        font-family: sans-serif;
                        padding: 40px;
                        line-height: 1.6;
                        font-size: 14px;
                    }
                    h1, h2, h3, h4, h5, h6 {
                        margin-top: 24px;
                        margin-bottom: 12px;
                    }
                    p {
                        margin-bottom: 12px;
                    }
                </style>
            </head>
            <body>${htmlContent}</body>
        </html>
    `);

    const pdfBytes = await page.pdf({ format: "A4" });
    await browser.close();

    // FIX #2: Convert Uint8Array → Buffer
    return new NextResponse(Buffer.from(pdfBytes), {
        status: 200,
        headers: {
            "Content-Type": "application/pdf",
            "Content-Disposition": 'attachment; filename="export.pdf"',
        },
    });
}
