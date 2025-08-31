#!/usr/bin/env python3
"""
PyQt-based Poem Editor with Better Burmese Support
Alternative to tkinter with proper Burmese keyboard input
"""

import sys
import os
import json
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton, 
                            QFileDialog, QMessageBox, QSplitter, QScrollArea,
                            QGridLayout, QFrame, QGroupBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QIcon, QPalette, QColor
import fitz  # PyMuPDF
from PIL import Image
from datetime import datetime

class BurmesePoemEditor(QMainWindow):
    """PyQt-based poem editor with proper Burmese text support"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Burmese Poem Editor - Enhanced Version")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize data
        self.current_poems = []
        self.current_poem_index = 0
        self.current_pdf_path = None
        self.pdf_doc = None
        self.current_pdf_page = 0
        self.pdf_zoom_factor = 1.5  # Default zoom
        self.settings_file = "poem_editor_settings.json"
        self.current_json_data = None  # Store the entire loaded JSON data
        self.working_json_data = None  # Temporary working copy of JSON data
        self.original_json_path = None  # Path to the original JSON file
        self.edited_save_path = None  # Path where edited poems will be saved
        
        # Apply modern styling
        self.apply_modern_style()
        
        # Setup UI
        self.setup_ui()
        
        # Set Burmese font for better text rendering
        burmese_font = QFont("Myanmar Text", 11)
        self.setFont(burmese_font)
        
        # Load settings and restore last position
        self.load_settings()

        # Set default save path for edited poems
        self.set_default_save_path()

    def set_default_save_path(self):
        """Set default save path for edited poems"""
        if os.path.exists("PoemJsonFiles"):
            self.edited_save_path = "PoemJsonFiles/Edited"
        else:
            self.edited_save_path = "EditedPoems"

        # Create directory if it doesn't exist
        if not os.path.exists(self.edited_save_path):
            os.makedirs(self.edited_save_path)
            self.update_status(f"Created save directory: {self.edited_save_path}")

    def apply_modern_style(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #357abd;
            }
            
            QPushButton:pressed {
                background-color: #2868a0;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 11px;
            }
            
            QLineEdit:focus {
                border-color: #4a90e2;
            }
            
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-family: "Myanmar Text";
                font-size: 20px;
            }
            
            QTextEdit:focus {
                border-color: #4a90e2;
            }
            
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4a90e2;
                font-size: 12px;
            }
            
            QScrollArea {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            
            QFrame {
                background-color: white;
                border-radius: 6px;
            }
        """)
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with margins
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Control panel
        self.setup_control_panel(main_layout)
        
        # Navigation panel
        self.setup_navigation_panel(main_layout)
        
        # Main content area
        self.setup_content_area(main_layout)
        
    def setup_control_panel(self, parent_layout):
        """Setup control buttons"""
        control_group = QGroupBox("File Operations")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        # Load JSON button
        self.load_json_btn = QPushButton("📄 Load JSON File")
        self.load_json_btn.clicked.connect(self.load_json_files)
        self.load_json_btn.setMinimumHeight(40)
        control_layout.addWidget(self.load_json_btn)
        
        # Select PDF button
        self.select_pdf_btn = QPushButton("📄 Select PDF File")
        self.select_pdf_btn.clicked.connect(self.select_pdf_file)
        self.select_pdf_btn.setMinimumHeight(40)
        control_layout.addWidget(self.select_pdf_btn)
        
        # Save edits button
        self.save_edits_btn = QPushButton("💾 Save Edits")
        self.save_edits_btn.clicked.connect(self.save_edits)
        self.save_edits_btn.setMinimumHeight(40)
        control_layout.addWidget(self.save_edits_btn)
        
        # Spacer
        control_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Info panel
        info_layout = QVBoxLayout()
        
        # PDF info label
        self.pdf_info_label = QLabel("No PDF selected")
        self.pdf_info_label.setStyleSheet("color: #666666; font-weight: normal;")
        info_layout.addWidget(self.pdf_info_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #4a90e2; font-weight: normal;")
        info_layout.addWidget(self.status_label)
        
        control_layout.addLayout(info_layout)
        
        parent_layout.addWidget(control_group)
        
    def setup_navigation_panel(self, parent_layout):
        """Setup navigation controls"""
        nav_group = QGroupBox("Navigation")
        nav_layout = QHBoxLayout(nav_group)
        nav_layout.setSpacing(10)
        
        # Poem navigation section
        poem_nav_layout = QHBoxLayout()
        
        self.prev_poem_btn = QPushButton("⬅️ Previous Poem")
        self.prev_poem_btn.clicked.connect(self.previous_poem)
        self.prev_poem_btn.setMinimumHeight(35)
        poem_nav_layout.addWidget(self.prev_poem_btn)
        
        self.next_poem_btn = QPushButton("Next Poem ➡️")
        self.next_poem_btn.clicked.connect(self.next_poem)
        self.next_poem_btn.setMinimumHeight(35)
        poem_nav_layout.addWidget(self.next_poem_btn)
        
        self.poem_info_label = QLabel("No poems loaded")
        self.poem_info_label.setStyleSheet("color: #666666; font-weight: normal; margin: 0 10px;")
        poem_nav_layout.addWidget(self.poem_info_label)
        
        nav_layout.addLayout(poem_nav_layout)
        
        # Spacer
        nav_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # PDF page navigation section
        pdf_nav_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("◀ Prev Page")
        self.prev_page_btn.clicked.connect(self.prev_pdf_page)
        self.prev_page_btn.setMinimumHeight(35)
        pdf_nav_layout.addWidget(self.prev_page_btn)
        
        self.next_page_btn = QPushButton("Next Page ▶")
        self.next_page_btn.clicked.connect(self.next_pdf_page)
        self.next_page_btn.setMinimumHeight(35)
        pdf_nav_layout.addWidget(self.next_page_btn)
        
        self.page_label = QLabel("Page: -")
        self.page_label.setStyleSheet("color: #666666; font-weight: normal; margin: 0 10px;")
        pdf_nav_layout.addWidget(self.page_label)
        
        # Page input
        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(60)
        self.page_input.setMinimumHeight(30)
        self.page_input.setPlaceholderText("Page #")
        self.page_input.returnPressed.connect(self.go_to_page)
        pdf_nav_layout.addWidget(self.page_input)
        
        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self.go_to_page)
        go_btn.setMinimumHeight(30)
        go_btn.setMaximumWidth(40)
        pdf_nav_layout.addWidget(go_btn)
        
        nav_layout.addLayout(pdf_nav_layout)
        
        parent_layout.addWidget(nav_group)
        
    def setup_content_area(self, parent_layout):
        """Setup main content area"""
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - PDF view
        self.setup_pdf_panel(splitter)
        
        # Right panel - Poem editing
        self.setup_poem_panel(splitter)
        
        # Set initial sizes (60% PDF, 40% poem)
        splitter.setSizes([960, 640])
        
        parent_layout.addWidget(splitter)
        
    def setup_pdf_panel(self, parent):
        """Setup PDF viewing panel"""
        pdf_group = QGroupBox("PDF Viewer")
        pdf_layout = QVBoxLayout(pdf_group)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        
        zoom_out_btn = QPushButton("🔍➖ Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out_pdf)
        zoom_out_btn.setMaximumWidth(120)
        zoom_layout.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("150%")
        self.zoom_label.setStyleSheet("color: #666666; font-weight: normal; margin: 0 10px;")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setMinimumWidth(60)
        zoom_layout.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("🔍➕ Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in_pdf)
        zoom_in_btn.setMaximumWidth(120)
        zoom_layout.addWidget(zoom_in_btn)
        
        reset_zoom_btn = QPushButton("🔄 Reset")
        reset_zoom_btn.clicked.connect(self.reset_zoom_pdf)
        reset_zoom_btn.setMaximumWidth(80)
        zoom_layout.addWidget(reset_zoom_btn)
        
        zoom_layout.addStretch()
        
        pdf_layout.addLayout(zoom_layout)
        
        # PDF image display
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setMinimumWidth(600)
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.pdf_label.setStyleSheet("background-color: white; border: 1px solid #e0e0e0;")
        self.pdf_scroll.setWidget(self.pdf_label)
        self.pdf_scroll.setWidgetResizable(True)
        pdf_layout.addWidget(self.pdf_scroll)
        
        parent.addWidget(pdf_group)
        
    def setup_poem_panel(self, parent):
        """Setup poem editing panel"""
        poem_group = QGroupBox("Poem Editor")
        poem_layout = QVBoxLayout(poem_group)
        poem_layout.setSpacing(15)
        
        # Metadata section
        meta_group = QGroupBox("Poem Information")
        meta_layout = QGridLayout(meta_group)
        meta_layout.setSpacing(10)
        
        # Title
        meta_layout.addWidget(QLabel("Title:"), 0, 0)
        self.title_entry = QLineEdit()
        self.title_entry.setFont(QFont("Myanmar Text", 10))
        self.title_entry.setMinimumHeight(35)
        self.title_entry.setPlaceholderText("Enter poem title...")
        meta_layout.addWidget(self.title_entry, 0, 1)
        
        # Author
        meta_layout.addWidget(QLabel("Author:"), 1, 0)
        self.author_entry = QLineEdit()
        self.author_entry.setFont(QFont("Myanmar Text", 10))
        self.author_entry.setMinimumHeight(35)
        self.author_entry.setPlaceholderText("Enter author name...")
        meta_layout.addWidget(self.author_entry, 1, 1)
        
        # Type
        meta_layout.addWidget(QLabel("Type:"), 2, 0)
        self.type_entry = QLineEdit()
        self.type_entry.setFont(QFont("Myanmar Text", 10))
        self.type_entry.setMinimumHeight(35)
        self.type_entry.setPlaceholderText("Enter poem type...")
        meta_layout.addWidget(self.type_entry, 2, 1)
        
        # Page
        meta_layout.addWidget(QLabel("Page:"), 3, 0)
        self.poem_page_entry = QLineEdit()
        self.poem_page_entry.setMaximumWidth(100)
        self.poem_page_entry.setMinimumHeight(35)
        self.poem_page_entry.setPlaceholderText("Page #")
        self.poem_page_entry.returnPressed.connect(self.sync_pdf_page)
        meta_layout.addWidget(self.poem_page_entry, 3, 1)
        
        meta_layout.setColumnStretch(1, 1)
        
        poem_layout.addWidget(meta_group)
        
        # Poem text area
        text_group = QGroupBox("Poem Content")
        text_layout = QVBoxLayout(text_group)
        
        # This is the key improvement - QTextEdit has much better Unicode support
        self.poem_text = QTextEdit()
        self.poem_text.setFont(QFont("Myanmar Text", 12))
        self.poem_text.setMinimumHeight(400)
        self.poem_text.setPlaceholderText("Enter or edit poem lines here...")
        
        # Enable proper text input methods for complex scripts
        self.poem_text.setInputMethodHints(Qt.ImhMultiLine | Qt.ImhNoPredictiveText)
        
        text_layout.addWidget(self.poem_text)
        poem_layout.addWidget(text_group)
        
        # Edit buttons
        button_group = QGroupBox("Actions")
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(10)
        
        auto_fix_btn = QPushButton("🔧 Auto-Fix OCR")
        auto_fix_btn.clicked.connect(self.auto_fix_ocr)
        auto_fix_btn.setMinimumHeight(40)
        button_layout.addWidget(auto_fix_btn)
        
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.clicked.connect(self.reset_poem)
        reset_btn.setMinimumHeight(40)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Mark as edited with status indicator
        self.mark_edited_btn = QPushButton("✅ Mark as Edited")
        self.mark_edited_btn.clicked.connect(self.mark_as_edited)
        self.mark_edited_btn.setMinimumHeight(40)
        self.update_mark_edited_button_style(False)  # Initially not edited
        button_layout.addWidget(self.mark_edited_btn)
        
        poem_layout.addWidget(button_group)
        
        parent.addWidget(poem_group)
    
    def update_mark_edited_button_style(self, is_edited):
        """Update the mark as edited button style based on edit status"""
        if is_edited:
            self.mark_edited_btn.setText("✅ Already Marked")
            self.mark_edited_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: #212529;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
                QPushButton:pressed {
                    background-color: #d39e00;
                }
            """)
        else:
            self.mark_edited_btn.setText("✅ Mark as Edited")
            self.mark_edited_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
    
    def get_current_poem_id(self):
        """Get unique ID for current poem"""
        if not self.current_poems:
            return None
        poem = self.current_poems[self.current_poem_index]
        return f"{poem.get('title', 'Unknown')}_{self.current_poem_index}_{poem.get('json_file', '')}"
    
    def is_current_poem_edited(self):
        """Check if current poem has been marked as edited"""
        if not self.current_poems:
            return False
        poem = self.current_poems[self.current_poem_index]
        return poem.get('edited', False)
        
    def load_json_files(self):
        """Load individual JSON file and create working copy"""
        json_path, _ = QFileDialog.getOpenFileName(
            self, "Select JSON File", "PoemJsonFiles",
            "JSON files (*.json);;All files (*.*)")

        if json_path:
            self.load_json_file(json_path)
            
    def load_json_file(self, json_path):
        """Load individual JSON file and create working copy"""
        try:
            # Store the original file path
            self.original_json_path = json_path

            # Load the original JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            # Create a deep copy for working
            import copy
            self.working_json_data = copy.deepcopy(original_data)
            self.current_json_data = original_data

            # Extract poems from the working copy
            self.current_poems = []
            if isinstance(self.working_json_data, list):
                # Multiple poems in the file
                for i, poem in enumerate(self.working_json_data):
                    if 'poem_lines' in poem and 'poem_type' in poem:
                        poem['json_file'] = json_path
                        poem['poem_index'] = i  # Store index for updating later
                        self.current_poems.append(poem)
            else:
                # Single poem object
                if 'poem_lines' in self.working_json_data and 'poem_type' in self.working_json_data:
                    self.working_json_data['json_file'] = json_path
                    self.working_json_data['poem_index'] = 0
                    self.current_poems.append(self.working_json_data)

            self.current_poem_index = 0
            self.update_status(f"Loaded {len(self.current_poems)} poems from {os.path.basename(json_path)}")
            self.display_current_poem()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")
    
    def select_pdf_file(self):
        """Select PDF file"""
        pdf_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "PoemOcrFiles", 
            "PDF files (*.pdf);;All files (*.*)")
        
        if pdf_path:
            try:
                if self.pdf_doc:
                    self.pdf_doc.close()
                
                self.pdf_doc = fitz.open(pdf_path)
                self.current_pdf_path = pdf_path
                self.current_pdf_page = 0
                
                self.pdf_info_label.setText(
                    f"PDF: {os.path.basename(pdf_path)} ({self.pdf_doc.page_count} pages)")
                
                self.update_status(f"Loaded PDF: {os.path.basename(pdf_path)}")
                self.display_pdf_page()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load PDF: {e}")
    
    def display_current_poem(self):
        """Display current poem"""
        if not self.current_poems:
            return
            
        poem = self.current_poems[self.current_poem_index]
        
        # Update poem info
        self.poem_info_label.setText(
            f"Poem {self.current_poem_index + 1} of {len(self.current_poems)}")
        
        # Show current content (from working copy)
        self.title_entry.setText(poem.get('title', ''))
        self.author_entry.setText(poem.get('author', ''))
        self.type_entry.setText(poem.get('poem_type', ''))
        self.poem_page_entry.setText(str(poem.get('poem_start_at_page', '')))
        self.poem_text.setPlainText('\n'.join(poem.get('poem_lines', [])))

        # Show edit status visually
        if poem.get('edited', False):
            self.title_entry.setStyleSheet("background-color: #e8f5e8; border-color: #28a745; color: #28a745;")
            self.author_entry.setStyleSheet("background-color: #e8f5e8; border-color: #28a745; color: #28a745;")
            self.type_entry.setStyleSheet("background-color: #e8f5e8; border-color: #28a745; color: #28a745;")
            self.poem_text.setStyleSheet("background-color: #e8f5e8; border-color: #28a745; color: #28a745;")
        else:
            self.title_entry.setStyleSheet("")
            self.author_entry.setStyleSheet("")
            self.type_entry.setStyleSheet("")
            self.poem_text.setStyleSheet("")
        
        # Navigate to poem page
        page_num = poem.get('poem_start_at_page')
        if page_num and self.pdf_doc:
            self.current_pdf_page = max(0, int(page_num) - 1)
            self.display_pdf_page()
        
        # Update edit status button
        self.update_mark_edited_button_style(self.is_current_poem_edited())
        
        # Save current position
        self.save_current_position()
    
    def display_pdf_page(self):
        """Display current PDF page"""
        if not self.pdf_doc:
            return
            
        try:
            if 0 <= self.current_pdf_page < self.pdf_doc.page_count:
                page = self.pdf_doc[self.current_pdf_page]
                
                # Update page info
                self.page_label.setText(
                    f"Page: {self.current_pdf_page + 1} of {self.pdf_doc.page_count}")
                self.page_input.setText(str(self.current_pdf_page + 1))
                
                # Convert page to image with current zoom
                mat = fitz.Matrix(self.pdf_zoom_factor, self.pdf_zoom_factor)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Display image
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                
                self.pdf_label.setPixmap(pixmap)
                
                # Update zoom label
                self.zoom_label.setText(f"{int(self.pdf_zoom_factor * 100)}%")
                
        except Exception as e:
            self.update_status(f"Error displaying PDF page: {e}")
    
    def zoom_in_pdf(self):
        """Zoom in on PDF"""
        if self.pdf_zoom_factor < 3.0:  # Max zoom 300%
            self.pdf_zoom_factor += 0.25
            self.display_pdf_page()
            self.update_status(f"Zoomed in to {int(self.pdf_zoom_factor * 100)}%")
    
    def zoom_out_pdf(self):
        """Zoom out on PDF"""
        if self.pdf_zoom_factor > 0.5:  # Min zoom 50%
            self.pdf_zoom_factor -= 0.25
            self.display_pdf_page()
            self.update_status(f"Zoomed out to {int(self.pdf_zoom_factor * 100)}%")
    
    def reset_zoom_pdf(self):
        """Reset PDF zoom to default"""
        self.pdf_zoom_factor = 1.5
        self.display_pdf_page()
        self.update_status("PDF zoom reset to 150%")
    
    def prev_pdf_page(self):
        """Go to previous PDF page"""
        if self.pdf_doc and self.current_pdf_page > 0:
            self.current_pdf_page -= 1
            self.display_pdf_page()
    
    def next_pdf_page(self):
        """Go to next PDF page"""
        if self.pdf_doc and self.current_pdf_page < self.pdf_doc.page_count - 1:
            self.current_pdf_page += 1
            self.display_pdf_page()
    
    def go_to_page(self):
        """Go to specific page"""
        try:
            page_num = int(self.page_input.text()) - 1
            if self.pdf_doc and 0 <= page_num < self.pdf_doc.page_count:
                self.current_pdf_page = page_num
                self.display_pdf_page()
        except ValueError:
            pass
    
    def sync_pdf_page(self):
        """Sync PDF page with poem page"""
        try:
            page_num = int(self.poem_page_entry.text()) - 1
            if self.pdf_doc and 0 <= page_num < self.pdf_doc.page_count:
                self.current_pdf_page = page_num
                self.display_pdf_page()
        except ValueError:
            pass
    

    
    def auto_fix_ocr(self):
        """Apply automatic OCR fixes"""
        current_text = self.poem_text.toPlainText()
        
        # Common OCR corrections for Burmese
        corrections = {
            'ကွို': 'ကို',
            'မွှ': 'မှ', 
            'နွှင့်': 'နှင့်',
            ',': '၊',
            '.': '။',
            'ကိုု': 'ကို',
            'မှွ': 'မှ',
        }
        
        fixed_text = current_text
        changes_made = 0
        
        for wrong, correct in corrections.items():
            if wrong in fixed_text:
                fixed_text = fixed_text.replace(wrong, correct)
                changes_made += 1
        
        # Clean extra whitespace
        lines = fixed_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        fixed_text = '\n'.join(cleaned_lines)
        
        self.poem_text.setPlainText(fixed_text)
        self.update_status(f"Applied {changes_made} OCR fixes")
    
    def reset_poem(self):
        """Reset poem to original state by reloading from original JSON"""
        if self.current_poems and self.current_json_data:
            poem = self.current_poems[self.current_poem_index]

            # Find the original poem data and reset working copy
            if isinstance(self.current_json_data, list):
                # Multiple poems - find the matching one
                if isinstance(self.working_json_data, list):
                    poem_index = poem.get('poem_index', 0)
                    if poem_index < len(self.current_json_data) and poem_index < len(self.working_json_data):
                        # Create a fresh copy of the original poem
                        import copy
                        original_poem = self.current_json_data[poem_index]
                        self.working_json_data[poem_index] = copy.deepcopy(original_poem)
                        self.working_json_data[poem_index]['json_file'] = self.original_json_path
                        self.working_json_data[poem_index]['poem_index'] = poem_index
                        self.current_poems[self.current_poem_index] = self.working_json_data[poem_index]
            else:
                # Single poem - reset the working copy
                import copy
                self.working_json_data = copy.deepcopy(self.current_json_data)
                self.working_json_data['json_file'] = self.original_json_path
                self.working_json_data['poem_index'] = 0
                self.current_poems[self.current_poem_index] = self.working_json_data

            # Update display
            self.display_current_poem()

            # Update button style
            self.update_mark_edited_button_style(False)

            self.update_status("Reset to original poem")

    def mark_as_edited(self):
        """Mark current poem as edited in working copy"""
        if not self.current_poems or not self.working_json_data:
            QMessageBox.warning(self, "Warning", "No poems loaded to mark as edited.")
            return

        poem = self.current_poems[self.current_poem_index]

        # Get edited content
        edited_lines = [line.strip() for line in self.poem_text.toPlainText().split('\n') if line.strip()]

        if not edited_lines:
            QMessageBox.warning(self, "Warning", "Poem content is empty. Please add content before marking as edited.")
            return

        # Update the poem in the working copy (directly replace values)
        if isinstance(self.working_json_data, list):
            # Multiple poems - update the specific poem
            poem_index = poem.get('poem_index', 0)
            if poem_index < len(self.working_json_data):
                # Directly replace with edited values
                self.working_json_data[poem_index]['title'] = self.title_entry.text()
                self.working_json_data[poem_index]['author'] = self.author_entry.text()
                self.working_json_data[poem_index]['poem_type'] = self.type_entry.text()
                self.working_json_data[poem_index]['poem_lines'] = edited_lines
                self.working_json_data[poem_index]['poem_start_at_page'] = self.poem_page_entry.text()
                self.working_json_data[poem_index]['edited'] = True
                self.working_json_data[poem_index]['edit_timestamp'] = datetime.now().isoformat()

                # Update the current poem reference
                self.current_poems[self.current_poem_index] = self.working_json_data[poem_index]
        else:
            # Single poem - update the working copy directly
            self.working_json_data['title'] = self.title_entry.text()
            self.working_json_data['author'] = self.author_entry.text()
            self.working_json_data['poem_type'] = self.type_entry.text()
            self.working_json_data['poem_lines'] = edited_lines
            self.working_json_data['poem_start_at_page'] = self.poem_page_entry.text()
            self.working_json_data['edited'] = True
            self.working_json_data['edit_timestamp'] = datetime.now().isoformat()

            # Update the current poem reference
            self.current_poems[self.current_poem_index] = self.working_json_data

        # Update button style
        self.update_mark_edited_button_style(True)

        # Count total edited poems
        edited_count = sum(1 for p in self.current_poems if p.get('edited', False))
        self.update_status(f"✅ Marked as edited (in working copy): {poem.get('title', 'Unknown')} ({edited_count} total edits)")
    

    def save_edits(self):
        """Save the entire working JSON file to a new location"""
        if not self.working_json_data:
            QMessageBox.information(self, "Info", "No working data to save")
            return

        try:
            # Ask user for save location and filename
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Edited JSON File",
                self.original_json_path or "edited_poems.json",
                "JSON files (*.json);;All files (*.*)"
            )

            if not save_path:
                return

            # Ensure the filename has .json extension
            if not save_path.endswith('.json'):
                save_path += '.json'

            # Save the entire working copy
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.working_json_data, f, ensure_ascii=False, indent=2)

            # Count edited poems for status message
            edited_count = sum(1 for poem in self.current_poems if poem.get('edited', False))

            QMessageBox.information(self, "Success",
                                  f"Saved working copy to:\n{save_path}\n({edited_count} poems marked as edited)")
            self.update_status(f"💾 Saved working copy to {os.path.basename(save_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save working copy: {e}")
    
    def previous_poem(self):
        """Go to previous poem"""
        if self.current_poems and self.current_poem_index > 0:
            self.current_poem_index -= 1
            self.display_current_poem()
    
    def next_poem(self):
        """Go to next poem"""
        if self.current_poems and self.current_poem_index < len(self.current_poems) - 1:
            self.current_poem_index += 1
            self.display_current_poem()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)
    
    def save_current_position(self):
        """Save current editing position"""
        if not self.current_poems:
            return
            
        settings = {
            'last_poem_index': self.current_poem_index,
            'last_pdf_path': self.current_pdf_path,
            'last_pdf_page': self.current_pdf_page,
            'pdf_zoom_factor': self.pdf_zoom_factor,
            'window_geometry': [self.x(), self.y(), self.width(), self.height()],
            'last_json_directory': getattr(self, 'last_json_directory', None)
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            pass  # Silently fail to avoid disrupting user experience
    
    def load_settings(self):
        """Load and restore previous editing position"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Restore window geometry
                if 'window_geometry' in settings:
                    x, y, w, h = settings['window_geometry']
                    self.setGeometry(x, y, w, h)
                
                # Restore zoom factor
                if 'pdf_zoom_factor' in settings:
                    self.pdf_zoom_factor = settings['pdf_zoom_factor']
                
                # Store for later restoration
                self.stored_settings = settings
                
        except Exception as e:
            pass  # Silently fail and use defaults
    
    def restore_last_position(self):
        """Restore last editing position after loading data"""
        if not hasattr(self, 'stored_settings'):
            return
            
        settings = self.stored_settings
        
        try:
            # Restore poem position
            if ('last_poem_index' in settings and 
                settings['last_poem_index'] < len(self.current_poems)):
                self.current_poem_index = settings['last_poem_index']
                self.display_current_poem()
                self.update_status(f"Restored to poem {self.current_poem_index + 1}")
            
            # Restore PDF if it exists
            if ('last_pdf_path' in settings and 
                settings['last_pdf_path'] and 
                os.path.exists(settings['last_pdf_path'])):
                
                self.pdf_doc = fitz.open(settings['last_pdf_path'])
                self.current_pdf_path = settings['last_pdf_path']
                
                if 'last_pdf_page' in settings:
                    self.current_pdf_page = min(settings['last_pdf_page'], 
                                              self.pdf_doc.page_count - 1)
                
                self.pdf_info_label.setText(
                    f"PDF: {os.path.basename(self.current_pdf_path)} ({self.pdf_doc.page_count} pages)")
                self.display_pdf_page()
                
        except Exception as e:
            self.update_status("Could not fully restore previous session")
    

    
    def closeEvent(self, event):
        """Handle application closing"""
        # Save current position
        self.save_current_position()

        # Close PDF document
        if self.pdf_doc:
            self.pdf_doc.close()
            
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application-wide Burmese font support
    app.setFont(QFont("Myanmar Text", 10))
    
    # Enable better text rendering for complex scripts
    app.setAttribute(Qt.AA_Use96Dpi, True)
    
    window = BurmesePoemEditor()
    
    # No auto-loading - user must select individual files now
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
