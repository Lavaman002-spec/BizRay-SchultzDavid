/* eslint-disable @typescript-eslint/no-explicit-any */
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { CompanyWithDetails } from '@/types/company';
import { computeRiskInsights } from '@/lib/riskInsights';
import { getReportingStats } from '@/lib/reportingStats';

/**
 * Generate a PDF report for a company with all available information
 * Following the BizRay design language with clean formatting
 */
export function generateCompanyPDF(company: CompanyWithDetails): void {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  let yPosition = 20;
  const riskInsights = computeRiskInsights(company);
  const reportingStats = getReportingStats(company);

  // Color palette matching the design language
  const colors: Record<string, [number, number, number]> = {
    primary: [37, 99, 235], // blue-600
    secondary: [107, 114, 128], // gray-500
    lightGray: [243, 244, 246], // gray-100
    darkGray: [31, 41, 55], // gray-800
    text: [17, 24, 39], // gray-900
  };

  const formatDate = (value?: Date | string | null) => {
    if (!value) return 'Not available';
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) return 'Not available';
    return date.toLocaleDateString();
  };

  // Helper function to add section headers
  const addSectionHeader = (text: string, y: number) => {
    doc.setFillColor(...colors.lightGray);
    doc.rect(margin, y - 5, pageWidth - margin * 2, 10, 'F');
    doc.setFontSize(14);
    doc.setTextColor(...colors.darkGray);
    doc.setFont('helvetica', 'bold');
    doc.text(text, margin + 2, y + 2);
    return y + 15;
  };

  // Title
  doc.setFontSize(24);
  doc.setTextColor(...colors.text);
  doc.setFont('helvetica', 'bold');
  doc.text('Company Report', margin, yPosition);
  yPosition += 10;

  // Horizontal line
  doc.setDrawColor(...colors.secondary);
  doc.setLineWidth(0.5);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 15;

  // Company Header
  doc.setFontSize(18);
  doc.setTextColor(...colors.primary);
  doc.setFont('helvetica', 'bold');
  doc.text(company.name, margin, yPosition);
  yPosition += 8;

  // Company details (Legal Form, FN Number, Status)
  doc.setFontSize(11);
  doc.setTextColor(...colors.secondary);
  doc.setFont('helvetica', 'normal');
  const headerInfo = [
    company.legal_form || 'N/A',
    `FN ${company.fnr}`,
    'Active',
  ].join(' • ');
  doc.text(headerInfo, margin, yPosition);
  yPosition += 15;

  // Basic Information Section
  yPosition = addSectionHeader('Basic Information', yPosition);

  const basicInfo = [
    ['Company Name', company.name],
    ['Legal Form', company.legal_form || 'Not available'],
    ['FN Number', company.fnr],
    ['State', company.state || 'Not available'],
    ['City', company.city || 'Not available'],
    [
      'Founded',
      company.created_at
        ? new Date(company.created_at).getFullYear().toString()
        : 'Not available',
    ],
  ];

  autoTable(doc, {
    startY: yPosition,
    head: [],
    body: basicInfo,
    theme: 'plain',
    styles: {
      fontSize: 10,
      cellPadding: 3,
      textColor: colors.text,
    },
    columnStyles: {
      0: { fontStyle: 'bold', textColor: colors.darkGray, cellWidth: 50 },
      1: { textColor: colors.text },
    },
    margin: { left: margin, right: margin },
  });

  yPosition = (doc as any).lastAutoTable.finalY + 15;

  // Addresses Section
  if (company.addresses && company.addresses.length > 0) {
    yPosition = addSectionHeader('Addresses', yPosition);

    company.addresses.forEach((address, index) => {
      const addressLines = [
        address.street && address.house_number
          ? `${address.street} ${address.house_number}`
          : address.street || 'N/A',
        address.city
          ? `${address.postal_code || ''} ${address.city}`.trim()
          : 'N/A',
        address.country || 'Austria',
      ];

      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...colors.darkGray);
      doc.text(`Address ${index + 1}`, margin + 2, yPosition);
      yPosition += 6;

      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...colors.text);
      addressLines.forEach((line) => {
        doc.text(line, margin + 2, yPosition);
        yPosition += 5;
      });

      yPosition += 5;
    });

    yPosition += 5;
  }

  // Officers & Management Section
  if (company.officers && company.officers.length > 0) {
    // Check if we need a new page
    if (yPosition > 240) {
      doc.addPage();
      yPosition = 20;
    }

    yPosition = addSectionHeader('Officers & Management', yPosition);

    const officersData = company.officers.map((officer) => [
      officer.full_name ||
        `${officer.first_name || ''} ${officer.last_name || ''}`.trim() ||
        'N/A',
      officer.role || 'Officer',
      officer.birth_date
        ? new Date(officer.birth_date).toLocaleDateString()
        : 'N/A',
    ]);

    autoTable(doc, {
      startY: yPosition,
      head: [['Name', 'Role', 'Birth Date']],
      body: officersData,
      theme: 'striped',
      headStyles: {
        fillColor: colors.primary,
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: 10,
      },
      styles: {
        fontSize: 9,
        cellPadding: 4,
        textColor: colors.text,
      },
      alternateRowStyles: {
        fillColor: colors.lightGray,
      },
      margin: { left: margin, right: margin },
    });

    yPosition = (doc as any).lastAutoTable.finalY + 15;
  }

  // Activities Section
  if (company.activities && company.activities.length > 0) {
    // Check if we need a new page
    if (yPosition > 240) {
      doc.addPage();
      yPosition = 20;
    }

    yPosition = addSectionHeader('Business Activities', yPosition);

    company.activities.forEach((activity, index) => {
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...colors.text);

      // Wrap text if needed
      const splitText = doc.splitTextToSize(
        `${index + 1}. ${activity.description}`,
        pageWidth - margin * 2 - 4
      );

      splitText.forEach((line: string) => {
        if (yPosition > 280) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(line, margin + 2, yPosition);
        yPosition += 5;
      });

      yPosition += 3;
    });

    yPosition += 5;
  }

  // Risk Overview Section
  if (yPosition > 240) {
    doc.addPage();
    yPosition = 20;
  }

  yPosition = addSectionHeader('Risk Overview', yPosition);

  doc.setFontSize(11);
  doc.setTextColor(...colors.text);
  doc.setFont('helvetica', 'bold');
  doc.text(
    `Overall Score: ${riskInsights.score}/100 (${riskInsights.level} risk)`,
    margin + 2,
    yPosition
  );
  yPosition += 6;

  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...colors.secondary);
  doc.text(
    `Signals derived from revenue, profitability, compliance, legal, operational, and network indicators.`,
    margin + 2,
    yPosition
  );
  yPosition += 10;

  autoTable(doc, {
    startY: yPosition,
    head: [['Category', 'Score', 'Insight']],
    body: riskInsights.breakdown.map((item) => [
      item.category,
      `${item.score}`,
      item.hint || '—',
    ]),
    theme: 'grid',
    headStyles: {
      fillColor: colors.primary,
      textColor: [255, 255, 255],
      fontSize: 10,
    },
    styles: {
      fontSize: 9,
      cellPadding: 3,
      textColor: colors.text,
    },
    alternateRowStyles: {
      fillColor: [248, 250, 252],
    },
    margin: { left: margin, right: margin },
  });

  yPosition = (doc as any).lastAutoTable.finalY + 8;

  if (riskInsights.alerts.length > 0) {
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Alerts & Notes', margin + 2, yPosition);
    yPosition += 6;

    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.text);

    riskInsights.alerts.forEach((alert) => {
      const line = `${alert.severity.toUpperCase()} • ${alert.title} (${
        alert.timestamp
      })${alert.description ? ` – ${alert.description}` : ''}`;
      const rows = doc.splitTextToSize(line, pageWidth - margin * 2 - 4);

      rows.forEach((row) => {
        if (yPosition > 280) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(`• ${row}`, margin + 4, yPosition);
        yPosition += 5;
      });

      yPosition += 3;
    });
  }

  // Reporting & Compliance Section
  if (yPosition > 240) {
    doc.addPage();
    yPosition = 20;
  }

  yPosition = addSectionHeader('Reporting & Compliance', yPosition);

  const reportingLines = [
    `Last filing: ${formatDate(reportingStats.lastFiling.date)} (${
      reportingStats.lastFiling.type
    }, status: ${reportingStats.lastFiling.status})`,
    `Next due: ${formatDate(reportingStats.nextDue.date)} (${
      reportingStats.nextDue.isOverdue
        ? 'Overdue'
        : reportingStats.nextDue.dueInDays !== null
        ? `in ${reportingStats.nextDue.dueInDays} days`
        : 'On track'
    })`,
    `Compliance: ${reportingStats.compliance.statusLabel} • ${reportingStats.compliance.badgeLabel}`,
    `Documents on record: ${reportingStats.documents.count} (${reportingStats.documents.issuesText})`,
  ];

  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...colors.text);
  reportingLines.forEach((line) => {
    doc.text(line, margin + 2, yPosition);
    yPosition += 6;
  });

  yPosition += 4;

  if (company.filings && company.filings.length > 0) {
    const filingsData = company.filings
      .slice()
      .sort((a, b) => {
        const aDate = a.date ? new Date(a.date).getTime() : 0;
        const bDate = b.date ? new Date(b.date).getTime() : 0;
        return bDate - aDate;
      })
      .map((filing) => [
        filing.date ? new Date(filing.date).toLocaleDateString() : 'N/A',
        filing.filing_type || 'Filing',
        filing.status || 'Unknown',
        filing.description || '—',
      ]);

    autoTable(doc, {
      startY: yPosition,
      head: [['Date', 'Type', 'Status', 'Description']],
      body: filingsData,
      theme: 'grid',
      headStyles: {
        fillColor: colors.primary,
        textColor: [255, 255, 255],
        fontSize: 9,
      },
      styles: {
        fontSize: 8,
        cellPadding: 3,
        textColor: colors.text,
      },
      columnStyles: {
        0: { cellWidth: 25 },
        1: { cellWidth: 35 },
        2: { cellWidth: 28 },
        3: { cellWidth: pageWidth - margin * 2 - 88 },
      },
      margin: { left: margin, right: margin },
    });

    yPosition = (doc as any).lastAutoTable.finalY + 10;
  }

  // Footer
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(...colors.secondary);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `Generated by BizRay • ${new Date().toLocaleDateString()}`,
      margin,
      doc.internal.pageSize.getHeight() - 10
    );
    doc.text(
      `Page ${i} of ${pageCount}`,
      pageWidth - margin - 20,
      doc.internal.pageSize.getHeight() - 10
    );
  }

  // Save the PDF
  const fileName = `${company.name.replace(/[^a-zA-Z0-9]/g, '_')}_Report_${
    new Date().toISOString().split('T')[0]
  }.pdf`;
  doc.save(fileName);
}
