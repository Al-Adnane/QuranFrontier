# Scholar Governance Dashboard

A Next.js web application for Scholar Board oversight and correction workflows in Islamic scholarship verification.

## Features

### Pages
- **Dashboard** (`/dashboard`) - System health metrics, recent corrections, notifications, quick statistics, scholar board overview
- **Corrections** (`/corrections`) - Pending corrections review with filtering, bulk actions, and impact tracking
- **Audit Log** (`/audit_log`) - Immutable event log with query filters, search, export, and tamper detection
- **Conflict Resolution** (`/conflict_resolution`) - Madhab disagreement visualization with evidence chains and scholar notes
- **Analytics** (`/analytics`) - Usage statistics, error tracking, performance metrics, and correction velocity
- **Transparency Report** (`/transparency_report`) - Public summary statistics and compliance reporting

### Components
- **VerseViewer** - Display verses with confidence scoring and error reporting
- **TafsirPanel** - Side-by-side tafsir comparison with filtering
- **ConflictResolver** - Madhab disagreement visualization and resolution tools
- **AuditTrail** - Chronological event logging with hash verification
- **Layout** - Responsive sidebar navigation and main content area

## Architecture

### Stack
- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Date Handling**: date-fns

### Directory Structure
```
dashboard/
├── pages/
│   ├── _app.tsx              # App wrapper with layout
│   ├── index.tsx             # Root redirect
│   ├── dashboard.tsx         # Main dashboard
│   ├── corrections.tsx       # Corrections review
│   ├── audit_log.tsx         # Audit trail viewer
│   ├── conflict_resolution.tsx # Madhab conflicts
│   ├── analytics.tsx         # Analytics dashboard
│   └── transparency_report.tsx # Public report
├── components/
│   ├── Layout.tsx            # Main layout with sidebar
│   ├── VerseViewer.tsx       # Verse display component
│   ├── TafsirPanel.tsx       # Tafsir comparison
│   ├── ConflictResolver.tsx  # Conflict resolution UI
│   └── AuditTrail.tsx        # Audit log component
├── lib/
│   ├── api.ts               # API client and endpoints
│   └── store.ts             # Zustand stores (auth, notifications)
├── styles/
│   └── globals.css          # Tailwind and custom styles
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

## Setup & Installation

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
# Navigate to dashboard directory
cd nomos/engine/dashboard

# Install dependencies
npm install

# Set up environment variables (optional)
# Create .env.local file with:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev

# Open browser to http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

## API Integration

The dashboard is designed to connect to a FastAPI backend. Update the API endpoints in `lib/api.ts` to match your backend:

```typescript
// Example API call
import { api } from '@/lib/api';

// Get corrections
const corrections = await api.getCorrections('submitted');

// Submit new correction
await api.submitCorrection({
  type: 'hadith_grade',
  title: 'Correction title',
  originalText: 'Original',
  proposedChange: 'Proposed',
  justification: 'Justification',
});
```

## Authentication

The dashboard includes role-based access control:
- **Public**: Read-only access to verses and tafsirs
- **Researcher**: Can submit corrections and search
- **Scholar**: Can approve/reject corrections, resolve conflicts
- **Admin**: Full system access

Current implementation uses mock authentication. To integrate with your backend:

```typescript
// In lib/store.ts, update the login function to call your API:
login: async (email: string, password: string) => {
  const response = await api.login(email, password);
  // Handle token and user setup
};
```

## Real-time Updates

The dashboard is prepared for WebSocket integration:

```typescript
// In your pages, add WebSocket connection:
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');

  ws.onmessage = (event) => {
    const { type, data } = JSON.parse(event.data);
    if (type === 'new_correction') {
      // Update corrections list
    }
  };

  return () => ws.close();
}, []);
```

## Styling

The dashboard uses Tailwind CSS with custom color scheme:
- **Primary**: Quranic Gold (`#D4AF37`)
- **Dark**: `#1a1a1a`
- **Light**: `#f5f5f5`

Customize in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      quranic: {
        gold: '#D4AF37',
        dark: '#1a1a1a',
        light: '#f5f5f5',
      },
    },
  },
}
```

## Performance Optimization

- Pages use Next.js automatic code splitting
- Images should be optimized with `next/image`
- API calls are cached where appropriate
- Zustand stores prevent unnecessary re-renders

## Troubleshooting

### Port already in use
```bash
# Use different port
npm run dev -- -p 3001
```

### Module not found errors
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

## Future Enhancements

- [ ] WebSocket integration for real-time updates
- [ ] Export reports to PDF/Excel
- [ ] Advanced visualization charts
- [ ] Collaborative editing features
- [ ] Mobile-responsive improvements
- [ ] Dark mode support
- [ ] Advanced search filters
- [ ] Multi-language support

## License

Part of the NOMOS Universal Ethical Reasoning Infrastructure.

## Support

For issues or questions, contact the development team or check the main NOMOS documentation.
