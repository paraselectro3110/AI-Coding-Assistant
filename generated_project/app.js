// Simple Calculator Logic
// This script assumes the DOM elements defined in index.html are present.

// Import DOM elements
const display = document.getElementById('display');
const buttons = document.querySelectorAll('.btn');

// State variables
let currentInput = '';
let previousValue = null; // holds the left operand as a number
let operator = null; // '+', '-', '*', '/'
let shouldResetDisplay = false;

/**
 * Updates the calculator display and synchronises currentInput.
 * @param {string|number} value - Value to show on the display.
 */
function updateDisplay(value) {
  const str = String(value);
  display.value = str;
  currentInput = str;
}

/**
 * Clears all calculator state and resets the display to "0".
 */
function clearAll() {
  currentInput = '';
  previousValue = null;
  operator = null;
  shouldResetDisplay = false;
  updateDisplay('0');
}

/**
 * Appends a digit (or decimal point) to the current input.
 * If the display should be reset first, it clears the current input.
 * @param {string} digit - The digit character pressed.
 */
function appendDigit(digit) {
  if (shouldResetDisplay) {
    currentInput = '';
    shouldResetDisplay = false;
  }
  // Prevent leading zeros like "00" – keep a single zero unless a decimal point follows.
  if (currentInput === '0' && digit === '0') return;
  if (currentInput === '0' && digit !== '.') {
    currentInput = digit;
  } else {
    currentInput += digit;
  }
  updateDisplay(currentInput);
}

/**
 * Performs the pending arithmetic operation.
 * Returns the result as a number, or the string "Error" on division by zero.
 */
function compute() {
  if (operator === null) {
    return parseFloat(currentInput) || 0;
  }
  const currentVal = parseFloat(currentInput) || 0;
  let result;
  switch (operator) {
    case '+':
      result = previousValue + currentVal;
      break;
    case '-':
      result = previousValue - currentVal;
      break;
    case '*':
      result = previousValue * currentVal;
      break;
    case '/':
      if (currentVal === 0) {
        // Division by zero error handling
        updateDisplay('Error');
        shouldResetDisplay = true;
        return 'Error';
      }
      result = previousValue / currentVal;
      break;
    default:
      result = currentVal;
  }
  return result;
}

/**
 * Sets the operator for the next calculation.
 * If there is already a pending operation, it is computed first.
 * @param {string} op - One of '+', '-', '*', '/'.
 */
function setOperator(op) {
  if (previousValue === null) {
    // First operator press – store the current number.
    previousValue = parseFloat(currentInput) || 0;
  } else if (operator) {
    // Compute the previous pending operation before storing the new operator.
    const result = compute();
    if (result === 'Error') {
      // Error already displayed; reset state.
      previousValue = null;
      operator = null;
      return;
    }
    previousValue = result;
    updateDisplay(result);
  }
  operator = op;
  shouldResetDisplay = true;
}

// Attach event listeners to buttons based on their classes.
buttons.forEach((btn) => {
  if (btn.classList.contains('digit')) {
    btn.addEventListener('click', () => {
      const digit = btn.dataset.value;
      appendDigit(digit);
    });
  } else if (btn.classList.contains('operator')) {
    btn.addEventListener('click', () => {
      const op = btn.dataset.operator;
      setOperator(op);
    });
  }
});

// Equals button handling
const equalsBtn = document.getElementById('equals');
if (equalsBtn) {
  equalsBtn.addEventListener('click', () => {
    if (operator) {
      const result = compute();
      if (result !== 'Error') {
        updateDisplay(result);
      }
      previousValue = null;
      operator = null;
      shouldResetDisplay = true;
    }
  });
}

// Clear button handling
const clearBtn = document.getElementById('clear');
if (clearBtn) {
  clearBtn.addEventListener('click', clearAll);
}

// Expose functions for testing via the global `calc` object.
window.calc = {
  appendDigit,
  setOperator,
  compute,
  clearAll,
  updateDisplay,
};

// Initialise display on load.
clearAll();
