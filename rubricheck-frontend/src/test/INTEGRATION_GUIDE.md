# Student Results Integration Guide

This guide shows how to integrate the new Student Results component into your RubriCheck application.

## 🚀 Quick Start

### 1. Add the Component to Your App

```typescript
// In your main App.tsx or routing file
import StudentResults from './pages/StudentResults'

// Add a route for the student view
<Route path="/student-results" component={StudentResults} />
```

### 2. Update Navigation

Add a "Student View" button to your existing Results page:

```typescript
// In Results.tsx
<a 
  href="/student-results" 
  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
>
  Student View
</a>
```

### 3. Test with Sample Data

Use the generated test data to verify functionality:

```typescript
import { studentTestResult } from './test/StudentResultsTestData'

// In your test environment
const mockResult = studentTestResult
const mockEssayText = studentTestResult.essay_text
```

## 📊 Data Format Requirements

The Student Results component expects data in this format:

```typescript
interface StudentResult {
  id: string
  essay_text: string
  overall_score: number        // 0-100 scale
  letter_grade: string         // A+, A, B+, etc.
  timestamp: string           // ISO date string
  criteria: Criterion[]
  metadata: {
    word_count: number
    paragraph_count: number
    reading_time: string
  }
}
```

## 🔄 Converting Backend Data

If your backend returns data in a different format, use this conversion:

```typescript
function convertBackendToStudentResult(backendResult: any, essayText: string): StudentResult {
  return {
    id: backendResult.id || 'student_result_001',
    essay_text: essayText,
    overall_score: backendResult.overall?.numeric > 1 
      ? backendResult.overall.numeric 
      : backendResult.overall.numeric * 100,
    letter_grade: backendResult.overall?.letter || 'N/A',
    timestamp: new Date().toISOString(),
    criteria: backendResult.items?.map((item: any) => ({
      id: item.id,
      name: item.name,
      weight: item.weight,
      score: item.score,
      level: getLevelFromScore(item.score),
      confidence: item.confidence,
      evidence_spans: item.evidence_spans || [],
      feedback: {
        why: item.feedback?.why || 'No feedback available.',
        suggestion: item.feedback?.suggestion || 'No suggestions available.',
        strengths: item.feedback?.strengths || [],
        areas_for_improvement: item.feedback?.areas_for_improvement || []
      }
    })) || [],
    metadata: {
      word_count: essayText.split(/\s+/).length,
      paragraph_count: essayText.split(/\n\s*\n/).length,
      reading_time: `${Math.ceil(essayText.split(/\s+/).length / 200)}-${Math.ceil(essayText.split(/\s+/).length / 150)} minutes`
    }
  }
}
```

## 🎨 Customization Options

### Styling
The component uses Tailwind CSS classes. You can customize:

```typescript
// Color schemes for different levels
const levelColors = {
  'Excellent': 'bg-emerald-100 text-emerald-800',
  'Proficient': 'bg-sky-100 text-sky-800',
  'Meets expectations': 'bg-amber-100 text-amber-800',
  'Developing': 'bg-rose-100 text-rose-800',
  'Poor': 'bg-red-100 text-red-800'
}
```

### Features
Toggle features on/off:

```typescript
const [showConfidenceIndicators, setShowConfidenceIndicators] = useState(true)
const [accessibilityMode, setAccessibilityMode] = useState(false)
```

## 🧪 Testing

### 1. Unit Tests
```typescript
import { render, screen } from '@testing-library/react'
import StudentResults from './StudentResults'

test('renders student results with test data', () => {
  render(<StudentResults />)
  expect(screen.getByText('RubriCheck Results — Student View')).toBeInTheDocument()
})
```

### 2. Integration Tests
```typescript
test('keyboard navigation works', () => {
  render(<StudentResults />)
  // Test arrow key navigation
  fireEvent.keyDown(document, { key: 'ArrowDown' })
  // Verify focus changes
})
```

### 3. Accessibility Tests
```typescript
test('meets accessibility standards', () => {
  render(<StudentResults />)
  const results = axe(container)
  expect(results).toHaveNoViolations()
})
```

## 📱 Responsive Design

The component is fully responsive:

- **Desktop**: Two-column layout (essay + feedback)
- **Tablet**: Stacked layout with full-width panels
- **Mobile**: Optimized for touch interaction

## 🔧 Configuration

### Environment Variables
```env
# Optional: Customize export endpoints
REACT_APP_PDF_EXPORT_URL=/api/export/pdf
REACT_APP_CSV_EXPORT_URL=/api/export/csv
```

### Props (if needed)
```typescript
interface StudentResultsProps {
  customTheme?: 'light' | 'dark' | 'high-contrast'
  showExportButtons?: boolean
  enableKeyboardNavigation?: boolean
  maxEvidenceSpans?: number
}
```

## 🚨 Error Handling

The component includes comprehensive error handling:

```typescript
// Null/undefined result
if (!studentResult) {
  return <div>No results available</div>
}

// Invalid data structure
if (!result.overall || !result.items) {
  return <div>Invalid result format</div>
}
```

## 📈 Performance

### Optimization Tips
1. **Memoize expensive calculations**:
```typescript
const filteredCriteria = useMemo(() => 
  criteria.filter(c => c.name.includes(searchTerm)), 
  [criteria, searchTerm]
)
```

2. **Lazy load evidence spans**:
```typescript
const [visibleSpans, setVisibleSpans] = useState(10)
```

3. **Debounce search**:
```typescript
const debouncedSearch = useDebounce(searchTerm, 300)
```

## 🔍 Debugging

### Common Issues
1. **Evidence not highlighting**: Check evidence_spans data format
2. **Keyboard navigation not working**: Verify focus management
3. **Export buttons not working**: Implement export handlers

### Debug Mode
```typescript
const DEBUG = process.env.NODE_ENV === 'development'

if (DEBUG) {
  console.log('Student Result Data:', studentResult)
  console.log('Evidence Spans:', studentResult.criteria.flatMap(c => c.evidence_spans))
}
```

## 📚 Additional Resources

- [Test Data Examples](./StudentResultsTestData.ts)
- [HTML Test Page](./StudentResultsTestPage.html)
- [Component Documentation](./README.md)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 🤝 Contributing

When adding new features:

1. Update the TypeScript interfaces
2. Add test cases
3. Update documentation
4. Test accessibility compliance
5. Verify responsive design

---

**Ready to provide better student feedback experiences! 🎓**
