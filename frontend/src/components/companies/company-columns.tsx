'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { ExternalLink, Eye } from 'lucide-react';

export type Company = {
  fnr: string;
  name: string;
};

export const companyColumns: ColumnDef<Company>[] = [
  {
    accessorKey: 'fnr',
    header: 'FNR',
    cell: ({ row }) => (
      <div className="font-mono text-sm">{row.getValue('fnr')}</div>
    ),
  },
  {
    accessorKey: 'name',
    header: 'Company Name',
    cell: ({ row }) => (
      <div className="font-medium">{row.getValue('name')}</div>
    ),
  },
  {
    id: 'actions',
    header: () => <div className="text-right">Actions</div>,
    cell: ({ row }) => {
      const company = row.original;

      return (
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // You can add custom action here
              console.log('View details for:', company);
            }}
          >
            <Eye className="mr-2 h-4 w-4" />
            View Details
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <a
              href={`https://www.justiz.gv.at/web2013/html/default/2c9484853e87b5f4013ef4474f9e044f.de.html?fbclid=${company.fnr}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </Button>
        </div>
      );
    },
  },
];
