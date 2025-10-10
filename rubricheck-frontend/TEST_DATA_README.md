# Test Data for Student Results View

This document explains how to use the test data feature to preview the Student Results view without running a full evaluation.

## Quick Start

1. **Open the application** in your browser (http://localhost:5173)
2. **Click "Load Test Data"** button in the yellow development panel at the top
3. **Click "Student View"** in the Results section
4. **Explore the Student Results** with real data!

## What's Included

The test data includes:

- **Essay**: A 803-word essay about Aristotle's philosophy and social media
- **Evaluation Results**: 6 criteria with detailed feedback, evidence spans, and suggestions
- **Overall Score**: 76.25% (B or below)
- **Evidence Spans**: Highlighted text segments that support each criterion

## Features to Test

### Left Panel - Essay Viewer
- ✅ **Annotated View**: Yellow highlights show AI evidence
- ✅ **Original View**: Clean text without highlights
- ✅ **Interactive Highlights**: Click highlighted text to expand related criteria
- ✅ **Smooth Scrolling**: Auto-scroll to evidence when clicked

### Right Panel - Rubric & Feedback
- ✅ **Collapsible Panel**: Click chevron to expand/collapse entire panel
- ✅ **Individual Criteria**: Click arrows to expand/collapse each criterion
- ✅ **Auto-expansion**: Clicking essay highlights automatically opens related criteria
- ✅ **Search**: Filter criteria by name
- ✅ **Confidence Indicators**: High/Medium/Low confidence levels
- ✅ **Score Visualization**: Progress bars and level badges

### Accessibility Features
- ✅ **Keyboard Navigation**: Use ↑/↓ arrows to navigate criteria
- ✅ **High Contrast Mode**: Toggle accessibility mode
- ✅ **Screen Reader Support**: Proper ARIA labels and semantic HTML

## Console Commands

You can also load test data from the browser console:

```javascript
// Load test data
loadTestData()

// Check if data is loaded
console.log(useApp.getState().result)
console.log(useApp.getState().essayText)
```

## Data Structure

The test data comes from a real evaluation:
- **File**: `evaluation_results_20251009_141904.json`
- **Essay**: About Aristotle's philosophy and social media
- **6 Criteria**: Focus, Organization, Evidence, Analysis, Style, Grammar
- **Evidence Spans**: 3-5 highlighted text segments per criterion
- **Feedback**: Detailed "Why?" explanations and "Try this next" suggestions

## Removing Test Data

To clear the test data and return to normal operation:

1. **Refresh the page** (F5 or Ctrl+R)
2. **Or use console**: `useApp.getState().reset()`

## Production Note

The "Load Test Data" button and development panel should be removed before deploying to production. This is only for development and testing purposes.

---

**Happy Testing!** 🎉

The Student Results view is now fully functional with real data. Try clicking on highlighted text, expanding criteria, and exploring all the interactive features!
