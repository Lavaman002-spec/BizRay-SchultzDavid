# Testing the Company Search Table

## Prerequisites

Make sure both backend and frontend are running:

```bash
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend
cd frontend
pnpm dev
```

Or use the convenience script:

```bash
make dev
```

## Testing the Search Feature

1. **Navigate to Search Page**

   - Open http://localhost:3000
   - Click "Search Companies" button
   - Or go directly to http://localhost:3000/search

2. **Search for Companies**

   - Enter a company name (minimum 2 characters)
   - Example searches:
     - "BMW" - for BMW companies
     - "Austria" - for companies with Austria in name
     - "Bank" - for banking institutions
   - Click "Search" button

3. **View Results in Table**

   - Results display in a scrollable table with:
     - FNR (Company Registration Number)
     - Company Name
     - Action buttons

4. **View Company Details**

   - Click "View Details" button for any company
   - A modal dialog opens showing:
     - Basic information (name, legal form, location)
     - Status
     - Business purpose
     - Raw JSON data (expandable)

5. **External Link**
   - Click the external link icon to open the official registry page

## Features Demonstrated

- ✅ **shadcn/ui Table Component** - Responsive table with proper styling
- ✅ **Scroll Area** - Handle large datasets with scrollable content
- ✅ **Dialog Modal** - Show detailed company information
- ✅ **Loading States** - Skeleton loaders while fetching data
- ✅ **Error Handling** - User-friendly error messages
- ✅ **Responsive Design** - Works on desktop and mobile

## API Endpoints Used

- `GET /search?q={query}` - Search companies
- `GET /company/{fnr}` - Get company details

## Troubleshooting

**Backend not responding:**

- Ensure backend is running on port 8000
- Check backend/.env has valid API_KEY and WSDL_URL
- Run `curl http://localhost:8000/healthz` to verify

**No results found:**

- Try different search terms
- Ensure minimum 2 characters
- Check backend logs for API issues

**Frontend errors:**

- Clear browser cache
- Run `pnpm install` to ensure all dependencies
- Check browser console for errors
