# BizRay Frontend

This is the frontend application built with [Next.js](https://nextjs.org).

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm

### Installation

```bash
pnpm install
```

### Development

Run the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Build

```bash
pnpm build
```

### Production

```bash
pnpm start
```

## Project Structure

```
src/
├── app/              # Next.js App Router pages
│   ├── api/         # API routes
│   ├── search/      # Search page with table view
│   ├── layout.tsx   # Root layout
│   └── page.tsx     # Home page
├── components/      # React components
│   ├── company-table.tsx              # Company data table
│   ├── company-details-dialog.tsx     # Company details modal
│   ├── layout/                        # Layout components
│   └── ui/                            # UI components (shadcn/ui)
└── lib/             # Utility functions
```

## Features

- **Company Search**: Search companies from Austrian Business Register
- **Table View**: Display search results in an interactive table with:
  - Company Registration Number (FNR)
  - Company Name
  - View Details button to see full company information
  - External link to official registry
- **Company Details**: Modal dialog with comprehensive company information
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS

## Tech Stack

- **Framework:** Next.js 15.5 with App Router
- **UI Library:** React 19
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn/ui with Radix UI primitives
- **Icons:** Lucide React
- **Type Safety:** TypeScript

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)
