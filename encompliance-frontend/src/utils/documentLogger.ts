// Document Flow Logger - A utility for tracking document-related operations

// Enable verbose logging in development only
const VERBOSE_LOGGING = process.env.NODE_ENV === 'development' || true;

// Unique color for document logs to make them stand out in the console
const LOG_STYLE = 'background: #3a5683; color: white; padding: 2px 4px; border-radius: 2px;';
const ERROR_STYLE = 'background: #e53e3e; color: white; padding: 2px 4px; border-radius: 2px;';
const SUCCESS_STYLE = 'background: #38a169; color: white; padding: 2px 4px; border-radius: 2px;';
const WARNING_STYLE = 'background: #d69e2e; color: white; padding: 2px 4px; border-radius: 2px;';

interface LogData {
  [key: string]: any;
}

// Main logging function
export const docLog = (message: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  console.log(`%c[DOC]%c ${message}`, LOG_STYLE, '', data || '');
};

// Success logging
export const docSuccess = (message: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  console.log(`%c[DOC-SUCCESS]%c ${message}`, SUCCESS_STYLE, '', data || '');
};

// Error logging
export const docError = (message: string, error?: any, data?: LogData) => {
  console.error(`%c[DOC-ERROR]%c ${message}`, ERROR_STYLE, '', error, data || '');
};

// Warning logging
export const docWarn = (message: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  console.warn(`%c[DOC-WARN]%c ${message}`, WARNING_STYLE, '', data || '');
};

// Operation start logging
export const docStart = (operation: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  console.log(`%c[DOC-START]%c ${operation} started`, LOG_STYLE, '', data || '');
  console.time(`DOC-OP: ${operation}`);
  return operation; // Return the operation name for timing
};

// Operation end logging
export const docEnd = (operation: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  try {
    console.timeEnd(`DOC-OP: ${operation}`);
  } catch (e) {
    console.warn(`Timer 'DOC-OP: ${operation}' does not exist. Make sure to call docStart first.`);
  }
  console.log(`%c[DOC-END]%c ${operation} completed`, LOG_STYLE, '', data || '');
};

// Document state transition logging
export const docState = (documentId: string | number, from: string, to: string, data?: LogData) => {
  if (!VERBOSE_LOGGING) return;
  
  console.log(`%c[DOC-STATE]%c Document ${documentId}: ${from} → ${to}`, LOG_STYLE, '', data || '');
};

export default {
  log: docLog,
  success: docSuccess,
  error: docError,
  warn: docWarn,
  start: docStart,
  end: docEnd,
  state: docState
}; 