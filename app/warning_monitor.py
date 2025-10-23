#!/usr/bin/env python3
"""
Streamlit Warning Monitor for AI Garment Generator
Captures, logs, and monitors Streamlit warnings and deprecation notices.
"""
import logging
import warnings
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Dict, Any
import streamlit as st

class StreamlitWarningMonitor:
    """Monitor and capture Streamlit warnings and deprecation notices."""

    def __init__(self, db_path: str = "data/streamlit_warnings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._setup_database()
        self._setup_warning_capture()
        self.logger = self._setup_logger()

    def _setup_database(self):
        """Create database table for storing warnings."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    filename TEXT,
                    lineno INTEGER,
                    function TEXT,
                    stack_trace TEXT,
                    session_id TEXT,
                    user_agent TEXT,
                    streamlit_version TEXT,
                    severity TEXT DEFAULT 'warning',
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT,
                    notes TEXT
                )
            ''')

            # Create indexes for better query performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON warnings(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON warnings(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_resolved ON warnings(resolved)')

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for warning monitor."""
        logger = logging.getLogger('streamlit_warnings')
        logger.setLevel(logging.WARNING)

        # File handler
        log_file = Path("logs/streamlit_warnings.log")
        log_file.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def _setup_warning_capture(self):
        """Setup warning capture for Streamlit and general Python warnings."""
        # Capture Python warnings
        warnings.filterwarnings('error', category=DeprecationWarning)
        warnings.filterwarnings('error', category=PendingDeprecationWarning)

        # Custom warning handler
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            self._capture_warning({
                'message': str(message),
                'category': category.__name__,
                'filename': filename,
                'lineno': lineno,
                'function': None,  # Would need more complex stack inspection
                'stack_trace': None
            })

        # Set up warning capture
        warnings.showwarning = warning_handler

        # Also capture Streamlit-specific warnings
        self._patch_streamlit_warnings()

    def _patch_streamlit_warnings(self):
        """Patch Streamlit to capture its internal warnings."""
        try:
            import streamlit as st

            # Monkey patch streamlit's warning functions
            original_warning = st.warning
            def patched_warning(message, *args, **kwargs):
                self._capture_warning({
                    'message': str(message),
                    'category': 'StreamlitWarning',
                    'filename': 'streamlit_ui',
                    'lineno': None,
                    'function': 'st.warning',
                    'stack_trace': None
                })
                return original_warning(message, *args, **kwargs)

            st.warning = patched_warning

            # Capture deprecation warnings from Streamlit
            if hasattr(st, '_get_logger'):
                streamlit_logger = st._get_logger()
                self._add_streamlit_handler(streamlit_logger)

        except Exception as e:
            self.logger.error(f"Failed to patch Streamlit warnings: {e}")

    def _add_streamlit_handler(self, streamlit_logger):
        """Add handler to capture Streamlit's internal logging."""
        class StreamlitWarningHandler(logging.Handler):
            def __init__(self, monitor):
                super().__init__()
                self.monitor = monitor

            def emit(self, record):
                if record.levelno >= logging.WARNING:
                    self.monitor._capture_warning({
                        'message': record.getMessage(),
                        'category': 'StreamlitInternal',
                        'filename': record.filename,
                        'lineno': record.lineno,
                        'function': record.funcName,
                        'stack_trace': None
                    })

        handler = StreamlitWarningHandler(self)
        streamlit_logger.addHandler(handler)

    def _capture_warning(self, warning_data: Dict[str, Any]):
        """Capture and store a warning."""
        try:
            # Get session info if in Streamlit context
            session_id = None
            user_agent = None
            try:
                if hasattr(st, 'session_state') and 'session_id' in st.session_state:
                    session_id = st.session_state.session_id
                import streamlit.web.server.server_util as server_util
                if hasattr(server_util, 'get_current_session'):
                    session = server_util.get_current_session()
                    if session:
                        user_agent = getattr(session, 'client', {}).get('user_agent', '')
            except:
                pass

            # Get Streamlit version
            streamlit_version = None
            try:
                import streamlit as st
                streamlit_version = st.__version__
            except:
                pass

            # Prepare warning record
            warning_record = {
                'timestamp': datetime.now().isoformat(),
                'category': warning_data.get('category', 'Unknown'),
                'message': warning_data.get('message', ''),
                'filename': warning_data.get('filename'),
                'lineno': warning_data.get('lineno'),
                'function': warning_data.get('function'),
                'stack_trace': warning_data.get('stack_trace'),
                'session_id': session_id,
                'user_agent': user_agent,
                'streamlit_version': streamlit_version,
                'severity': self._determine_severity(warning_data)
            }

            # Store in database
            self._store_warning(warning_record)

            # Log to file
            self.logger.warning(
                f"[{warning_record['category']}] {warning_record['message']} "
                f"(file: {warning_record['filename']}, line: {warning_record['lineno']})"
            )

        except Exception as e:
            # Fallback logging if database fails
            print(f"Warning capture failed: {e}", file=sys.stderr)

    def _determine_severity(self, warning_data: Dict[str, Any]) -> str:
        """Determine warning severity."""
        message = warning_data.get('message', '').lower()
        category = warning_data.get('category', '').lower()

        if 'deprecat' in message or 'deprecat' in category:
            return 'deprecation'
        elif 'error' in message or 'fail' in message:
            return 'error'
        elif 'warn' in message:
            return 'warning'
        else:
            return 'info'

    def _store_warning(self, warning_record: Dict[str, Any]):
        """Store warning in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO warnings
                (timestamp, category, message, filename, lineno, function,
                 stack_trace, session_id, user_agent, streamlit_version, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                warning_record['timestamp'],
                warning_record['category'],
                warning_record['message'],
                warning_record['filename'],
                warning_record['lineno'],
                warning_record['function'],
                warning_record['stack_trace'],
                warning_record['session_id'],
                warning_record['user_agent'],
                warning_record['streamlit_version'],
                warning_record['severity']
            ))

    def get_warnings(self, limit: int = 100, resolved: bool = None,
                    category: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get warnings from database."""
        query = "SELECT * FROM warnings WHERE 1=1"
        params = []

        if resolved is not None:
            query += " AND resolved = ?"
            params.append(resolved)

        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def mark_resolved(self, warning_id: int, notes: str = None):
        """Mark a warning as resolved."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE warnings
                SET resolved = TRUE, resolved_at = ?, notes = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), notes, warning_id))

    def get_warning_stats(self) -> Dict[str, Any]:
        """Get warning statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}

            # Total warnings
            cursor = conn.execute("SELECT COUNT(*) FROM warnings")
            stats['total'] = cursor.fetchone()[0]

            # Unresolved warnings
            cursor = conn.execute("SELECT COUNT(*) FROM warnings WHERE resolved = FALSE")
            stats['unresolved'] = cursor.fetchone()[0]

            # By category
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM warnings
                GROUP BY category
                ORDER BY count DESC
            """)
            stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}

            # By severity
            cursor = conn.execute("""
                SELECT severity, COUNT(*) as count
                FROM warnings
                GROUP BY severity
                ORDER BY count DESC
            """)
            stats['by_severity'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Recent warnings (last 24 hours)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE timestamp > datetime('now', '-1 day')
            """)
            stats['recent_24h'] = cursor.fetchone()[0]

            return stats

# Global monitor instance
_monitor = None

def get_monitor() -> StreamlitWarningMonitor:
    """Get the global warning monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = StreamlitWarningMonitor()
    return _monitor

def initialize_warning_monitor():
    """Initialize the warning monitor. Call this at app startup."""
    monitor = get_monitor()
    return monitor

def log_custom_warning(message: str, category: str = "Custom", severity: str = "warning"):
    """Log a custom warning manually."""
    monitor = get_monitor()
    monitor._capture_warning({
        'message': message,
        'category': category,
        'filename': None,
        'lineno': None,
        'function': None,
        'stack_trace': None
    })

# Initialize on import
if __name__ != "__main__":
    initialize_warning_monitor()