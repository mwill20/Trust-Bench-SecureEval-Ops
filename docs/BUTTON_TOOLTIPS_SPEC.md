# Button Tooltips Specification

**Last Updated**: October 14, 2025

---

## Button Hover Descriptions

### 1. Generate Report 📊

**Tooltip Text**:

```
📊 Generate a comprehensive PDF/HTML report with all metrics, charts, and
recommendations from the latest evaluation run. Perfect for sharing with
stakeholders or documenting system performance.
```

**Key Information Conveyed**:

- **What**: Creates a comprehensive report
- **Format**: PDF or HTML output
- **Content**: Metrics, charts, recommendations
- **Source**: Latest evaluation run
- **Use Case**: Sharing with stakeholders, documentation

**Emoji**: 📊 (bar chart - represents reporting/analytics)

---

### 2. Cleanup Workspace 🧹

**Tooltip Text**:

```
🧹 Archive old evaluation runs and clean up temporary files to free disk space.
Keeps the 10 most recent runs and the current baseline. Safe operation with
confirmation dialog.
```

**Key Information Conveyed**:

- **What**: Archives old runs and cleans temp files
- **Benefit**: Frees disk space
- **Safety**: Keeps 10 recent runs + baseline
- **Protection**: Confirmation dialog before deletion
- **Reassurance**: Safe operation

**Emoji**: 🧹 (broom - represents cleaning/tidying)

---

### 3. Promote to Baseline ⭐

**Tooltip Text**:

```
⭐ Save the current evaluation as the golden standard baseline. Future runs
will compare against this baseline to detect performance regressions or
improvements. Use this after a successful evaluation.
```

**Key Information Conveyed**:

- **What**: Saves current run as baseline
- **Purpose**: Golden standard for comparison
- **Benefit**: Detect regressions/improvements in future runs
- **When to Use**: After successful evaluation
- **Value**: Performance tracking over time

**Emoji**: ⭐ (star - represents excellence/baseline standard)

---

## Implementation Details

### Technology

- **Method**: HTML `title` attribute on `<button>` elements
- **Browser Support**: Native tooltip (all browsers)
- **Styling**: Default browser tooltip styling
- **Delay**: Browser default (~1 second hover delay)

### Code Location

- **File**: `trust_bench_studio/frontend/components/App.tsx`
- **Lines**: ~733-757 (footer section)

### Future Enhancements (Optional)

If you want more advanced tooltips with custom styling, consider:

1. **React Tooltip Library**:

   ```bash
   npm install react-tooltip
   ```

   - Custom styling
   - Positioning control
   - Rich content (icons, links)
   - Animation options

2. **Tailwind Tooltip Component**:

   - Use `group` and `peer` classes
   - Custom positioning
   - Fade-in animations
   - Dark mode support

3. **Tooltip Content Ideas**:
   - Show last action timestamp
   - Display disk space savings
   - Show baseline comparison stats
   - Add keyboard shortcuts
   - Include status indicators

---

## Tooltip Best Practices Applied

✅ **Concise but Informative**: Each tooltip ~2-3 sentences  
✅ **Action-Oriented**: Describes what will happen  
✅ **User Benefits**: Explains why they'd use it  
✅ **Safety Cues**: Mentions confirmations/safeguards  
✅ **Visual Hierarchy**: Emoji helps quick scanning  
✅ **Context-Aware**: Mentions prerequisites (e.g., "after successful evaluation")

---

## Accessibility Considerations

### Screen Readers

The `title` attribute is read by screen readers, making these buttons accessible.

### Keyboard Navigation

- Tooltips appear on focus (not just hover)
- Tab navigation shows tooltips
- Supports keyboard-only users

### Color Contrast

Button colors already meet WCAG AA standards:

- Gray button: sufficient contrast
- Green button: high contrast
- Blue button: high contrast

---

## Testing Tooltips

### Manual Testing

1. Open TrustBench Studio (`http://localhost:3000`)
2. Navigate to footer buttons
3. Hover over each button
4. Verify tooltip appears within ~1 second
5. Check tooltip text is readable
6. Verify tooltip disappears when hover ends

### Browser Testing

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (macOS)
- ✅ Mobile browsers (touch: shows on tap-hold)

---

## Tooltip Content Guidelines

### Writing Style

- **Clear & Direct**: No jargon or overly technical terms
- **Benefit-Focused**: Lead with what the user gains
- **Safe & Reassuring**: Mention safeguards for destructive actions
- **Actionable**: Use verbs (Generate, Archive, Save)

### Length

- **Ideal**: 150-250 characters
- **Max**: 500 characters (browser limitation)
- **Current**:
  - Generate Report: ~215 chars ✅
  - Cleanup Workspace: ~203 chars ✅
  - Promote to Baseline: ~223 chars ✅

### Formatting

- **Line Length**: ~70-80 chars per line (for readability)
- **Structure**: What → How → Why → When
- **Emoji**: One at the start for visual recognition

---

## Alternative Tooltip Designs (Future Options)

### Option 1: Expanded Tooltip with Stats

```tsx
<Tooltip>
  <TooltipTrigger>Generate Report</TooltipTrigger>
  <TooltipContent>
    <div className="space-y-2">
      <p>📊 Generate Comprehensive Report</p>
      <div className="text-xs opacity-75">
        <p>Last generated: 2 hours ago</p>
        <p>Format: PDF + HTML</p>
        <p>Size: ~2.3 MB</p>
      </div>
    </div>
  </TooltipContent>
</Tooltip>
```

### Option 2: Tooltip with Action Preview

```tsx
<Tooltip>
  <TooltipTrigger>Cleanup Workspace</TooltipTrigger>
  <TooltipContent>
    <div className="space-y-2">
      <p>🧹 Archive Old Runs</p>
      <div className="text-xs">
        <p>Will archive: 15 old runs</p>
        <p>Will free: ~458 MB</p>
        <p>Will keep: 10 recent + baseline</p>
      </div>
    </div>
  </TooltipContent>
</Tooltip>
```

### Option 3: Contextual Tooltip

```tsx
// Shows different tooltip based on current state
{
  hasBaseline ? (
    <button title="⭐ Update baseline with current evaluation">
      Promote to Baseline
    </button>
  ) : (
    <button title="⭐ Set this as your first baseline (recommended!)">
      Promote to Baseline
    </button>
  );
}
```

---

## Documentation Cross-References

- **Button Functionality**: See main requirements document
- **Implementation Plan**: Coming next
- **API Endpoints**: Backend routes to be created
- **User Guide**: To be added to documentation

---

## Changelog

### v1.0 - October 14, 2025

- ✅ Added tooltip to "Generate Report" button
- ✅ Added tooltip to "Cleanup Workspace" button
- ✅ Added tooltip to "Promote to Baseline" button
- ✅ Used native HTML `title` attribute for simplicity
- ✅ Included emojis for visual scanning

### Future Versions

- [ ] Consider react-tooltip for richer content
- [ ] Add keyboard shortcuts to tooltips
- [ ] Show contextual stats in tooltips
- [ ] Add animation/fade-in effects
- [ ] Support mobile long-press tooltips

---

**Status**: ✅ Implemented and ready for testing
