# Palette's Journal

## 2025-02-12 - Focus States on Containers
**Learning:** Standard browser outlines on inputs often clash with custom designs or are too subtle. Applying `:focus-within` styles to the parent container of an input creates a much more robust and "designed" focus state that mimics native desktop applications.
**Action:** When styling inputs inside containers (like search bars), always remove the input's default outline and apply a focus ring/border change to the container using `:focus-within` for better visual feedback.

## 2025-10-24 - Input Loading States
**Learning:** For async operations like AI processing, simply showing a spinner isn't enough. Disabling the input and changing the placeholder to a verb (e.g., "Thinking...") provides immediate confirmation that the system accepted the request and is working, preventing user frustration from double-submissions.
**Action:** When implementing search/chat inputs that trigger async backend tasks, always pair the loading spinner with a disabled input state and a status-reflecting placeholder.

## 2025-10-25 - Integrated Action Feedback
**Learning:** Placing loading indicators (spinners) directly inside the primary action button rather than as a separate element preserves layout stability and reinforces the connection between the action (Submit) and the process (Loading).
**Action:** For single-action forms or inputs, replace the submit icon/text with a spinner during loading states to save space and provide direct feedback.

## 2026-02-08 - Desktop Expectations in Web Tech
**Learning:** In Tauri/Electron apps, users expect native desktop behaviors (like Esc to close dialogs) by default. Missing these interactions breaks the illusion of a native app more than visual discrepancies.
**Action:** Always implement global keyboard shortcuts (Esc for modals, Enter for submission) in desktop-targeted web views.

## 2026-03-01 - Native Focus Styles on Custom Elements
**Learning:** Custom buttons (like icon-only toggles) often lose default focus rings when styled with `background: transparent; border: none`. This makes keyboard navigation impossible. Manually adding `:focus-visible` styles is crucial for accessibility in custom UI components.
**Action:** When creating custom interactive elements (icon buttons, toggles), always explicitly define `:focus-visible` styles to ensure keyboard users can see where they are.

## 2026-06-15 - Micro-Interactions for Config Fields
**Learning:** For read-only configuration fields (like API keys or URLs), users expect quick copy functionality without manual selection. Providing immediate visual feedback (icon change/check) directly on the button is more effective than a separate toast for these small interactions.
**Action:** Always implement click-to-copy buttons with temporary success state (check icon) for read-only text fields that users might need to transfer elsewhere.

## 2026-10-27 - Dynamic Accessibility for State Changes
**Learning:** Visual feedback (like an icon changing to a checkmark) is insufficient for screen reader users. Updating `aria-label` and `title` attributes dynamically to reflect the successful state (e.g., "Copied!") provides essential confirmation for non-visual users.
**Action:** When implementing interactive state toggles (like copy-to-clipboard), always ensure the accessible name updates to reflect the new state, not just the visual icon.

## 2026-11-28 - Backend Status Normalization
**Learning:** Backend status codes (e.g., 'active', 'idle') often leak into the UI as raw strings. Previous logic only checked for 'Connected', causing other valid states to appear as errors.
**Action:** Always create a normalization layer (helper function) mapping raw status strings to UI-friendly labels and semantic colors.

## 2026-05-15 - Maintaining Focus During Loading States
**Learning:** While disabling inputs during async operations prevents duplicate submissions, it often causes the browser to move focus to the `body`, forcing users to re-click the input when the operation finishes. Using `readOnly` instead of `disabled` preserves focus while still preventing edits.
**Action:** Use `readOnly` combined with visual styling (e.g., `cursor: progress`, reduced opacity) for text inputs during short loading states to keep the user's workflow seamless.

## 2027-01-05 - Silencing Decorative SVGs
**Learning:** Icon buttons with `aria-label` often contain SVG graphics that screen readers unnecessarily announce as "graphic" or try to parse, creating noise.
**Action:** Always add `aria-hidden="true"` to SVG elements inside buttons that already provide an accessible name via `aria-label` or text content.

## 2027-05-20 - Fire-and-Forget Feedback
**Learning:** Actions that trigger background processes (like 'Capture') often lack immediate visual feedback, leaving users unsure if the click registered. Logging to a debug console is insufficient.
**Action:** For fire-and-forget buttons, always implement a temporary 'success' state (icon change/color flash) on the button itself to confirm the command was sent.

## 2027-05-21 - Consistent Copy Feedback for Generated Content
**Learning:** Users often need to transfer generated content (like task breakdowns) to other tools. Providing a dedicated "Copy All" button with immediate visual feedback (icon change) is a high-value, low-effort enhancement that aligns with existing patterns for configuration fields.
**Action:** When displaying read-only generated lists or text blocks, always include a copy button in the header that provides the same visual and accessible feedback as configuration fields.

## 2027-08-14 - Input Clearing Mechanisms
**Learning:** In search-heavy interfaces, users frequently need to clear their input to start over. Relying solely on backspace is tedious, especially for mouse users. A dedicated "Clear" button that appears when text is present is a standard expectation that improves flow.
**Action:** For main search or task inputs, always include a conditionally rendered "Clear" button inside the input container that resets the value and returns focus to the input.

## 2027-09-02 - Linking Helper Text
**Learning:** Placing helper text (e.g., "Stored in Windows Registry") visually near an input isn't enough for screen readers. They may miss the context entirely if it's read after the input.
**Action:** Always use `aria-describedby` to programmatically link helper text to its corresponding input, ensuring the description is announced when the input receives focus.

## 2027-09-02 - Respecting Motion Preferences
**Learning:** Purely decorative animations (like pulsing badges) can trigger vestibular disorders. Users who enable "Reduce Motion" expect these to stop, not just slow down.
**Action:** Always include a `@media (prefers-reduced-motion: reduce)` block that sets `animation: none` for decorative elements, ensuring the interface remains accessible to all users.

## 2027-10-15 - Accessible Log Views
**Learning:** Debug logs are often treated as "noise" and dimmed (low opacity), which destroys accessibility. Users with low vision cannot read them, and screen readers get a jumble of divs.
**Action:** For log regions, always use `role="log"`, ensure valid contrast (avoid opacity on text), and provide a "Clear" action to manage the noise.
