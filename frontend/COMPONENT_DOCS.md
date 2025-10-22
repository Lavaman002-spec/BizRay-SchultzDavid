# Company List Component

## Overview

The `CompanyList` is a reusable React component that provides a complete company search and display interface connected to the backend API.

## Location

- **Component**: `/frontend/src/components/companies/company-list.tsx`
- **Columns**: `/frontend/src/components/companies/company-columns.tsx`

## Features

- ✅ **Connected to Backend API** - Fetches real data from `/search` endpoint
- ✅ **Reusable** - Can be used on multiple pages with different configurations
- ✅ **Search Functionality** - Built-in search form (can be toggled)
- ✅ **Loading States** - Skeleton loaders while fetching data
- ✅ **Error Handling** - User-friendly error messages
- ✅ **Data Table** - Uses TanStack Table for sorting and display
- ✅ **Action Buttons** - View details and external link for each company

## Usage

### Basic Usage

```tsx
import { CompanyList } from '@/components/companies/company-list';

export default function MyPage() {
  return <CompanyList />;
}
```

### With Search Bar (Default)

```tsx
<CompanyList showSearch={true} />
```

### Without Search Bar

```tsx
<CompanyList showSearch={false} />
```

### Auto-load with Initial Query

```tsx
<CompanyList initialQuery="BMW" autoLoad={true} showSearch={false} />
```

## Props

| Prop           | Type      | Default | Description                      |
| -------------- | --------- | ------- | -------------------------------- |
| `initialQuery` | `string`  | `''`    | Initial search query             |
| `autoLoad`     | `boolean` | `false` | Automatically load data on mount |
| `showSearch`   | `boolean` | `true`  | Show/hide the search input form  |

## Component Structure

### CompanyList Component

- Manages state (companies, loading, error, query)
- Handles API calls to backend
- Renders search form (optional)
- Displays loading/error/empty states
- Renders DataTable with results

### Company Columns

- Defines table column structure
- **FNR Column**: Company registration number (monospace font)
- **Company Name Column**: Company name (medium font weight)
- **Actions Column**:
  - View Details button (placeholder for modal)
  - External link to official registry

## Data Type

```typescript
export type Company = {
  fnr: string; // Company Registration Number
  name: string; // Company Name
};
```

## API Integration

The component fetches data from:

```
GET http://localhost:8000/search?q={query}
```

Expected response:

```json
{
  "results": [
    {
      "fnr": "123456a",
      "name": "Example Company GmbH"
    }
  ]
}
```

## Examples

### Home Page (Main Page)

```tsx
// Shows search bar, allows users to search companies
<CompanyList showSearch={true} />
```

### Search Page

```tsx
// Dedicated search page with card layout
<Card>
  <CardHeader>
    <CardTitle>Company Search</CardTitle>
  </CardHeader>
  <CardContent>
    <CompanyList showSearch={true} />
  </CardContent>
</Card>
```

### Dashboard with Pre-loaded Results

```tsx
// Load specific companies without search bar
<CompanyList initialQuery="Technology" autoLoad={true} showSearch={false} />
```

## Customization

### Adding Custom Actions

Edit `/frontend/src/components/companies/company-columns.tsx`:

```tsx
{
  id: 'actions',
  cell: ({ row }) => {
    const company = row.original;

    return (
      <div className="flex justify-end gap-2">
        <Button onClick={() => handleCustomAction(company)}>
          Custom Action
        </Button>
        {/* Existing buttons... */}
      </div>
    );
  },
}
```

### Adding More Columns

```tsx
export const companyColumns: ColumnDef<Company>[] = [
  // Existing columns...
  {
    accessorKey: 'location',
    header: 'Location',
    cell: ({ row }) => <div>{row.getValue('location')}</div>,
  },
];
```

## Related Components

- **DataTable**: `/frontend/src/app/companies/data-table.tsx` - Generic data table wrapper
- **CompanyTable**: `/frontend/src/components/company-table.tsx` - Legacy table (can be deprecated)
- **CompanyDetailsDialog**: `/frontend/src/components/company-details-dialog.tsx` - Modal for details

## Migration Notes

### Old Approach (Before)

```tsx
// Had to manage state, API calls, and UI in each page
const [companies, setCompanies] = useState([]);
const [loading, setLoading] = useState(false);
// ... lots of duplicate code
```

### New Approach (After)

```tsx
// Just import and use!
<CompanyList showSearch={true} />
```

## Future Enhancements

- [ ] Add pagination support
- [ ] Add sorting by FNR or name
- [ ] Add filtering options
- [ ] Add export to CSV functionality
- [ ] Integrate CompanyDetailsDialog for "View Details" button
- [ ] Add company logo/avatar display
- [ ] Add company status badges
