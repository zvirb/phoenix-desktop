# Palette's Journal

## 2025-02-12 - Focus States on Containers
**Learning:** Standard browser outlines on inputs often clash with custom designs or are too subtle. Applying `:focus-within` styles to the parent container of an input creates a much more robust and "designed" focus state that mimics native desktop applications.
**Action:** When styling inputs inside containers (like search bars), always remove the input's default outline and apply a focus ring/border change to the container using `:focus-within` for better visual feedback.

## 2025-10-24 - Input Loading States
**Learning:** For async operations like AI processing, simply showing a spinner isn't enough. Disabling the input and changing the placeholder to a verb (e.g., "Thinking...") provides immediate confirmation that the system accepted the request and is working, preventing user frustration from double-submissions.
**Action:** When implementing search/chat inputs that trigger async backend tasks, always pair the loading spinner with a disabled input state and a status-reflecting placeholder.
