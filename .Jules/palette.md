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
