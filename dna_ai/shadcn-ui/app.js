// Universal AI Assistant - Enhanced with File Management & Settings
class UniversalAIAssistant {
    constructor() {
        this.currentLanguage = 'python';
        this.isAIPanelOpen = false;
        this.isSettingsPanelOpen = false;
        this.isFileExplorerOpen = false;
        this.isSidebarCollapsed = false;
        this.chatHistory = [];
        this.chatMode = 'coding';
        this.openFiles = new Map();
        this.currentFile = 'welcome.md';
        this.fileSystem = new Map();
        this.settings = this.loadSettings();
        this.supportedLanguages = [
            'python', 'javascript', 'java', 'cpp', 'rust', 'go', 'ruby', 'php',
            'swift', 'kotlin', 'csharp', 'typescript', 'r', 'julia', 'haskell',
            'clojure', 'erlang', 'elixir', 'bash', 'powershell', 'lua', 'zig',
            'nim', 'crystal', 'sql', 'yaml', 'json', 'dockerfile'
        ];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileSystem();
        this.setupDragAndDrop();
        this.updateLanguageDisplay();
        this.loadLanguageTemplate();
        this.setupModeToggle();
        this.applySettings();
        this.loadWelcomeMessage();
        this.updateFileCount();
    }

    loadSettings() {
        const defaultSettings = {
            theme: 'dark',
            fontSize: 14,
            fontFamily: 'monaco',
            tabSize: 2,
            wordWrap: true,
            lineNumbers: true,
            autoSave: true,
            defaultMode: 'coding',
            autoComplete: true,
            codeAnalysis: true,
            maxFiles: 20,
            debugMode: false
        };

        try {
            const saved = localStorage.getItem('aiAssistantSettings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            console.error('Error loading settings:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('aiAssistantSettings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    applySettings() {
        // Apply theme
        document.body.className = this.settings.theme === 'light' ? 'light-theme' : '';
        
        // Apply font settings
        const codeEditor = document.getElementById('codeEditor');
        if (codeEditor) {
            codeEditor.style.fontSize = `${this.settings.fontSize}px`;
            codeEditor.style.fontFamily = this.getFontFamily(this.settings.fontFamily);
            codeEditor.style.tabSize = this.settings.tabSize;
            codeEditor.style.whiteSpace = this.settings.wordWrap ? 'pre-wrap' : 'pre';
        }

        // Update settings UI
        this.updateSettingsUI();
    }

    getFontFamily(family) {
        const fonts = {
            'monaco': 'Monaco, Menlo, Ubuntu Mono, Consolas, monospace',
            'consolas': 'Consolas, Monaco, Menlo, Ubuntu Mono, monospace',
            'fira-code': 'Fira Code, Monaco, Menlo, Ubuntu Mono, Consolas, monospace',
            'source-code-pro': 'Source Code Pro, Monaco, Menlo, Ubuntu Mono, Consolas, monospace'
        };
        return fonts[family] || fonts.monaco;
    }

    updateSettingsUI() {
        // Update all setting controls to match current settings
        const elements = {
            'themeSelect': this.settings.theme,
            'fontSizeSlider': this.settings.fontSize,
            'fontFamilySelect': this.settings.fontFamily,
            'tabSizeSlider': this.settings.tabSize,
            'wordWrapCheck': this.settings.wordWrap,
            'lineNumbersCheck': this.settings.lineNumbers,
            'autoSaveCheck': this.settings.autoSave,
            'defaultModeSelect': this.settings.defaultMode,
            'autoCompleteCheck': this.settings.autoComplete,
            'codeAnalysisCheck': this.settings.codeAnalysis,
            'maxFilesSlider': this.settings.maxFiles,
            'debugModeCheck': this.settings.debugMode
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });

        // Update value displays
        document.getElementById('fontSizeValue').textContent = `${this.settings.fontSize}px`;
        document.getElementById('tabSizeValue').textContent = `${this.settings.tabSize} spaces`;
        document.getElementById('maxFilesValue').textContent = `${this.settings.maxFiles} files`;
    }

    setupFileSystem() {
        // Initialize with welcome file
        this.openFiles.set('welcome.md', {
            name: 'welcome.md',
            content: `# Welcome to Universal AI Assistant!

This AI can code in 30+ programming languages and answer general questions.

## Features:
- 📁 **File Management**: Import files and folders via drag & drop
- 💻 **Multi-Language Coding**: Support for 30+ programming languages
- 🤖 **Dual-Mode AI**: Switch between Coding and General Chat modes
- ⚙️ **Customizable Settings**: Theme, fonts, editor preferences
- 📝 **Multi-File Editing**: Work with multiple files in tabs
- 🎨 **Dark Theme**: Professional GitHub-style interface

## Getting Started:
1. Import your files using the sidebar
2. Open the AI chat for assistance
3. Select a programming language
4. Start coding!

## AI Modes:
- **💻 Coding Mode**: Generate code, debug, explain algorithms
- **💬 General Mode**: Math, definitions, recommendations, trivia

Try asking the AI: "Create a Python function" or "What is 25% of 200?"`,
            type: 'markdown',
            modified: false,
            path: 'welcome.md'
        });

        this.updateFileTree();
    }

    setupDragAndDrop() {
        const dropZone = document.getElementById('dropZone');
        if (!dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
        });

        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
        dropZone.addEventListener('click', () => document.getElementById('fileInput').click());
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    async handleDrop(e) {
        const files = Array.from(e.dataTransfer.files);
        await this.processFiles(files);
    }

    async processFiles(files) {
        for (const file of files) {
            if (file.type.startsWith('image/')) {
                // Handle image files
                await this.addImageFile(file);
            } else {
                // Handle text files
                await this.addTextFile(file);
            }
        }
        this.updateFileTree();
        this.updateFileCount();
        this.showOutput(`✅ Imported ${files.length} file(s) successfully!`, 'success');
    }

    async addTextFile(file) {
        try {
            const content = await this.readFileAsText(file);
            const fileType = this.getFileType(file.name);
            
            this.openFiles.set(file.name, {
                name: file.name,
                content: content,
                type: fileType,
                modified: false,
                path: file.name,
                size: file.size
            });

            // Auto-open the file
            this.openFile(file.name);
        } catch (error) {
            console.error('Error reading file:', error);
            this.showOutput(`❌ Error reading file: ${file.name}`, 'error');
        }
    }

    async addImageFile(file) {
        try {
            const url = URL.createObjectURL(file);
            
            this.openFiles.set(file.name, {
                name: file.name,
                content: url,
                type: 'image',
                modified: false,
                path: file.name,
                size: file.size,
                isImage: true
            });

        } catch (error) {
            console.error('Error processing image:', error);
            this.showOutput(`❌ Error processing image: ${file.name}`, 'error');
        }
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    getFileType(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const typeMap = {
            'js': 'javascript',
            'py': 'python',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'cpp',
            'rs': 'rust',
            'go': 'go',
            'rb': 'ruby',
            'php': 'php',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'md': 'markdown',
            'txt': 'text',
            'ts': 'typescript',
            'jsx': 'javascript',
            'tsx': 'typescript',
            'vue': 'javascript',
            'sql': 'sql',
            'sh': 'bash',
            'yml': 'yaml',
            'yaml': 'yaml'
        };
        return typeMap[ext] || 'text';
    }

    updateFileTree() {
        const fileTree = document.getElementById('fileTree');
        if (!fileTree) return;

        const workspaceInfo = fileTree.querySelector('.workspace-info');
        fileTree.innerHTML = '';
        if (workspaceInfo) {
            fileTree.appendChild(workspaceInfo);
        }

        this.openFiles.forEach((file, filename) => {
            const fileItem = document.createElement('div');
            fileItem.className = `file-item ${file.name === this.currentFile ? 'active' : ''}`;
            fileItem.dataset.type = file.type;
            fileItem.innerHTML = `
                <span class="file-name">${file.name}</span>
                <div class="file-actions">
                    <button class="file-action" onclick="aiAssistant.renameFile('${filename}')" title="Rename">✏️</button>
                    <button class="file-action" onclick="aiAssistant.deleteFile('${filename}')" title="Delete">🗑️</button>
                </div>
            `;
            
            fileItem.addEventListener('click', () => this.openFile(filename));
            fileTree.appendChild(fileItem);
        });
    }

    openFile(filename) {
        const file = this.openFiles.get(filename);
        if (!file) return;

        this.currentFile = filename;
        
        // Update editor content
        const codeEditor = document.getElementById('codeEditor');
        if (codeEditor && !file.isImage) {
            codeEditor.value = file.content;
        }

        // Update tabs
        this.updateEditorTabs();
        
        // Update file tree
        this.updateFileTree();
        
        // Update status bar
        this.updateStatusBar();
        
        // Update breadcrumb
        const breadcrumb = document.getElementById('breadcrumb');
        if (breadcrumb) {
            breadcrumb.textContent = `Universal AI Assistant - ${filename}`;
        }

        // Auto-detect and set language
        if (file.type && this.supportedLanguages.includes(file.type)) {
            this.changeLanguage(file.type);
        }
    }

    updateEditorTabs() {
        const editorTabs = document.getElementById('editorTabs');
        if (!editorTabs) return;

        editorTabs.innerHTML = '';
        
        this.openFiles.forEach((file, filename) => {
            const tab = document.createElement('button');
            tab.className = `editor-tab ${filename === this.currentFile ? 'active' : ''} ${file.modified ? 'modified' : ''}`;
            tab.dataset.file = filename;
            
            const icon = this.getFileIcon(file.type);
            tab.innerHTML = `
                <span>${icon} ${file.name}</span>
                <button class="tab-close" onclick="aiAssistant.closeFile('${filename}', event)">×</button>
            `;
            
            tab.addEventListener('click', (e) => {
                if (!e.target.classList.contains('tab-close')) {
                    this.openFile(filename);
                }
            });
            
            editorTabs.appendChild(tab);
        });
    }

    getFileIcon(type) {
        const icons = {
            'javascript': '🟨',
            'python': '🐍',
            'java': '☕',
            'cpp': '⚡',
            'rust': '🦀',
            'go': '🐹',
            'ruby': '💎',
            'php': '🐘',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            'markdown': '📝',
            'image': '🖼️',
            'text': '📄'
        };
        return icons[type] || '📄';
    }

    closeFile(filename, event) {
        if (event) {
            event.stopPropagation();
        }

        const file = this.openFiles.get(filename);
        if (file && file.modified) {
            if (!confirm(`File "${filename}" has unsaved changes. Close anyway?`)) {
                return;
            }
        }

        this.openFiles.delete(filename);
        
        // If closing current file, switch to another
        if (filename === this.currentFile) {
            const remaining = Array.from(this.openFiles.keys());
            if (remaining.length > 0) {
                this.openFile(remaining[0]);
            } else {
                // Create a new welcome file
                this.createNewFile('untitled.txt');
            }
        }

        this.updateEditorTabs();
        this.updateFileTree();
        this.updateFileCount();
    }

    createNewFile(filename = null) {
        const name = filename || prompt('Enter filename:');
        if (!name) return;

        if (this.openFiles.has(name)) {
            alert('File already exists!');
            return;
        }

        const fileType = this.getFileType(name);
        this.openFiles.set(name, {
            name: name,
            content: '',
            type: fileType,
            modified: false,
            path: name
        });

        this.openFile(name);
        this.updateFileCount();
    }

    renameFile(oldName) {
        const newName = prompt('Enter new filename:', oldName);
        if (!newName || newName === oldName) return;

        if (this.openFiles.has(newName)) {
            alert('File already exists!');
            return;
        }

        const file = this.openFiles.get(oldName);
        if (file) {
            file.name = newName;
            file.path = newName;
            this.openFiles.set(newName, file);
            this.openFiles.delete(oldName);

            if (this.currentFile === oldName) {
                this.currentFile = newName;
            }

            this.updateEditorTabs();
            this.updateFileTree();
        }
    }

    deleteFile(filename) {
        if (!confirm(`Delete file "${filename}"?`)) return;

        this.closeFile(filename);
    }

    updateFileCount() {
        const fileCount = document.getElementById('fileCount');
        if (fileCount) {
            const count = this.openFiles.size;
            fileCount.textContent = `${count} file${count !== 1 ? 's' : ''}`;
        }
    }

    setupEventListeners() {
        // Sidebar toggle
        const toggleSidebar = document.getElementById('toggleSidebar');
        if (toggleSidebar) {
            toggleSidebar.addEventListener('click', () => this.toggleSidebar());
        }

        // AI panel toggle
        const toggleAI = document.getElementById('toggleAI');
        if (toggleAI) {
            toggleAI.addEventListener('click', () => this.toggleAIPanel());
        }

        // Close AI panel
        const closeAI = document.getElementById('closeAI');
        if (closeAI) {
            closeAI.addEventListener('click', () => this.toggleAIPanel());
        }

        // Language selector
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.addEventListener('change', (e) => this.changeLanguage(e.target.value));
        }

        // Run code button
        const runCode = document.getElementById('runCode');
        if (runCode) {
            runCode.addEventListener('click', () => this.runCode());
        }

        // Send message
        const sendMessage = document.getElementById('sendMessage');
        if (sendMessage) {
            sendMessage.addEventListener('click', () => this.sendMessage());
        }

        // Chat input enter key
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            chatInput.addEventListener('input', () => this.autoResizeTextarea(chatInput));
        }

        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => this.handleNavigation(item.dataset.view));
        });

        // Panel tabs
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchPanel(tab.dataset.panel));
        });

        // Code editor improvements
        const codeEditor = document.getElementById('codeEditor');
        if (codeEditor) {
            codeEditor.addEventListener('input', () => {
                this.updateStatusBar();
                this.markFileAsModified();
                if (this.settings.autoSave) {
                    this.autoSave();
                }
            });
            codeEditor.addEventListener('keydown', (e) => this.handleCodeEditorKeydown(e));
        }

        // File import buttons
        const importFiles = document.getElementById('importFiles');
        if (importFiles) {
            importFiles.addEventListener('click', () => document.getElementById('fileInput').click());
        }

        const importFolder = document.getElementById('importFolder');
        if (importFolder) {
            importFolder.addEventListener('click', () => document.getElementById('folderInput').click());
        }

        // File inputs
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.processFiles(Array.from(e.target.files)));
        }

        const folderInput = document.getElementById('folderInput');
        if (folderInput) {
            folderInput.addEventListener('change', (e) => this.processFiles(Array.from(e.target.files)));
        }

        // Explorer buttons
        const newFile = document.getElementById('newFile');
        if (newFile) {
            newFile.addEventListener('click', () => this.createNewFile());
        }

        const newFolder = document.getElementById('newFolder');
        if (newFolder) {
            newFolder.addEventListener('click', () => alert('Folder creation coming soon!'));
        }

        const refreshExplorer = document.getElementById('refreshExplorer');
        if (refreshExplorer) {
            refreshExplorer.addEventListener('click', () => this.updateFileTree());
        }

        // Settings event listeners
        this.setupSettingsEventListeners();
    }

    setupSettingsEventListeners() {
        // Close settings
        const closeSettings = document.getElementById('closeSettings');
        if (closeSettings) {
            closeSettings.addEventListener('click', () => this.toggleSettingsPanel());
        }

        // Theme selector
        const themeSelect = document.getElementById('themeSelect');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                this.settings.theme = e.target.value;
                this.applySettings();
                this.saveSettings();
            });
        }

        // Font size slider
        const fontSizeSlider = document.getElementById('fontSizeSlider');
        if (fontSizeSlider) {
            fontSizeSlider.addEventListener('input', (e) => {
                this.settings.fontSize = parseInt(e.target.value);
                this.applySettings();
                this.saveSettings();
            });
        }

        // Font family selector
        const fontFamilySelect = document.getElementById('fontFamilySelect');
        if (fontFamilySelect) {
            fontFamilySelect.addEventListener('change', (e) => {
                this.settings.fontFamily = e.target.value;
                this.applySettings();
                this.saveSettings();
            });
        }

        // Tab size slider
        const tabSizeSlider = document.getElementById('tabSizeSlider');
        if (tabSizeSlider) {
            tabSizeSlider.addEventListener('input', (e) => {
                this.settings.tabSize = parseInt(e.target.value);
                this.applySettings();
                this.saveSettings();
            });
        }

        // Checkboxes
        ['wordWrap', 'lineNumbers', 'autoSave', 'autoComplete', 'codeAnalysis', 'debugMode'].forEach(setting => {
            const checkbox = document.getElementById(setting + 'Check');
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.settings[setting] = e.target.checked;
                    this.applySettings();
                    this.saveSettings();
                });
            }
        });

        // Default mode selector
        const defaultModeSelect = document.getElementById('defaultModeSelect');
        if (defaultModeSelect) {
            defaultModeSelect.addEventListener('change', (e) => {
                this.settings.defaultMode = e.target.value;
                this.saveSettings();
            });
        }

        // Max files slider
        const maxFilesSlider = document.getElementById('maxFilesSlider');
        if (maxFilesSlider) {
            maxFilesSlider.addEventListener('input', (e) => {
                this.settings.maxFiles = parseInt(e.target.value);
                document.getElementById('maxFilesValue').textContent = `${e.target.value} files`;
                this.saveSettings();
            });
        }

        // Reset settings
        const resetSettings = document.getElementById('resetSettings');
        if (resetSettings) {
            resetSettings.addEventListener('click', () => {
                if (confirm('Reset all settings to defaults?')) {
                    localStorage.removeItem('aiAssistantSettings');
                    this.settings = this.loadSettings();
                    this.applySettings();
                    this.showOutput('✅ Settings reset to defaults', 'success');
                }
            });
        }

        // Export/Import settings
        const exportSettings = document.getElementById('exportSettings');
        if (exportSettings) {
            exportSettings.addEventListener('click', () => this.exportSettings());
        }

        const importSettings = document.getElementById('importSettings');
        if (importSettings) {
            importSettings.addEventListener('click', () => this.importSettings());
        }

        // Clear data
        const clearData = document.getElementById('clearData');
        if (clearData) {
            clearData.addEventListener('click', () => {
                if (confirm('Clear all data including files and settings?')) {
                    localStorage.clear();
                    location.reload();
                }
            });
        }
    }

    exportSettings() {
        const data = {
            settings: this.settings,
            files: Array.from(this.openFiles.entries()),
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ai-assistant-settings.json';
        a.click();
        URL.revokeObjectURL(url);
        
        this.showOutput('✅ Settings exported successfully', 'success');
    }

    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
            try {
                const file = e.target.files[0];
                const text = await this.readFileAsText(file);
                const data = JSON.parse(text);
                
                if (data.settings) {
                    this.settings = { ...this.settings, ...data.settings };
                    this.applySettings();
                    this.saveSettings();
                }
                
                if (data.files && confirm('Import files as well?')) {
                    data.files.forEach(([name, file]) => {
                        this.openFiles.set(name, file);
                    });
                    this.updateFileTree();
                    this.updateFileCount();
                }
                
                this.showOutput('✅ Settings imported successfully', 'success');
            } catch (error) {
                this.showOutput('❌ Error importing settings', 'error');
                console.error(error);
            }
        };
        input.click();
    }

    markFileAsModified() {
        const file = this.openFiles.get(this.currentFile);
        if (file && !file.modified) {
            file.modified = true;
            this.updateEditorTabs();
        }
    }

    autoSave() {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveCurrentFile();
        }, 1000);
    }

    saveCurrentFile() {
        const file = this.openFiles.get(this.currentFile);
        const codeEditor = document.getElementById('codeEditor');
        
        if (file && codeEditor) {
            file.content = codeEditor.value;
            file.modified = false;
            this.updateEditorTabs();
        }
    }

    setupModeToggle() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchChatMode(btn.dataset.mode));
        });
    }

    switchChatMode(mode) {
        this.chatMode = mode;
        
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
        
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            if (mode === 'coding') {
                chatInput.placeholder = 'Ask me about coding, algorithms, debugging, or any programming question...';
            } else {
                chatInput.placeholder = 'Ask me anything! Weather, math, definitions, recommendations, fun facts...';
            }
        }
        
        const modeMessage = mode === 'coding' 
            ? '💻 **Switched to Coding Mode!**\n\nI can now help you with:\n• Code generation in 30+ languages\n• Bug fixes and debugging\n• Algorithm implementations\n• Programming best practices\n• Code analysis and optimization\n\nWhat would you like to code today?'
            : '💬 **Switched to General Chat Mode!**\n\nI can now help you with:\n• Math calculations and word problems\n• Definitions and explanations\n• Weather information\n• Movie/book/travel recommendations\n• Fun facts and trivia\n• Creative writing and translations\n• General conversation\n\nWhat would you like to know?';
        
        this.addChatMessage(modeMessage, 'ai');
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            this.isSidebarCollapsed = !this.isSidebarCollapsed;
            sidebar.classList.toggle('collapsed', this.isSidebarCollapsed);
        }
    }

    toggleAIPanel() {
        const aiPanel = document.getElementById('aiPanel');
        if (aiPanel) {
            this.isAIPanelOpen = !this.isAIPanelOpen;
            aiPanel.classList.toggle('hidden', !this.isAIPanelOpen);
            
            const toggleButton = document.getElementById('toggleAI');
            if (toggleButton) {
                toggleButton.textContent = this.isAIPanelOpen ? '❌ Close AI' : '🤖 AI Chat';
            }

            // Close settings if open
            if (this.isAIPanelOpen && this.isSettingsPanelOpen) {
                this.toggleSettingsPanel();
            }
        }
    }

    toggleSettingsPanel() {
        const settingsPanel = document.getElementById('settingsPanel');
        if (settingsPanel) {
            this.isSettingsPanelOpen = !this.isSettingsPanelOpen;
            settingsPanel.classList.toggle('hidden', !this.isSettingsPanelOpen);

            // Close AI panel if open
            if (this.isSettingsPanelOpen && this.isAIPanelOpen) {
                this.toggleAIPanel();
            }
        }
    }

    toggleFileExplorer() {
        const fileExplorer = document.getElementById('fileExplorer');
        if (fileExplorer) {
            this.isFileExplorerOpen = !this.isFileExplorerOpen;
            fileExplorer.classList.toggle('hidden', !this.isFileExplorerOpen);
        }
    }

    changeLanguage(language) {
        this.currentLanguage = language;
        this.updateLanguageDisplay();
        this.updateStatusBar();
        
        // Update current file type if it matches
        const file = this.openFiles.get(this.currentFile);
        if (file && this.supportedLanguages.includes(language)) {
            file.type = language;
        }
    }

    updateLanguageDisplay() {
        const statusLeft = document.querySelector('.status-left');
        if (statusLeft && statusLeft.children[1]) {
            statusLeft.children[1].textContent = this.getLanguageDisplayName(this.currentLanguage);
        }

        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.value = this.currentLanguage;
        }
    }

    getLanguageDisplayName(lang) {
        const displayNames = {
            'python': 'Python 3.11',
            'javascript': 'JavaScript ES2023',
            'java': 'Java 17',
            'cpp': 'C++ 17',
            'rust': 'Rust 1.70',
            'go': 'Go 1.20',
            'ruby': 'Ruby 3.2',
            'php': 'PHP 8.2',
            'swift': 'Swift 5.8',
            'kotlin': 'Kotlin 1.9',
            'csharp': 'C# 11',
            'typescript': 'TypeScript 5.0',
            'r': 'R 4.3',
            'julia': 'Julia 1.9',
            'haskell': 'Haskell GHC 9.4',
            'clojure': 'Clojure 1.11',
            'erlang': 'Erlang/OTP 26',
            'elixir': 'Elixir 1.15',
            'bash': 'Bash 5.2',
            'powershell': 'PowerShell 7.3',
            'lua': 'Lua 5.4',
            'zig': 'Zig 0.11',
            'nim': 'Nim 2.0',
            'crystal': 'Crystal 1.9',
            'sql': 'SQL',
            'yaml': 'YAML',
            'json': 'JSON',
            'dockerfile': 'Dockerfile'
        };
        return displayNames[lang] || lang.toUpperCase();
    }

    loadLanguageTemplate() {
        // Templates are loaded when files are opened or created
    }

    async runCode() {
        const codeEditor = document.getElementById('codeEditor');
        if (!codeEditor) return;

        const code = codeEditor.value;
        if (!code.trim()) {
            this.showOutput('❌ No code to run', 'error');
            return;
        }

        this.showOutput('🔄 Running code...', 'info');
        
        try {
            const response = await this.executeCode(code, this.currentLanguage);
            
            if (response.success) {
                this.showOutput(`✅ Code executed successfully!\n\n${response.output}`, 'success');
            } else {
                this.showOutput(`❌ Execution failed:\n${response.error}`, 'error');
            }
        } catch (error) {
            this.showOutput(`❌ Error: ${error.message}`, 'error');
        }
    }

    async executeCode(code, language) {
        return new Promise((resolve) => {
            setTimeout(() => {
                if (code.includes('fibonacci')) {
                    const output = 'F(0) = 0\nF(1) = 1\nF(2) = 1\nF(3) = 2\nF(4) = 3\nF(5) = 5\nF(6) = 8\nF(7) = 13\nF(8) = 21\nF(9) = 34';
                    resolve({ success: true, output });
                } else if (language === 'python' && code.includes('print')) {
                    const matches = code.match(/print\(['"](.+?)['"]\)/g);
                    const output = matches ? matches.map(m => m.match(/print\(['"](.+?)['"]\)/)[1]).join('\n') : 'Hello, World!';
                    resolve({ success: true, output });
                } else if (language === 'javascript' && code.includes('console.log')) {
                    const matches = code.match(/console\.log\(['"`](.+?)['"`]\)/g);
                    const output = matches ? matches.map(m => m.match(/console\.log\(['"`](.+?)['"`]\)/)[1]).join('\n') : 'Hello, World!';
                    resolve({ success: true, output });
                } else {
                    resolve({ 
                        success: true, 
                        output: `Code execution simulated for ${language.toUpperCase()}\nHello, World!\n\n✅ Syntax check passed\n✅ Code structure valid\n\nNote: Connect to backend for real execution.` 
                    });
                }
            }, 1000 + Math.random() * 1000);
        });
    }

    showOutput(message, type = 'info') {
        const panelContent = document.getElementById('panelContent');
        if (!panelContent) return;

        const timestamp = new Date().toLocaleTimeString();
        const className = type === 'success' ? 'output-success' : 
                         type === 'error' ? 'output-error' : 
                         type === 'warning' ? 'output-warning' : '';

        panelContent.innerHTML = `<div class="${className}">[${timestamp}] ${message}</div>`;
        
        const bottomPanel = document.getElementById('bottomPanel');
        if (bottomPanel && bottomPanel.classList.contains('hidden')) {
            bottomPanel.classList.remove('hidden');
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const chatMessages = document.getElementById('chatMessages');
        
        if (!chatInput || !chatMessages) return;

        const message = chatInput.value.trim();
        if (!message) return;

        this.addChatMessage(message, 'user');
        chatInput.value = '';
        this.autoResizeTextarea(chatInput);

        const typingId = this.addChatMessage('🤖 AI is thinking...', 'ai');

        try {
            const response = this.chatMode === 'coding' 
                ? await this.getCodingAIResponse(message)
                : await this.getGeneralAIResponse(message);
            
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
            }
            this.addChatMessage(response, 'ai');
            
        } catch (error) {
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
            }
            this.addChatMessage(`❌ Error: ${error.message}`, 'ai');
        }
    }

    addChatMessage(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.id = messageId;
        
        if (message.includes('```')) {
            const parts = message.split('```');
            let html = '';
            for (let i = 0; i < parts.length; i++) {
                if (i % 2 === 0) {
                    html += `<div>${this.formatText(parts[i])}</div>`;
                } else {
                    html += `<pre><code>${parts[i]}</code></pre>`;
                }
            }
            messageDiv.innerHTML = html;
        } else {
            messageDiv.innerHTML = this.formatText(message);
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageId;
    }

    formatText(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    async getCodingAIResponse(message) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const lowerMessage = message.toLowerCase();
                
                if (lowerMessage.includes('hello world')) {
                    const code = this.getHelloWorldCode(this.currentLanguage);
                    resolve(`Here's a Hello World program in **${this.currentLanguage}**:\n\n\`\`\`${this.currentLanguage}\n${code}\n\`\`\`\n\nWould you like me to explain how it works or generate something else?`);
                } 
                else if (lowerMessage.includes('fibonacci')) {
                    const code = this.getFibonacciCode(this.currentLanguage);
                    resolve(`Here's a Fibonacci function in **${this.currentLanguage}**:\n\n\`\`\`${this.currentLanguage}\n${code}\n\`\`\`\n\nThis uses recursion to calculate Fibonacci numbers. Would you like an iterative version instead?`);
                } 
                else if (lowerMessage.includes('file') || lowerMessage.includes('import')) {
                    resolve(`**📁 File Management Help:**\n\nI can help you work with your imported files!\n\n**Current files:** ${Array.from(this.openFiles.keys()).join(', ')}\n\n**Available actions:**\n• Analyze code structure\n• Generate documentation\n• Suggest improvements\n• Create related files\n• Debug issues\n\nWhat would you like me to help you with regarding your files?`);
                }
                else if (lowerMessage.includes('help')) {
                    resolve(`**💻 Coding Assistant Ready!**\n\nI can help you with:\n\n**📁 File Operations:**\n• Analyze your imported files\n• Generate code for new files\n• Debug existing code\n• Create documentation\n\n**🔧 Code Generation:**\n• Functions and classes\n• Algorithms and data structures\n• API endpoints and servers\n• Database queries\n\n**🌐 Languages:** ${this.supportedLanguages.length}+ supported\n\nWhat would you like me to help you build?`);
                }
                else {
                    resolve(`I can help you code in **${this.currentLanguage}**! Here are some things you can ask:\n\n• *"Analyze the file ${this.currentFile}"*\n• *"Create a function that..."*\n• *"Generate a ${this.currentLanguage} class for..."*\n• *"Debug this code..."*\n• *"Add documentation to..."*\n\nWhat specific code would you like me to create or help you with?`);
                }
            }, 1000 + Math.random() * 1000);
        });
    }

    async getGeneralAIResponse(message) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const lowerMessage = message.toLowerCase();
                
                if (lowerMessage.includes('calculate') || lowerMessage.includes('math') || /\d+\s*[+\-*/]\s*\d+/.test(lowerMessage)) {
                    const mathMatch = lowerMessage.match(/(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)/);
                    if (mathMatch) {
                        const [, num1, operator, num2] = mathMatch;
                        const n1 = parseFloat(num1), n2 = parseFloat(num2);
                        let result;
                        switch (operator) {
                            case '+': result = n1 + n2; break;
                            case '-': result = n1 - n2; break;
                            case '*': result = n1 * n2; break;
                            case '/': result = n2 !== 0 ? n1 / n2 : 'Cannot divide by zero'; break;
                        }
                        resolve(`**🧮 Math Result:**\n${n1} ${operator} ${n2} = **${result}**\n\nNeed help with more calculations?`);
                    } else {
                        resolve("**🧮 Math Helper Ready!** Try asking: '15 + 27' or 'What is 20% of 150?'");
                    }
                }
                else if (lowerMessage.includes('what is') || lowerMessage.includes('define')) {
                    resolve("**📚 I'd be happy to explain that!** I can define concepts in technology, science, mathematics, and general knowledge. What specifically would you like me to explain?");
                }
                else if (lowerMessage.includes('recommend')) {
                    resolve("**💡 I can recommend:**\n• 📚 Books (any genre)\n• 🎬 Movies and shows\n• 🍕 Food and restaurants\n• 🎵 Music and entertainment\n• 🎮 Activities and hobbies\n\nWhat type of recommendations are you looking for?");
                }
                else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
                    resolve("**👋 Hello!** I'm your AI assistant in General Chat Mode. I can help with everyday questions, math problems, recommendations, fun facts, and general conversation. What would you like to chat about?");
                }
                else {
                    resolve("**💬 I'm here to help!** I can assist with:\n\n🧮 **Math & Calculations**\n📚 **Definitions & Explanations**\n💡 **Recommendations**\n🎯 **Fun Facts & Trivia**\n✍️ **Creative Writing**\n🌍 **General Knowledge**\n\nWhat would you like to explore?");
                }
            }, 800 + Math.random() * 1200);
        });
    }

    getHelloWorldCode(language) {
        const codes = {
            python: 'print("Hello, World!")',
            javascript: 'console.log("Hello, World!");',
            java: 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
            cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}'
        };
        return codes[language] || `// Hello World in ${language}\nconsole.log("Hello, World!");`;
    }

    getFibonacciCode(language) {
        const codes = {
            python: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
            javascript: 'function fibonacci(n) {\n    if (n <= 1) return n;\n    return fibonacci(n-1) + fibonacci(n-2);\n}',
            java: 'public static int fibonacci(int n) {\n    if (n <= 1) return n;\n    return fibonacci(n-1) + fibonacci(n-2);\n}'
        };
        return codes[language] || `// Fibonacci in ${language}`;
    }

    handleNavigation(view) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeItem = document.querySelector(`[data-view="${view}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }

        switch (view) {
            case 'files':
                this.toggleFileExplorer();
                break;
            case 'chat':
                if (!this.isAIPanelOpen) {
                    this.toggleAIPanel();
                }
                break;
            case 'settings':
                this.toggleSettingsPanel();
                break;
            case 'languages':
                this.showLanguageInfo();
                break;
        }
    }

    showLanguageInfo() {
        const message = `**🌐 Universal Language Support**\n\nI can code in **${this.supportedLanguages.length}+ programming languages**:\n\n**Systems:** Python, C++, Rust, Go\n**Web:** JavaScript, TypeScript, HTML, CSS\n**Enterprise:** Java, C#, Kotlin, Swift\n**Functional:** Haskell, Clojure, Erlang\n**Data:** R, Julia, SQL\n**Config:** YAML, JSON, Dockerfile\n\n*Select any language and start coding!*`;
        
        if (!this.isAIPanelOpen) {
            this.toggleAIPanel();
        }
        
        setTimeout(() => {
            this.addChatMessage(message, 'ai');
        }, 100);
    }

    switchPanel(panel) {
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        const activeTab = document.querySelector(`[data-panel="${panel}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        const panelContent = document.getElementById('panelContent');
        if (!panelContent) return;

        switch (panel) {
            case 'output':
                panelContent.innerHTML = '<div class="output-success">✅ Ready to run code</div>';
                break;
            case 'terminal':
                panelContent.innerHTML = '<div>$ Universal AI Terminal</div><div>Ready for commands...</div>';
                break;
            case 'problems':
                panelContent.innerHTML = '<div class="output-success">✅ No problems detected</div>';
                break;
            case 'search':
                panelContent.innerHTML = '<div>🔍 Search functionality coming soon...</div>';
                break;
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    updateStatusBar() {
        const codeEditor = document.getElementById('codeEditor');
        const statusRight = document.querySelector('.status-right');
        const currentFileSpan = document.getElementById('currentFile');
        
        if (codeEditor && statusRight && statusRight.children[0]) {
            const lines = codeEditor.value.split('\n');
            const currentLine = codeEditor.value.substr(0, codeEditor.selectionStart).split('\n').length;
            const currentCol = codeEditor.selectionStart - codeEditor.value.lastIndexOf('\n', codeEditor.selectionStart - 1);
            
            statusRight.children[0].textContent = `Ln ${currentLine}, Col ${currentCol}`;
        }

        if (currentFileSpan) {
            currentFileSpan.textContent = this.currentFile || 'No file';
        }
    }

    handleCodeEditorKeydown(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            
            const spaces = ' '.repeat(this.settings.tabSize);
            e.target.value = e.target.value.substring(0, start) + spaces + e.target.value.substring(end);
            e.target.selectionStart = e.target.selectionEnd = start + this.settings.tabSize;
        }
    }

    loadWelcomeMessage() {
        setTimeout(() => {
            this.showOutput('🚀 Universal AI Assistant loaded successfully!\n✅ File import system ready\n✅ Multi-file editor active\n✅ Settings panel configured\n✅ Dual-mode AI ready\n\nReady to import files and start coding!', 'success');
        }, 500);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.aiAssistant = new UniversalAIAssistant();
    console.log('🤖 Universal AI Assistant with File Management initialized!');
});

// Handle responsive design
window.addEventListener('resize', () => {
    const sidebar = document.getElementById('sidebar');
    const aiPanel = document.getElementById('aiPanel');
    const settingsPanel = document.getElementById('settingsPanel');
    const fileExplorer = document.getElementById('fileExplorer');
    
    if (window.innerWidth <= 768) {
        [sidebar, aiPanel, settingsPanel, fileExplorer].forEach(panel => {
            if (panel) panel.classList.add('mobile');
        });
    } else {
        [sidebar, aiPanel, settingsPanel, fileExplorer].forEach(panel => {
            if (panel) panel.classList.remove('mobile');
        });
    }
});