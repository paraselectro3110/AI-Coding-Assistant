# Calculator Web App

## Project Overview
A simple, responsive web‑based calculator built with vanilla JavaScript, HTML, and CSS. It supports basic arithmetic operations, clear functionality, and displays user‑friendly error messages for invalid input.

---

## Tech Stack
- **HTML5** – Structure of the application.
- **CSS3** – Styling and responsive layout.
- **JavaScript (ES6)** – Core calculator logic and DOM interaction.

---

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Open the application**
   - Locate `index.html` in the project root.
   - Open the file directly in a web browser (no server required).
   - The calculator UI will load and be ready for use.

---

## Feature List
- **Basic Operations**: addition, subtraction, multiplication, division.
- **Clear (C) Button**: resets the current expression and display.
- **Equals (=) Button**: evaluates the entered expression.
- **Error Handling**: displays `Error` for malformed expressions or division by zero.
- **Responsive Design**: works on desktop and mobile browsers.

---

## Usage Guide
- **Number Buttons (0‑9)**: Append the corresponding digit to the display.
- **Operator Buttons (+, –, *, /)**: Append the operator to the current expression.
- **Clear (C)**: Clears the entire input and resets the display to `0`.
- **Equals (=)**: Calculates the result of the expression shown. If the expression is invalid, the display shows `Error`.
- **Error Messages**: The calculator shows a generic `Error` message for any evaluation failure (e.g., syntax errors, division by zero).

---

## Development Notes
- **File Responsibilities**
  - `index.html` – Defines the UI layout and button elements.
  - `styles.css` – Provides visual styling and ensures the calculator is responsive.
  - `app.js` – Contains all JavaScript logic: handling button clicks, building the expression string, evaluating it safely, and updating the display.
- **Task Ordering**
  1. Design the HTML structure for the calculator.
  2. Style the UI with CSS for a clean look.
  3. Implement core functionality in `app.js` (input handling, clear, evaluation, error handling).
- **Extending the Project**
  - **Keyboard Support**: Add an event listener for `keydown` events in `app.js` to map keyboard keys to calculator buttons.
  - **Advanced Operations**: Implement functions for exponentiation, parentheses handling, or scientific calculations.
  - **Theming**: Create additional CSS files or variables to allow dark/light mode toggling.

---

## License
[Add appropriate license information here]
