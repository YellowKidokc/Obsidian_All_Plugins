r"""
AUTO-LINKER TAB v3.0
====================
Redesigned UI with:
  - Shorter status log (compact)
  - Taller review table
  - Columns reordered: Found Count | Target Link | Key Term | Apply
  - Slide toggle (green=apply, red=ignore) instead of checkbox
  - Ignored terms management panel (collapsible)
  - HTML footnote output mode (for faiththruphysics.com articles)
  - Dual mode: Obsidian wikilinks OR HTML footnote references

For: O:\999_IGNORE\Python_Backend_Dashboards\ui\tabs\
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QGroupBox, QCheckBox, QFileDialog, QSlider,
    QSplitter, QFrame, QScrollArea, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QFont

if TYPE_CHECKING:
    from auto_linker_v2 import AutoLinkerStateManager

# ─── CUSTOM SLIDE TOGGLE WIDGET ───

class SlideToggle(QWidget):
    """A smooth slide toggle — green (right) = apply, red (left) = ignore."""
    
    toggled = Signal(bool)
    
    def __init__(self, checked=True, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._handle_pos = 1.0 if checked else 0.0
        self.setFixedSize(44, 22)
        self.setCursor(Qt.PointingHandCursor)
        
        self._animation = QPropertyAnimation(self, b"handle_pos")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, val):
        self._checked = val
        self._animate(val)
    
    def _animate(self, checked):
        self._animation.setStartValue(self._handle_pos)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()
    
    @property
    def handle_pos(self):
        return self._handle_pos
    
    @handle_pos.setter
    def handle_pos(self, val):
        self._handle_pos = val
        self.update()
    
    # Make handle_pos a Qt property for animation
    handle_pos = property(fget=lambda self: self._handle_pos, fset=lambda self, v: (setattr(self, '_handle_pos', v), self.update()))
    
    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animate(self._checked)
        self.toggled.emit(self._checked)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        r = h // 2
        
        # Track color: interpolate red → green
        t = self._handle_pos
        track_r = int(244 * (1 - t) + 78 * t)
        track_g = int(71 * (1 - t) + 201 * t)
        track_b = int(71 * (1 - t) + 176 * t)
        p.setBrush(QColor(track_r, track_g, track_b))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, r, r)
        
        # Handle
        handle_x = int(2 + self._handle_pos * (w - h))
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(handle_x, 2, h - 4, h - 4)
        
        p.end()


# ─── MAIN TAB ───

class AutoLinkerTabV3(QWidget):
    """Auto-Linker & Entity Extraction — v3 UI"""
    
    def __init__(self, state_manager=None):
        super().__init__()
        self.state_manager = state_manager
        self.scan_results: List[Dict] = []
        self.ignored_terms: Dict[str, Dict] = {}  # term -> {reason, timestamp, source}
        self.output_mode = "obsidian"  # "obsidian" or "html"
        
        self._load_ignored()
        self._setup_ui()
    
    def _load_ignored(self):
        """Load permanently ignored terms from disk."""
        ignore_file = Path("data/ignored_terms.json")
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r') as f:
                    self.ignored_terms = json.load(f)
            except:
                self.ignored_terms = {}
    
    def _save_ignored(self):
        """Persist ignored terms."""
        Path("data").mkdir(exist_ok=True)
        with open("data/ignored_terms.json", 'w') as f:
            json.dump(self.ignored_terms, f, indent=2)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # ── HEADER ──
        header = QLabel("🔗  Auto-Linker & Entity Extraction")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d9ff;")
        layout.addWidget(header)
        
        desc = QLabel("Scan files for key terms, link to glossary/SEP/Wikipedia. "
                       "Slide right (green) to apply, left (red) to ignore permanently.")
        desc.setStyleSheet("color: #888; font-size: 12px; margin-bottom: 8px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        # ── SCAN CONFIG ──
        config_group = QGroupBox("1. Scan Configuration")
        config_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; border: 1px solid #2a2a2a; border-radius: 6px; padding-top: 16px; margin-top: 8px; }")
        config_layout = QVBoxLayout(config_group)
        
        # Path row
        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select folder to scan...")
        self.path_input.setStyleSheet("padding: 8px; border-radius: 4px; border: 1px solid #3a3a3a; background: #1a1a1a; color: #fff;")
        path_row.addWidget(self.path_input)
        
        browse_btn = QPushButton("📁 Browse...")
        browse_btn.setStyleSheet("padding: 8px 16px; background: #00d9ff; color: #000; border-radius: 4px; font-weight: bold;")
        browse_btn.clicked.connect(self._browse_folder)
        path_row.addWidget(browse_btn)
        config_layout.addLayout(path_row)
        
        # Options row
        opts_row = QHBoxLayout()
        self.chk_recursive = QCheckBox("Recursive Scan")
        self.chk_recursive.setChecked(True)
        self.chk_recursive.setStyleSheet("color: #b0b0b0;")
        opts_row.addWidget(self.chk_recursive)
        
        self.chk_first_only = QCheckBox("Link First Only")
        self.chk_first_only.setChecked(False)
        self.chk_first_only.setStyleSheet("color: #b0b0b0;")
        opts_row.addWidget(self.chk_first_only)
        
        self.chk_wiki_fallback = QCheckBox("Wikipedia fallback")
        self.chk_wiki_fallback.setChecked(True)
        self.chk_wiki_fallback.setStyleSheet("color: #b0b0b0;")
        opts_row.addWidget(self.chk_wiki_fallback)
        
        self.chk_sep = QCheckBox("SEP links")
        self.chk_sep.setChecked(True)
        self.chk_sep.setStyleSheet("color: #b0b0b0;")
        opts_row.addWidget(self.chk_sep)
        
        opts_row.addStretch()
        config_layout.addLayout(opts_row)
        
        # Output mode row
        mode_row = QHBoxLayout()
        mode_label = QLabel("Output Mode:")
        mode_label.setStyleSheet("color: #888;")
        mode_row.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Obsidian (wikilinks)", "HTML (footnote references)"])
        self.mode_combo.setStyleSheet("padding: 4px 8px; background: #1a1a1a; color: #fff; border: 1px solid #3a3a3a; border-radius: 4px;")
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        mode_row.addWidget(self.mode_combo)
        
        min_label = QLabel("Min occurrences:")
        min_label.setStyleSheet("color: #888; margin-left: 16px;")
        mode_row.addWidget(min_label)
        
        self.min_input = QLineEdit("4")
        self.min_input.setFixedWidth(40)
        self.min_input.setStyleSheet("padding: 4px; background: #1a1a1a; color: #fff; border: 1px solid #3a3a3a; border-radius: 4px; text-align: center;")
        mode_row.addWidget(self.min_input)
        
        mode_row.addStretch()
        config_layout.addLayout(mode_row)
        
        # Scan button
        self.scan_btn = QPushButton("🔍 Scan for Potential Links")
        self.scan_btn.setStyleSheet("padding: 10px; background: #00d9ff; color: #000; border-radius: 6px; font-weight: bold; font-size: 14px;")
        self.scan_btn.clicked.connect(self._run_scan)
        config_layout.addWidget(self.scan_btn)
        
        layout.addWidget(config_group)
        
        # ── STATUS LOG (compact — ~3 lines visible) ──
        log_group = QGroupBox("Status Log")
        log_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; border: 1px solid #2a2a2a; border-radius: 6px; padding-top: 16px; margin-top: 4px; }")
        log_layout = QVBoxLayout(log_group)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(70)  # Compact — about 3 lines
        self.status_log.setStyleSheet("background: #0d0d0d; color: #707070; border: 1px solid #2a2a2a; border-radius: 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; padding: 6px;")
        self.status_log.setPlaceholderText("Scan logs appear here...")
        log_layout.addWidget(self.status_log)
        
        layout.addWidget(log_group)
        # ── REVIEW TABLE (tall — takes most of the space) ──
        review_group = QGroupBox("2. Review & Apply")
        review_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; border: 1px solid #2a2a2a; border-radius: 6px; padding-top: 16px; margin-top: 4px; }")
        review_layout = QVBoxLayout(review_group)
        
        # Column order: Found Count | Target Link | Key Term | Apply Toggle
        self.review_table = QTableWidget()
        self.review_table.setColumnCount(4)
        self.review_table.setHorizontalHeaderLabels(["Found Count", "Target Link", "Key Term", "Apply?"])
        self.review_table.horizontalHeader().setStyleSheet("color: #00d9ff; font-weight: bold; font-size: 11px;")
        self.review_table.setStyleSheet("""
            QTableWidget { background: #0d0d0d; border: 1px solid #2a2a2a; border-radius: 4px; gridline-color: #1a1a1a; }
            QTableWidget::item { padding: 6px 8px; color: #e0e0e0; border-bottom: 1px solid #1a1a1a; }
            QTableWidget::item:selected { background: #0f3460; }
            QHeaderView::section { background: #141414; color: #00d9ff; padding: 8px; border: none; border-bottom: 2px solid #00d9ff; font-weight: bold; }
        """)
        self.review_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.review_table.setAlternatingRowColors(True)
        self.review_table.setMinimumHeight(300)
        
        # Column widths
        header = self.review_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # Found Count
        header.setSectionResizeMode(1, QHeaderView.Stretch)    # Target Link
        header.setSectionResizeMode(2, QHeaderView.Stretch)    # Key Term
        header.setSectionResizeMode(3, QHeaderView.Fixed)      # Apply toggle
        self.review_table.setColumnWidth(0, 90)
        self.review_table.setColumnWidth(3, 70)
        
        review_layout.addWidget(self.review_table)
        
        # Action buttons
        btn_row = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Apply Selected Links")
        apply_btn.setStyleSheet("padding: 8px 20px; background: #4ec9b0; color: #000; border-radius: 4px; font-weight: bold;")
        apply_btn.clicked.connect(self._apply_links)
        btn_row.addWidget(apply_btn)
        
        apply_all_btn = QPushButton("⚡ Apply All Green")
        apply_all_btn.setStyleSheet("padding: 8px 20px; background: #007acc; color: #fff; border-radius: 4px; font-weight: bold;")
        apply_all_btn.clicked.connect(self._apply_all_green)
        btn_row.addWidget(apply_all_btn)
        
        ignore_all_red = QPushButton("🚫 Ignore All Red")
        ignore_all_red.setStyleSheet("padding: 8px 20px; background: #f44747; color: #fff; border-radius: 4px; font-weight: bold;")
        ignore_all_red.clicked.connect(self._ignore_all_red)
        btn_row.addWidget(ignore_all_red)
        
        btn_row.addStretch()
        
        export_btn = QPushButton("📄 Export HTML Footnotes")
        export_btn.setStyleSheet("padding: 8px 16px; background: #1a1a1a; color: #00d9ff; border: 1px solid #00d9ff; border-radius: 4px;")
        export_btn.clicked.connect(self._export_html_footnotes)
        btn_row.addWidget(export_btn)
        
        review_layout.addLayout(btn_row)
        layout.addWidget(review_group, stretch=3)  # Takes 3x the space
        
        # ── IGNORED TERMS PANEL (collapsible) ──
        self.ignored_group = QGroupBox(f"⊘ Ignored Terms ({len(self.ignored_terms)})")
        self.ignored_group.setCheckable(True)
        self.ignored_group.setChecked(False)  # Collapsed by default
        self.ignored_group.setStyleSheet("""
            QGroupBox { color: #f44747; font-weight: bold; border: 1px solid #2a2a2a; border-radius: 6px; padding-top: 16px; margin-top: 4px; }
            QGroupBox::indicator:unchecked { border: 1px solid #3a3a3a; background: #1a1a1a; }
            QGroupBox::indicator:checked { border: 1px solid #f44747; background: #2a1515; }
        """)
        ignored_layout = QVBoxLayout(self.ignored_group)
        
        self.ignored_table = QTableWidget()
        self.ignored_table.setColumnCount(4)
        self.ignored_table.setHorizontalHeaderLabels(["Term", "Source", "Ignored On", "Restore"])
        self.ignored_table.setStyleSheet("QTableWidget { background: #0d0d0d; border: 1px solid #2a2a2a; } QTableWidget::item { color: #888; }")
        self.ignored_table.setMaximumHeight(150)
        self.ignored_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ignored_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ignored_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ignored_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.ignored_table.setColumnWidth(3, 70)
        ignored_layout.addWidget(self.ignored_table)
        
        self._refresh_ignored_table()
        layout.addWidget(self.ignored_group)
    # ─── METHODS ───
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder:
            self.path_input.setText(folder)
    
    def _mode_changed(self, index):
        self.output_mode = "obsidian" if index == 0 else "html"
        self._log(f"Output mode: {self.output_mode}")
    
    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_log.append(f"[{timestamp}] {msg}")
        # Auto-scroll to bottom
        self.status_log.verticalScrollBar().setValue(
            self.status_log.verticalScrollBar().maximum())
    
    def _run_scan(self):
        """Scan the selected folder for key terms."""
        folder = self.path_input.text()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "No Folder", "Select a valid folder first.")
            return
        
        min_count = int(self.min_input.text() or "4")
        recursive = self.chk_recursive.isChecked()
        
        self._log(f"Scanning: {folder} (min={min_count}, recursive={recursive})")
        self.scan_btn.setText("⏳ Scanning...")
        self.scan_btn.setEnabled(False)
        
        try:
            # Collect all markdown/html files
            files = []
            pattern = "**/*" if recursive else "*"
            for ext in ['.md', '.html', '.htm', '.txt']:
                files.extend(Path(folder).glob(f"{pattern}{ext}"))
            
            self._log(f"Found {len(files)} files")
            
            # Load glossary terms
            glossary_terms = self._load_glossary_terms()
            self._log(f"Loaded {len(glossary_terms)} glossary terms")
            
            # Scan for term occurrences
            results = []
            for term, link_info in glossary_terms.items():
                # Skip ignored terms
                if term.lower() in {k.lower() for k in self.ignored_terms}:
                    continue
                
                count = 0
                for fpath in files:
                    try:
                        content = fpath.read_text(encoding='utf-8', errors='replace').lower()
                        count += content.count(term.lower())
                    except:
                        continue
                
                if count >= min_count:
                    results.append({
                        'term': term,
                        'count': count,
                        'link': link_info.get('url', ''),
                        'source': link_info.get('source', 'glossary'),
                        'apply': True  # Default to green/apply
                    })
            
            # Sort by count descending
            results.sort(key=lambda x: x['count'], reverse=True)
            self.scan_results = results
            
            self._log(f"Found {len(results)} terms above threshold")
            self._populate_review_table()
            
        except Exception as e:
            self._log(f"ERROR: {e}")
        finally:
            self.scan_btn.setText("🔍 Scan for Potential Links")
            self.scan_btn.setEnabled(True)
    
    def _load_glossary_terms(self) -> Dict:
        """Load terms from glossary, SEP, Wikipedia sources."""
        terms = {}
        
        # 1. Theophysics glossary (highest priority)
        glossary_dir = Path(r"O:\_Theophysics_v5\00_Canonical\Glossary")
        if glossary_dir.exists():
            for f in glossary_dir.glob("*.md"):
                name = f.stem
                if name.startswith('_') or name.startswith('00'):
                    continue
                # Strip _Canonical suffix for display
                display = name.replace('_Canonical', '').replace('_', ' ')
                url = f"https://faiththruphysics.com/glossary#{display.lower().replace(' ', '-')}"
                terms[display] = {'url': url, 'source': 'Theophysics Glossary', 'file': str(f)}
        
        # 2. SEP entries
        if self.chk_sep.isChecked():
            sep_dir = glossary_dir / "SEP" if glossary_dir.exists() else None
            if sep_dir and sep_dir.exists():
                for f in sep_dir.glob("*.md"):
                    name = f.stem.replace(' (SEP)', '')
                    sep_slug = name.lower().replace(' ', '-').replace("'", '')
                    url = f"https://plato.stanford.edu/entries/{sep_slug}/"
                    terms[name] = {'url': url, 'source': 'Stanford Encyclopedia'}
        
        # 3. Wikipedia fallback (only for terms not in glossary/SEP)
        if self.chk_wiki_fallback.isChecked():
            # Common physics/theology terms that might not be in the glossary
            wiki_terms = {
                'Hilbert Space': 'https://en.wikipedia.org/wiki/Hilbert_space',
                'Planck Length': 'https://en.wikipedia.org/wiki/Planck_length',
                'Renormalization': 'https://en.wikipedia.org/wiki/Renormalization',
                'Eigenstate': 'https://en.wikipedia.org/wiki/Eigenstate',
                'Hamiltonian': 'https://en.wikipedia.org/wiki/Hamiltonian_(quantum_mechanics)',
                'Lagrangian': 'https://en.wikipedia.org/wiki/Lagrangian_mechanics',
                'Schrödinger Equation': 'https://en.wikipedia.org/wiki/Schr%C3%B6dinger_equation',
                'Klein-Gordon': 'https://en.wikipedia.org/wiki/Klein%E2%80%93Gordon_equation',
                'Noether Theorem': 'https://en.wikipedia.org/wiki/Noether%27s_theorem',
                'Born Rule': 'https://en.wikipedia.org/wiki/Born_rule',
                'Bell Inequality': 'https://en.wikipedia.org/wiki/Bell%27s_theorem',
                'EPR Paradox': 'https://en.wikipedia.org/wiki/EPR_paradox',
                'Bekenstein Bound': 'https://en.wikipedia.org/wiki/Bekenstein_bound',
                'Hawking Radiation': 'https://en.wikipedia.org/wiki/Hawking_radiation',
                'Perichoresis': 'https://en.wikipedia.org/wiki/Perichoresis',
                'Soteriology': 'https://en.wikipedia.org/wiki/Soteriology',
                'Eschatology': 'https://en.wikipedia.org/wiki/Eschatology',
                'Pneumatology': 'https://en.wikipedia.org/wiki/Pneumatology',
                'Christology': 'https://en.wikipedia.org/wiki/Christology',
            }
            for term, url in wiki_terms.items():
                if term not in terms:
                    terms[term] = {'url': url, 'source': 'Wikipedia'}
        
        return terms
    
    def _populate_review_table(self):
        """Fill the review table with scan results + slide toggles."""
        self.review_table.setRowCount(len(self.scan_results))
        self._toggles = []  # Keep references to toggle widgets
        
        for i, result in enumerate(self.scan_results):
            # Column 0: Found Count (center-aligned)
            count_item = QTableWidgetItem(str(result['count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            count_item.setForeground(QColor("#00d9ff"))
            count_item.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
            self.review_table.setItem(i, 0, count_item)
            
            # Column 1: Target Link
            link_item = QTableWidgetItem(result['link'])
            link_item.setForeground(QColor("#4ec9b0"))
            link_item.setFont(QFont("JetBrains Mono", 9))
            link_item.setToolTip(f"Source: {result['source']}")
            self.review_table.setItem(i, 1, link_item)
            
            # Column 2: Key Term
            term_item = QTableWidgetItem(result['term'])
            term_item.setForeground(QColor("#ffffff"))
            term_item.setFont(QFont("DM Sans", 11))
            self.review_table.setItem(i, 2, term_item)
            
            # Column 3: Slide Toggle
            toggle = SlideToggle(checked=result.get('apply', True))
            toggle.toggled.connect(lambda checked, idx=i: self._toggle_changed(idx, checked))
            self._toggles.append(toggle)
            
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(12, 2, 12, 2)
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(toggle)
            self.review_table.setCellWidget(i, 3, container)
            
            self.review_table.setRowHeight(i, 36)
    
    def _toggle_changed(self, idx, checked):
        """Handle slide toggle change."""
        if idx < len(self.scan_results):
            self.scan_results[idx]['apply'] = checked
    def _apply_links(self):
        """Apply links for selected (green) terms only."""
        to_apply = [r for r in self.scan_results if r.get('apply', True)]
        if not to_apply:
            QMessageBox.information(self, "Nothing Selected", "No terms are toggled to apply.")
            return
        
        self._log(f"Applying {len(to_apply)} links in {self.output_mode} mode...")
        
        if self.output_mode == "html":
            self._apply_html_footnotes(to_apply)
        else:
            self._apply_obsidian_links(to_apply)
    
    def _apply_all_green(self):
        """Apply all green-toggled terms."""
        self._apply_links()
    
    def _ignore_all_red(self):
        """Move all red-toggled terms to the permanent ignore list."""
        to_ignore = [r for r in self.scan_results if not r.get('apply', True)]
        if not to_ignore:
            QMessageBox.information(self, "Nothing to Ignore", "No terms are toggled red.")
            return
        
        for r in to_ignore:
            self.ignored_terms[r['term']] = {
                'source': r.get('source', ''),
                'link': r.get('link', ''),
                'timestamp': datetime.now().isoformat(),
                'reason': 'User toggled red'
            }
        
        self._save_ignored()
        self._refresh_ignored_table()
        self.ignored_group.setTitle(f"⊘ Ignored Terms ({len(self.ignored_terms)})")
        
        # Remove from scan results
        self.scan_results = [r for r in self.scan_results if r.get('apply', True)]
        self._populate_review_table()
        
        self._log(f"Ignored {len(to_ignore)} terms permanently")
    
    def _refresh_ignored_table(self):
        """Refresh the ignored terms panel."""
        self.ignored_table.setRowCount(len(self.ignored_terms))
        
        for i, (term, info) in enumerate(sorted(self.ignored_terms.items())):
            self.ignored_table.setItem(i, 0, QTableWidgetItem(term))
            self.ignored_table.setItem(i, 1, QTableWidgetItem(info.get('source', '')))
            
            ts = info.get('timestamp', '')
            if ts:
                try:
                    ts = datetime.fromisoformat(ts).strftime("%Y-%m-%d")
                except:
                    pass
            self.ignored_table.setItem(i, 2, QTableWidgetItem(ts))
            
            # Restore button
            restore_btn = QPushButton("↩️")
            restore_btn.setFixedSize(32, 28)
            restore_btn.setStyleSheet("background: #1a1a1a; border: 1px solid #3a3a3a; border-radius: 4px; color: #4ec9b0;")
            restore_btn.setToolTip(f"Restore '{term}' to active scanning")
            restore_btn.clicked.connect(lambda _, t=term: self._restore_term(t))
            
            container = QWidget()
            cl = QHBoxLayout(container)
            cl.setContentsMargins(4, 0, 4, 0)
            cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(restore_btn)
            self.ignored_table.setCellWidget(i, 3, container)
    
    def _restore_term(self, term):
        """Restore an ignored term back to active scanning."""
        if term in self.ignored_terms:
            del self.ignored_terms[term]
            self._save_ignored()
            self._refresh_ignored_table()
            self.ignored_group.setTitle(f"⊘ Ignored Terms ({len(self.ignored_terms)})")
            self._log(f"Restored: {term}")
    
    def _apply_obsidian_links(self, terms):
        """Insert wikilinks into markdown files."""
        folder = self.path_input.text()
        if not folder:
            return
        
        first_only = self.chk_first_only.isChecked()
        count = 0
        
        for fpath in Path(folder).rglob("*.md") if self.chk_recursive.isChecked() else Path(folder).glob("*.md"):
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
                modified = False
                
                for t in terms:
                    term = t['term']
                    # Don't link inside existing links, headers, or code blocks
                    import re
                    pattern = rf'(?<!\[\[)(?<!\|)(?<!#)\b({re.escape(term)})\b(?!\]\])(?!\|)'
                    
                    if first_only:
                        new_content, n = re.subn(pattern, f'[[{term}]]', content, count=1)
                    else:
                        new_content, n = re.subn(pattern, f'[[{term}]]', content)
                    
                    if n > 0:
                        content = new_content
                        modified = True
                        count += n
                
                if modified:
                    fpath.write_text(content, encoding='utf-8')
                    
            except Exception as e:
                self._log(f"Error processing {fpath.name}: {e}")
        
        self._log(f"Applied {count} wikilinks across files")
        QMessageBox.information(self, "Done", f"Applied {count} wikilinks.")
    
    def _apply_html_footnotes(self, terms):
        """Insert footnote-style references into HTML files.
        
        Converts: "Bell's theorem proves..."
        Into:     "Bell's theorem<sup><a href='#fn-1'>[1]</a></sup> proves..."
        
        And appends a <section class='footnotes'> at the bottom with full links.
        """
        folder = self.path_input.text()
        if not folder:
            return
        
        count = 0
        for fpath in Path(folder).rglob("*.html") if self.chk_recursive.isChecked() else Path(folder).glob("*.html"):
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
                footnotes = []
                fn_num = 1
                modified = False
                
                for t in terms:
                    term = t['term']
                    link = t['link']
                    source = t.get('source', '')
                    
                    import re
                    # Match term not already in a link or sup tag
                    pattern = rf'(?<!<a[^>]*>)(?<!<sup>)\b({re.escape(term)})\b(?!</a>)(?!</sup>)'
                    
                    match = re.search(pattern, content)
                    if match:
                        sup = f'<sup class="fn-ref"><a href="#fn-{fn_num}" id="fnref-{fn_num}">[{fn_num}]</a></sup>'
                        content = content[:match.end()] + sup + content[match.end():]
                        footnotes.append({
                            'num': fn_num,
                            'term': term,
                            'link': link,
                            'source': source
                        })
                        fn_num += 1
                        modified = True
                        count += 1
                
                if modified and footnotes:
                    # Build footnotes section
                    fn_html = '\n<section class="footnotes" style="border-top:1px solid rgba(201,168,76,0.15);margin-top:40px;padding-top:20px;">\n'
                    fn_html += '  <h3 style="font-family:\'Cormorant Garamond\',serif;font-size:18px;color:#c9a84c;margin-bottom:12px;">References & Further Reading</h3>\n'
                    fn_html += '  <ol style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#9a9690;line-height:2;">\n'
                    
                    for fn in footnotes:
                        fn_html += f'    <li id="fn-{fn["num"]}">{fn["term"]} — '
                        fn_html += f'<a href="{fn["link"]}" target="_blank" rel="noopener" style="color:#4a7fb5;">{fn["source"]}</a> '
                        fn_html += f'<a href="#fnref-{fn["num"]}" style="color:#5a5752;">↩</a></li>\n'
                    
                    fn_html += '  </ol>\n</section>\n'
                    
                    # Insert before </body> or </main> or at end
                    if '</body>' in content:
                        content = content.replace('</body>', fn_html + '</body>')
                    elif '</main>' in content:
                        content = content.replace('</main>', fn_html + '</main>')
                    else:
                        content += fn_html
                    
                    # Add footnote CSS if not present
                    if '.fn-ref' not in content:
                        fn_css = '<style>.fn-ref a{color:#c9a84c;text-decoration:none;font-size:10px;vertical-align:super;}.fn-ref a:hover{color:#e8c86c;}</style>\n'
                        if '</head>' in content:
                            content = content.replace('</head>', fn_css + '</head>')
                    
                    fpath.write_text(content, encoding='utf-8')
                    self._log(f"Added {len(footnotes)} footnotes to {fpath.name}")
                    
            except Exception as e:
                self._log(f"Error processing {fpath.name}: {e}")
        
        self._log(f"Applied {count} footnote references across HTML files")
        QMessageBox.information(self, "Done", f"Applied {count} HTML footnote references.")
    
    def _export_html_footnotes(self):
        """Export current green terms as a standalone footnotes HTML snippet."""
        to_export = [r for r in self.scan_results if r.get('apply', True)]
        if not to_export:
            QMessageBox.information(self, "Nothing to Export", "No green terms to export.")
            return
        
        html = '<section class="footnotes">\n'
        html += '  <h3>References & Further Reading</h3>\n  <ol>\n'
        for i, r in enumerate(to_export, 1):
            html += f'    <li><strong>{r["term"]}</strong> — <a href="{r["link"]}" target="_blank">{r.get("source", "Reference")}</a> (found {r["count"]}×)</li>\n'
        html += '  </ol>\n</section>'
        
        # Copy to clipboard
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(html)
        self._log(f"Exported {len(to_export)} footnotes to clipboard")
        QMessageBox.information(self, "Copied", f"HTML footnotes copied to clipboard ({len(to_export)} references).")
