# Sentinel Report: Unlimited Client-Side File Processing

**Observation:** The `ChatInterface` component allows users to drag and drop files of any size. The browser attempts to read the entire file into memory as a Base64 string via `FileReader`.

**Impact:** **High**. Large files (e.g., >50MB) can cause the browser tab to freeze or crash due to memory exhaustion. Additionally, sending massive payloads to the backend without size validation can lead to server-side memory pressure or denial of service.

**Suggested Action:** Implement a client-side file size check (e.g., 10MB limit) in the `onDrop` handler and `handleSubmit` function. Display a toast error if the file exceeds the limit.

**Future Benefit:** Improved UX stability and backend protection against resource exhaustion attacks.
