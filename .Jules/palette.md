# Palette Journal

## 2024-10-24 - Initializing UX/A11y Focus

**Learning:** The project lacks explicit accessibility guidelines or documentation.
**Action:** Establish Palette persona to focus on incremental accessibility and UX improvements. Initial focus is on screen reader compatibility and keyboard navigation.

## 2024-10-24 - Screen Reader Verification

**Learning:** Verifying ARIA attributes (like `aria-live` and `aria-busy`) requires careful inspection of the DOM state during dynamic updates. Using browser automation scripts (Playwright) to check attribute presence is effective for verifying structural changes, even if auditory verification is not possible.
**Action:** Use Playwright scripts to assert the presence and correct values of ARIA attributes for future accessibility tasks.

## 2024-10-24 - Async Action Feedback Pattern
**Learning:** For async actions like form submission in the Neon theme, replacing the button text with a spinner and "PROCESSING" provides clear visual and screen-reader feedback, avoiding layout shifts and user uncertainty.
**Action:** Adopt the "Spinner in Button" pattern for all future async triggers: Disable button, set `aria-busy="true"`, inject `.spinner`, and update text to present tense (e.g., "PROCESSING").

## 2024-10-25 - Accessible Typing Effect

**Learning:** Terminal typing effects create a jarring experience for screen reader users, who hear fragmented character announcements. Using `aria-busy` is insufficient as it blocks updates but doesn't guarantee coherent reading.
**Action:** Implement a "Split Content" pattern for typing effects: Inject the full text immediately in a visually-hidden (`sr-only`) element for screen readers, and use an `aria-hidden` element for the character-by-character visual animation.
