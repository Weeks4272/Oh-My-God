// Universal AI Assistant - Complete Implementation with Fixed Send Function
let universalAI, fileManager, uiManager;

class UniversalAI {
    constructor() {
        this.conversationHistory = [];
        this.currentMode = 'coding';
        this.restrictions = this.loadRestrictions();
        this.contextMemory = new Map();
        this.userProfile = {
            interests: [],
            expertise: [],
            conversationStyle: 'balanced'
        };
    }

    loadRestrictions() {
        try {
            const stored = localStorage.getItem('aiRestrictions');
            return stored ? JSON.parse(stored) : {
                prohibitedContent: [],
                restrictedTopics: [],
                contentFilters: {
                    violence: false,
                    adult: false,
                    hate: false,
                    misinformation: false
                },
                customRules: [],
                warningMessages: {
                    contentBlocked: "This content is restricted by your current settings.",
                    topicRestricted: "This topic is currently restricted."
                }
            };
        } catch (error) {
            console.error('Error loading restrictions:', error);
            return { prohibitedContent: [], restrictedTopics: [], contentFilters: {}, customRules: [], warningMessages: {} };
        }
    }

    async generateResponse(userInput, mode = 'coding') {
        try {
            // Check restrictions first
            const restrictionCheck = this.checkRestrictions(userInput);
            if (restrictionCheck.blocked) {
                return {
                    type: 'blocked',
                    content: restrictionCheck.message,
                    timestamp: new Date().toISOString()
                };
            }

            // Generate dynamic response based on input
            const response = await this.generateDynamicResponse(userInput, mode);
            this.updateConversationHistory(userInput, response);
            
            return {
                type: 'ai',
                content: response,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('Error generating response:', error);
            return {
                type: 'error',
                content: "I apologize, but I encountered an error processing your request. Please try rephrasing your question.",
                timestamp: new Date().toISOString()
            };
        }
    }

    async generateDynamicResponse(input, mode) {
        // Simulate thinking time for more realistic responses
        await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1500));

        const lowerInput = input.toLowerCase();
        
        // Handle greetings
        if (this.isGreeting(lowerInput)) {
            return this.generateGreetingResponse(input);
        }

        // Handle coding questions - PRIORITIZE CODE GENERATION
        if (mode === 'coding' || this.isCodingRelated(lowerInput)) {
            return this.generateActualCode(input);
        }

        // Handle questions
        if (this.isQuestion(lowerInput)) {
            return this.generateQuestionResponse(input);
        }

        // Handle requests for help or explanation
        if (this.isHelpRequest(lowerInput)) {
            return this.generateHelpResponse(input);
        }

        // Handle creative requests
        if (this.isCreativeRequest(lowerInput)) {
            return this.generateCreativeResponse(input);
        }

        // Handle math/calculation requests
        if (this.isMathRequest(lowerInput)) {
            return this.generateMathResponse(input);
        }

        // Handle personal/advice requests
        if (this.isPersonalAdvice(lowerInput)) {
            return this.generatePersonalResponse(input);
        }

        // Default conversational response
        return this.generateConversationalResponse(input);
    }

    isGreeting(input) {
        const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'];
        return greetings.some(greeting => input.includes(greeting));
    }

    isCodingRelated(input) {
        const codingKeywords = [
            'code', 'programming', 'function', 'variable', 'class', 'method', 'algorithm', 
            'debug', 'error', 'syntax', 'python', 'javascript', 'java', 'html', 'css', 
            'react', 'node', 'api', 'database', 'sql', 'git', 'github', 'framework',
            'library', 'package', 'install', 'compile', 'run', 'execute', 'script',
            'make', 'create', 'build', 'write', 'develop', 'app', 'website', 'program'
        ];
        return codingKeywords.some(keyword => input.includes(keyword));
    }

    isQuestion(input) {
        const questionWords = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you', 'could you', 'would you'];
        return questionWords.some(word => input.includes(word)) || input.includes('?');
    }

    isHelpRequest(input) {
        const helpKeywords = ['help', 'assist', 'explain', 'teach', 'show me', 'guide', 'tutorial'];
        return helpKeywords.some(keyword => input.includes(keyword));
    }

    isCreativeRequest(input) {
        const creativeKeywords = ['write', 'create', 'story', 'poem', 'song', 'creative', 'imagine', 'design', 'brainstorm'];
        return creativeKeywords.some(keyword => input.includes(keyword));
    }

    isMathRequest(input) {
        const mathKeywords = ['calculate', 'math', 'equation', 'solve', 'formula', 'number'];
        const hasNumbers = /\d/.test(input);
        const hasMathSymbols = /[+\-*/=]/.test(input);
        return mathKeywords.some(keyword => input.includes(keyword)) || (hasNumbers && hasMathSymbols);
    }

    isPersonalAdvice(input) {
        const adviceKeywords = ['advice', 'should i', 'what do you think', 'recommend', 'suggest', 'opinion'];
        return adviceKeywords.some(keyword => input.includes(keyword));
    }

    generateActualCode(input) {
        const lowerInput = input.toLowerCase();
        
        // Detect what type of code they want
        if (lowerInput.includes('calculator') || lowerInput.includes('calc')) {
            return this.generateCalculatorCode(input);
        }
        
        if (lowerInput.includes('todo') || lowerInput.includes('task')) {
            return this.generateTodoAppCode(input);
        }
        
        // Default: Generate a complete working example based on the request
        return this.generateDefaultCode(input);
    }

    generateCalculatorCode(input) {
        return `Here's a complete working calculator application:

\`\`\`html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .calculator {
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .display {
            width: 100%;
            height: 60px;
            font-size: 24px;
            text-align: right;
            padding: 0 10px;
            border: none;
            background: #f0f0f0;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        button {
            height: 60px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .number, .decimal {
            background: #e0e0e0;
        }
        .operator {
            background: #ff9500;
            color: white;
        }
        .equals {
            background: #ff9500;
            color: white;
        }
        .clear {
            background: #a6a6a6;
            color: white;
        }
        button:hover {
            transform: scale(1.05);
        }
        button:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="calculator">
        <input type="text" class="display" id="display" readonly>
        <div class="buttons">
            <button class="clear" onclick="clearDisplay()">C</button>
            <button class="clear" onclick="deleteLast()">⌫</button>
            <button class="operator" onclick="appendToDisplay('/')">/</button>
            <button class="operator" onclick="appendToDisplay('*')">×</button>
            
            <button class="number" onclick="appendToDisplay('7')">7</button>
            <button class="number" onclick="appendToDisplay('8')">8</button>
            <button class="number" onclick="appendToDisplay('9')">9</button>
            <button class="operator" onclick="appendToDisplay('-')">-</button>
            
            <button class="number" onclick="appendToDisplay('4')">4</button>
            <button class="number" onclick="appendToDisplay('5')">5</button>
            <button class="number" onclick="appendToDisplay('6')">6</button>
            <button class="operator" onclick="appendToDisplay('+')">+</button>
            
            <button class="number" onclick="appendToDisplay('1')">1</button>
            <button class="number" onclick="appendToDisplay('2')">2</button>
            <button class="number" onclick="appendToDisplay('3')">3</button>
            <button class="equals" onclick="calculate()" rowspan="2">=</button>
            
            <button class="number" onclick="appendToDisplay('0')" style="grid-column: span 2;">0</button>
            <button class="decimal" onclick="appendToDisplay('.')">.</button>
        </div>
    </div>

    <script>
        let display = document.getElementById('display');
        let currentInput = '';
        let operator = '';
        let previousInput = '';

        function appendToDisplay(value) {
            if (['+', '-', '*', '/'].includes(value)) {
                if (currentInput !== '') {
                    if (previousInput !== '' && operator !== '') {
                        calculate();
                    }
                    previousInput = currentInput;
                    operator = value;
                    currentInput = '';
                    display.value = previousInput + ' ' + value + ' ';
                }
            } else {
                currentInput += value;
                display.value += value;
            }
        }

        function calculate() {
            if (previousInput !== '' && currentInput !== '' && operator !== '') {
                let result;
                const prev = parseFloat(previousInput);
                const current = parseFloat(currentInput);
                
                switch (operator) {
                    case '+':
                        result = prev + current;
                        break;
                    case '-':
                        result = prev - current;
                        break;
                    case '*':
                        result = prev * current;
                        break;
                    case '/':
                        result = current !== 0 ? prev / current : 'Error';
                        break;
                    default:
                        return;
                }
                
                display.value = result;
                currentInput = result.toString();
                previousInput = '';
                operator = '';
            }
        }

        function clearDisplay() {
            display.value = '';
            currentInput = '';
            previousInput = '';
            operator = '';
        }

        function deleteLast() {
            display.value = display.value.slice(0, -1);
            if (currentInput !== '') {
                currentInput = currentInput.slice(0, -1);
            }
        }

        // Keyboard support
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            if ('0123456789.'.includes(key)) {
                appendToDisplay(key);
            } else if ('+-*/'.includes(key)) {
                appendToDisplay(key);
            } else if (key === 'Enter' || key === '=') {
                calculate();
            } else if (key === 'Escape' || key === 'c' || key === 'C') {
                clearDisplay();
            } else if (key === 'Backspace') {
                deleteLast();
            }
        });
    </script>
</body>
</html>
\`\`\`

✅ **Features:** Full calculator with keyboard support, error handling, and modern design
✅ **Usage:** Save as HTML file and open in browser - fully functional!`;
    }

    generateTodoAppCode(input) {
        return `Here's a complete Todo List application:

\`\`\`html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        h1 { text-align: center; color: #333; margin-bottom: 30px; font-size: 2.5rem; }
        .input-container { display: flex; gap: 10px; margin-bottom: 30px; }
        #todoInput {
            flex: 1; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px;
            font-size: 16px; outline: none; transition: border-color 0.3s;
        }
        #todoInput:focus { border-color: #667eea; }
        #addBtn {
            padding: 15px 25px; background: #667eea; color: white; border: none;
            border-radius: 10px; cursor: pointer; font-size: 16px; transition: background 0.3s;
        }
        #addBtn:hover { background: #5a6fd8; }
        #todoList { list-style: none; }
        .todo-item {
            display: flex; align-items: center; padding: 15px; margin-bottom: 10px;
            background: #f8f9fa; border-radius: 10px; transition: all 0.3s;
        }
        .todo-item.completed { opacity: 0.7; text-decoration: line-through; }
        .todo-checkbox { margin-right: 15px; width: 20px; height: 20px; cursor: pointer; }
        .todo-text { flex: 1; font-size: 16px; }
        .delete-btn {
            background: #ff4757; color: white; border: none; padding: 8px 12px;
            border-radius: 5px; cursor: pointer; transition: background 0.3s;
        }
        .delete-btn:hover { background: #ff3742; }
        .stats {
            text-align: center; margin-top: 20px; padding: 15px;
            background: #f8f9fa; border-radius: 10px;
        }
        .empty-state { text-align: center; color: #666; font-style: italic; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 My Todo List</h1>
        <div class="input-container">
            <input type="text" id="todoInput" placeholder="Add a new task..." maxlength="100">
            <button id="addBtn">Add Task</button>
        </div>
        <ul id="todoList"></ul>
        <div class="stats">
            <span id="totalTasks">0</span> total tasks, 
            <span id="completedTasks">0</span> completed, 
            <span id="activeTasks">0</span> remaining
        </div>
    </div>

    <script>
        class TodoApp {
            constructor() {
                this.todos = JSON.parse(localStorage.getItem('todos')) || [];
                this.init();
            }
            
            init() {
                this.bindEvents();
                this.render();
            }
            
            bindEvents() {
                document.getElementById('addBtn').addEventListener('click', () => this.addTodo());
                document.getElementById('todoInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.addTodo();
                });
            }
            
            addTodo() {
                const input = document.getElementById('todoInput');
                const text = input.value.trim();
                if (text === '') return;
                
                const todo = {
                    id: Date.now(),
                    text: text,
                    completed: false,
                    createdAt: new Date().toLocaleDateString()
                };
                
                this.todos.unshift(todo);
                this.saveTodos();
                this.render();
                input.value = '';
            }
            
            toggleTodo(id) {
                this.todos = this.todos.map(todo => 
                    todo.id === id ? { ...todo, completed: !todo.completed } : todo
                );
                this.saveTodos();
                this.render();
            }
            
            deleteTodo(id) {
                this.todos = this.todos.filter(todo => todo.id !== id);
                this.saveTodos();
                this.render();
            }
            
            render() {
                const todoList = document.getElementById('todoList');
                
                if (this.todos.length === 0) {
                    todoList.innerHTML = '<li class="empty-state">No tasks found. Add one above!</li>';
                } else {
                    todoList.innerHTML = this.todos.map(todo => \`
                        <li class="todo-item \${todo.completed ? 'completed' : ''}">
                            <input type="checkbox" class="todo-checkbox" 
                                   \${todo.completed ? 'checked' : ''} 
                                   onchange="app.toggleTodo(\${todo.id})">
                            <span class="todo-text">\${todo.text}</span>
                            <button class="delete-btn" onclick="app.deleteTodo(\${todo.id})">Delete</button>
                        </li>
                    \`).join('');
                }
                this.updateStats();
            }
            
            updateStats() {
                const total = this.todos.length;
                const completed = this.todos.filter(todo => todo.completed).length;
                const active = total - completed;
                
                document.getElementById('totalTasks').textContent = total;
                document.getElementById('completedTasks').textContent = completed;
                document.getElementById('activeTasks').textContent = active;
            }
            
            saveTodos() {
                localStorage.setItem('todos', JSON.stringify(this.todos));
            }
        }
        
        const app = new TodoApp();
    </script>
</body>
</html>
\`\`\`

✅ **Features:** Add/delete tasks, mark complete, persistent storage, statistics
✅ **Usage:** Save as HTML file and open in browser - your tasks will be saved!`;
    }

    generateDefaultCode(input) {
        return `I'll create a complete working application for you! Here's a versatile web app template:

\`\`\`html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Web App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .app-container {
            max-width: 800px; margin: 0 auto; background: white;
            border-radius: 20px; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        .feature-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .feature-card {
            background: #f8f9fa; padding: 20px; border-radius: 10px;
            text-align: center; transition: transform 0.3s;
        }
        .feature-card:hover { transform: translateY(-5px); }
        .feature-icon { font-size: 3rem; margin-bottom: 15px; }
        .feature-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 10px; }
        .btn {
            background: #667eea; color: white; border: none; padding: 12px 24px;
            border-radius: 25px; cursor: pointer; font-size: 16px; transition: all 0.3s;
        }
        .btn:hover { background: #5a6fd8; transform: translateY(-2px); }
        .interactive-section {
            background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;
        }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        .input-group input {
            flex: 1; padding: 10px; border: 2px solid #e0e0e0; border-radius: 5px;
        }
        .output { background: white; padding: 15px; border-radius: 5px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="app-container">
        <h1>🚀 Interactive Web Application</h1>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Smart Features</div>
                <p>Interactive elements with real-time updates</p>
                <button class="btn" onclick="app.runFeature('smart')">Try It</button>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Data Processing</div>
                <p>Process and visualize your data instantly</p>
                <button class="btn" onclick="app.runFeature('data')">Process</button>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <div class="feature-title">Creative Tools</div>
                <p>Generate and customize content dynamically</p>
                <button class="btn" onclick="app.runFeature('creative')">Create</button>
            </div>
        </div>
        
        <div class="interactive-section">
            <h3>Interactive Demo</h3>
            <div class="input-group">
                <input type="text" id="userInput" placeholder="Enter something to process...">
                <button class="btn" onclick="app.processInput()">Process</button>
            </div>
            <div class="output" id="output">Results will appear here...</div>
        </div>
    </div>

    <script>
        class WebApp {
            constructor() {
                this.data = [];
                this.init();
            }
            
            init() {
                console.log('Web App initialized successfully!');
                this.bindEvents();
            }
            
            bindEvents() {
                document.getElementById('userInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.processInput();
                });
            }
            
            runFeature(type) {
                const output = document.getElementById('output');
                
                switch(type) {
                    case 'smart':
                        output.innerHTML = \`
                            <h4>🎯 Smart Feature Activated!</h4>
                            <p>Current time: \${new Date().toLocaleString()}</p>
                            <p>Random number: \${Math.floor(Math.random() * 1000)}</p>
                            <p>User agent: \${navigator.userAgent.split(' ')[0]}</p>
                        \`;
                        break;
                        
                    case 'data':
                        const sampleData = Array.from({length: 10}, () => Math.floor(Math.random() * 100));
                        const average = sampleData.reduce((a, b) => a + b, 0) / sampleData.length;
                        output.innerHTML = \`
                            <h4>📊 Data Analysis Complete!</h4>
                            <p>Sample data: [\${sampleData.join(', ')}]</p>
                            <p>Average: \${average.toFixed(2)}</p>
                            <p>Max: \${Math.max(...sampleData)}</p>
                            <p>Min: \${Math.min(...sampleData)}</p>
                        \`;
                        break;
                        
                    case 'creative':
                        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
                        const randomColor = colors[Math.floor(Math.random() * colors.length)];
                        output.innerHTML = \`
                            <h4>🎨 Creative Content Generated!</h4>
                            <div style="width: 100px; height: 100px; background: \${randomColor}; 
                                        border-radius: 50%; margin: 10px auto;"></div>
                            <p>Random color: \${randomColor}</p>
                            <p>Generated at: \${new Date().toLocaleTimeString()}</p>
                        \`;
                        break;
                }
            }
            
            processInput() {
                const input = document.getElementById('userInput');
                const value = input.value.trim();
                const output = document.getElementById('output');
                
                if (!value) {
                    output.innerHTML = '<p style="color: #e74c3c;">Please enter something to process!</p>';
                    return;
                }
                
                // Process the input
                const wordCount = value.split(' ').length;
                const charCount = value.length;
                const reversed = value.split('').reverse().join('');
                const uppercase = value.toUpperCase();
                
                output.innerHTML = \`
                    <h4>✨ Input Processed Successfully!</h4>
                    <p><strong>Original:</strong> \${value}</p>
                    <p><strong>Word count:</strong> \${wordCount}</p>
                    <p><strong>Character count:</strong> \${charCount}</p>
                    <p><strong>Reversed:</strong> \${reversed}</p>
                    <p><strong>Uppercase:</strong> \${uppercase}</p>
                    <p><strong>Processed at:</strong> \${new Date().toLocaleString()}</p>
                \`;
                
                input.value = '';
            }
        }
        
        const app = new WebApp();
    </script>
</body>
</html>
\`\`\`

✅ **Features:** Interactive cards, data processing, real-time updates, responsive design
✅ **Usage:** Save as HTML file and open in browser - fully functional web app!

**What specific type of application would you like me to create next?**`;
    }

    generateGreetingResponse(input) {
        const responses = [
            "Hello! I'm here and ready to help you with anything you need. What's on your mind today?",
            "Hi there! Great to see you. What would you like to explore or work on together?",
            "Hey! I'm excited to assist you today. What can I help you with?",
            "Hello! I'm your AI assistant, ready to tackle any questions or tasks you have. What shall we dive into?"
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }

    generateQuestionResponse(input) {
        return `I'd be happy to answer your question! 

To provide you with the most helpful and accurate response, could you give me a bit more detail about what specifically you'd like to know?

Whether it's about:
- Technical concepts or programming
- How something works
- Explanations of complex topics
- Step-by-step guidance
- Or anything else you're curious about

The more context you provide, the better I can tailor my response to exactly what you need!`;
    }

    generateHelpResponse(input) {
        return `I'm absolutely here to help! I can assist you with a wide range of topics and tasks.

**I'm particularly good at:**
- Creating complete, working code applications
- Explaining complex concepts clearly
- Providing step-by-step guidance
- Solving technical problems
- Writing and creative tasks

**Popular requests I handle:**
- "Create a calculator app"
- "Build a todo list"
- "Make a weather app"
- "Write a contact form"
- "Build a dashboard"
- "Create a game"

What specific challenge are you facing? Just describe what you need, and I'll create or explain it for you!`;
    }

    generateCreativeResponse(input) {
        return `I'd love to help with your creative project! 

**Creative tasks I excel at:**
- Writing stories, poems, and scripts
- Brainstorming ideas and concepts
- Creating interactive web applications
- Designing user interfaces
- Building creative coding projects

**To get started, let me know:**
- What type of creative project interests you?
- Any specific themes or styles you prefer?
- Is this for personal use, work, or learning?

I can create complete, working examples or help you brainstorm ideas. What creative challenge would you like to tackle?`;
    }

    generateMathResponse(input) {
        // Try to identify and solve basic math problems
        const mathMatch = input.match(/(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)/);
        
        if (mathMatch) {
            const [, num1, operator, num2] = mathMatch;
            const a = parseFloat(num1);
            const b = parseFloat(num2);
            let result;
            
            switch (operator) {
                case '+': result = a + b; break;
                case '-': result = a - b; break;
                case '*': result = a * b; break;
                case '/': result = b !== 0 ? a / b : 'undefined (division by zero)'; break;
            }
            
            return `**Calculation Result:**
${a} ${operator} ${b} = **${result}**

I can help with various mathematical concepts:
- Basic arithmetic and algebra
- Geometry and trigonometry  
- Statistics and probability
- Creating calculator applications
- Mathematical visualizations

Need help with anything else mathematical?`;
        }

        return `I'm ready to help with your math question!

**Mathematical areas I can assist with:**
- **Calculations**: Arithmetic, percentages, conversions
- **Algebra**: Equations, functions, graphing
- **Geometry**: Areas, volumes, angles
- **Statistics**: Averages, probability, data analysis
- **Applications**: Creating calculator apps, data visualizations

What mathematical concept or problem would you like help with? I can solve it step-by-step or even create a calculator app for you!`;
    }

    generatePersonalResponse(input) {
        return `I'm happy to offer some perspective and guidance!

**I can help you think through:**
- **Decision Making**: Weighing pros and cons, exploring options
- **Goal Setting**: Breaking down objectives into actionable steps
- **Problem Solving**: Finding creative solutions to challenges
- **Learning**: Strategies for acquiring new skills
- **Productivity**: Time management and organization

**My approach:**
- Listen to your specific situation
- Offer multiple perspectives to consider
- Suggest practical next steps
- Help you organize your thoughts

What's on your mind? I'm here to help you work through whatever you're facing, whether it's a decision, challenge, or goal you're pursuing.`;
    }

    generateConversationalResponse(input) {
        const responses = [
            `That's interesting! I'd love to hear more about what you're thinking. Could you tell me a bit more about that?`,
            
            `I appreciate you sharing that with me. What aspects of this topic are you most curious about or would like to explore further?`,
            
            `Thanks for bringing that up! I'm here to help however I can. What would be most useful for you right now?`,
            
            `That sounds like something worth discussing! What's your perspective on it, and is there anything specific you'd like my input on?`,
            
            `I'm glad you brought that to my attention. Whether you're looking for information, analysis, creative ideas, or just want to talk it through, I'm here to help. What would be most valuable for you?`
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    checkRestrictions(input) {
        try {
            const restrictions = this.restrictions;
            
            // Check prohibited content
            for (const prohibited of restrictions.prohibitedContent || []) {
                if (new RegExp(prohibited, 'i').test(input)) {
                    return {
                        blocked: true,
                        message: restrictions.warningMessages?.contentBlocked || "This content is restricted by your current settings."
                    };
                }
            }
            
            // Check custom rules
            for (const rule of restrictions.customRules || []) {
                if (new RegExp(rule, 'i').test(input)) {
                    return {
                        blocked: true,
                        message: restrictions.warningMessages?.contentBlocked || "This content is restricted by your custom rules."
                    };
                }
            }
            
            return { blocked: false };
            
        } catch (error) {
            console.error('Error checking restrictions:', error);
            return { blocked: false };
        }
    }

    updateConversationHistory(userInput, aiResponse) {
        const entry = {
            timestamp: new Date().toISOString(),
            user: userInput,
            ai: aiResponse
        };
        
        this.conversationHistory.push(entry);
        
        // Keep only last 50 conversations
        if (this.conversationHistory.length > 50) {
            this.conversationHistory = this.conversationHistory.slice(-50);
        }
    }

    saveRestrictions(restrictions) {
        try {
            this.restrictions = restrictions;
            localStorage.setItem('aiRestrictions', JSON.stringify(restrictions));
            return true;
        } catch (error) {
            console.error('Error saving restrictions:', error);
            return false;
        }
    }
}

class FileManager {
    constructor() {
        this.files = this.loadFiles();
        this.activeFile = null;
    }

    loadFiles() {
        try {
            const stored = localStorage.getItem('projectFiles');
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('Error loading files:', error);
            return {};
        }
    }

    saveFiles() {
        try {
            localStorage.setItem('projectFiles', JSON.stringify(this.files));
        } catch (error) {
            console.error('Error saving files:', error);
        }
    }

    createFile(path, content = '', language = 'text') {
        const name = path.split('/').pop();
        this.files[path] = {
            name,
            content,
            language,
            modified: false
        };
        this.saveFiles();
        return this.files[path];
    }

    updateFile(path, content) {
        if (this.files[path]) {
            this.files[path].content = content;
            this.files[path].modified = true;
            this.saveFiles();
        }
    }

    getFile(path) {
        return this.files[path];
    }

    getAllFiles() {
        return this.files;
    }
}

class UIManager {
    constructor() {
        this.currentView = 'chat';
        this.currentMode = 'coding';
        this.setupEventListeners();
        this.initializeUI();
    }

    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.currentTarget.dataset.view;
                console.log('Navigation clicked:', view);
                
                if (view === 'restrictions') {
                    this.showRestrictionsModal();
                } else if (view === 'import') {
                    this.showImportModal();
                } else if (view === 'settings') {
                    this.showSettingsModal();
                } else {
                    this.switchView(view);
                }
            });
        });

        // FIXED: Chat functionality - Main chat input
        const sendButton = document.getElementById('sendMessage');
        const chatInput = document.getElementById('chatInput');
        
        console.log('Send button found:', !!sendButton);
        console.log('Chat input found:', !!chatInput);
        
        if (sendButton && chatInput) {
            // Remove any existing listeners first
            sendButton.replaceWith(sendButton.cloneNode(true));
            const newSendButton = document.getElementById('sendMessage');
            
            newSendButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Send button clicked!');
                this.sendMessage(chatInput, 'chatMessages');
            });
            
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('Enter key pressed!');
                    this.sendMessage(chatInput, 'chatMessages');
                }
            });
            
            console.log('✅ Main chat listeners attached');
        } else {
            console.error('❌ Main chat elements not found');
        }

        // Mode switching
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const mode = e.currentTarget.dataset.mode;
                console.log('Mode switched to:', mode);
                this.switchMode(mode);
            });
        });

        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const modal = e.target.closest('.modal-overlay');
                if (modal) {
                    modal.classList.add('hidden');
                }
            });
        });

        // Close AI panel
        const closeAI = document.getElementById('closeAI');
        if (closeAI) {
            closeAI.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById('aiPanel').classList.add('hidden');
            });
        }

        // File creation
        const createFileBtn = document.getElementById('createFile');
        if (createFileBtn) {
            createFileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.createNewFile();
            });
        }

        // Restrictions form handling
        const saveRestrictionsBtn = document.getElementById('saveRestrictions');
        if (saveRestrictionsBtn) {
            saveRestrictionsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveRestrictions();
            });
        }
        
        console.log('✅ All event listeners set up successfully');
    }

    initializeUI() {
        console.log('🎨 Initializing UI...');
        this.switchView('chat');
        this.showWelcomeMessage();
        console.log('✅ UI initialized');
    }

    showWelcomeMessage() {
        const welcomeMessage = `🚀 **Universal AI Assistant - Ready to Help!**

I'm here to create complete, working applications for you! I can build:

💻 **Complete Applications**
- Calculators with full functionality
- Todo lists with local storage
- Interactive games and tools
- Contact forms with validation
- Web applications and utilities

🎯 **Just Ask For What You Want:**
- "Create a calculator"
- "Build a todo app"
- "Make a simple game"
- "Create a contact form"
- "Build a web tool"

I'll provide complete, working code that you can save as HTML files and run immediately in your browser!

**What would you like me to build for you today?**`;

        this.addMessageToChat('ai', welcomeMessage, 'chatMessages');
    }

    switchView(view) {
        console.log('🔄 Switching to view:', view);
        
        // Hide all views
        document.querySelectorAll('.view').forEach(v => {
            v.classList.add('hidden');
        });

        // Show selected view
        const viewElement = document.getElementById(`${view}View`);
        if (viewElement) {
            viewElement.classList.remove('hidden');
            console.log('✅ View switched to:', view);
        } else {
            console.error('❌ View element not found:', `${view}View`);
        }

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-view="${view}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }

        this.currentView = view;
    }

    switchMode(mode) {
        console.log('🔄 Switching mode to:', mode);
        
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelectorAll(`[data-mode="${mode}"]`).forEach(btn => {
            btn.classList.add('active');
        });

        this.currentMode = mode;
        if (universalAI) {
            universalAI.currentMode = mode;
        }
    }

    async sendMessage(inputElement, messagesContainerId) {
        console.log('📤 Sending message...');
        
        if (!inputElement) {
            console.error('❌ Input element not found');
            return;
        }
        
        const message = inputElement.value.trim();
        console.log('Message content:', message);
        
        if (!message) {
            console.log('❌ Empty message, not sending');
            return;
        }

        // Clear input immediately
        inputElement.value = '';
        
        // Add user message
        this.addMessageToChat('user', message, messagesContainerId);
        this.showTypingIndicator(messagesContainerId);

        try {
            console.log('🤖 Generating AI response...');
            const response = await universalAI.generateResponse(message, this.currentMode);
            console.log('✅ AI response generated');
            
            this.hideTypingIndicator(messagesContainerId);
            this.addMessageToChat(response.type, response.content, messagesContainerId);
        } catch (error) {
            console.error('❌ Error generating response:', error);
            this.hideTypingIndicator(messagesContainerId);
            this.addMessageToChat('error', 'Sorry, I encountered an error processing your request.', messagesContainerId);
        }
    }

    addMessageToChat(type, content, containerId) {
        console.log('💬 Adding message to chat:', type);
        
        const chatMessages = document.getElementById(containerId);
        if (!chatMessages) {
            console.error('❌ Chat messages container not found:', containerId);
            return;
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${this.escapeHtml(content)}</div>
                <div class="message-time" style="font-size: 12px; color: #8b949e; margin-top: 4px;">${timestamp}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">${this.formatAIResponse(content)}</div>
                <div class="message-time" style="font-size: 12px; color: #8b949e; margin-top: 4px;">${timestamp}</div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        console.log('✅ Message added to chat');
    }

    formatAIResponse(content) {
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/g, '<pre style="background: #0d1117; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; border: 1px solid #30363d; color: #c9d1d9;"><code>$1</code></pre>')
            .replace(/`(.*?)`/g, '<code style="background: #0d1117; padding: 2px 6px; border-radius: 3px; font-size: 13px; color: #c9d1d9;">$1</code>')
            .replace(/\n/g, '<br>');
        
        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showTypingIndicator(containerId) {
        const chatMessages = document.getElementById(containerId);
        if (!chatMessages) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <em>Thinking...</em>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator(containerId) {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    createNewFile() {
        const fileName = prompt('Enter file name:');
        if (fileName && fileManager) {
            fileManager.createFile(fileName);
            this.updateFilesList();
            console.log('✅ File created:', fileName);
        }
    }

    updateFilesList() {
        const filesList = document.getElementById('filesList');
        if (!filesList || !fileManager) return;

        const files = fileManager.getAllFiles();
        const fileNames = Object.keys(files);

        if (fileNames.length === 0) {
            filesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📄</div>
                    <div class="empty-text">No files yet</div>
                    <div class="empty-subtext">Create your first file to get started</div>
                </div>
            `;
        } else {
            filesList.innerHTML = fileNames.map(fileName => `
                <div class="file-item" onclick="uiManager.openFile('${fileName}')">
                    <span class="file-icon">📄</span>
                    <span class="file-name">${fileName}</span>
                </div>
            `).join('');
        }
    }

    openFile(fileName) {
        if (fileManager) {
            const file = fileManager.getFile(fileName);
            if (file) {
                console.log('Opening file:', fileName, file);
                // Here you could open the file in an editor
            }
        }
    }

    showRestrictionsModal() {
        const modal = document.getElementById('restrictionsModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    showImportModal() {
        const modal = document.getElementById('importModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    showSettingsModal() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    saveRestrictions() {
        if (!universalAI) return;

        const restrictions = {
            prohibitedContent: [],
            restrictedTopics: [],
            contentFilters: {
                violence: document.getElementById('filterViolence')?.checked || false,
                adult: document.getElementById('filterAdult')?.checked || false,
                hate: document.getElementById('filterHate')?.checked || false,
                misinformation: document.getElementById('filterMisinformation')?.checked || false
            },
            customRules: [],
            warningMessages: {
                contentBlocked: "This content is restricted by your current settings.",
                topicRestricted: "This topic is currently restricted."
            }
        };

        universalAI.saveRestrictions(restrictions);
        
        // Close modal
        const modal = document.getElementById('restrictionsModal');
        if (modal) {
            modal.classList.add('hidden');
        }

        console.log('✅ Restrictions saved:', restrictions);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing Universal AI Assistant...');
    
    try {
        universalAI = new UniversalAI();
        fileManager = new FileManager();
        uiManager = new UIManager();
        
        console.log('✅ Universal AI Assistant initialized successfully!');
        
        // Test send function
        setTimeout(() => {
            const sendBtn = document.getElementById('sendMessage');
            const chatInput = document.getElementById('chatInput');
            console.log('🔍 Testing elements after init:');
            console.log('Send button exists:', !!sendBtn);
            console.log('Chat input exists:', !!chatInput);
            
            if (sendBtn && chatInput) {
                console.log('✅ Send function elements are ready!');
            } else {
                console.error('❌ Send function elements missing!');
            }
        }, 1000);
        
    } catch (error) {
        console.error('❌ Error initializing application:', error);
    }
});