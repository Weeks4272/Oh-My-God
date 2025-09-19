#!/usr/bin/env python3
"""
Real AI Engine - Python Implementation with Haystack, SymPy, and RAGatouille
Provides code generation, analysis, and execution capabilities using actual ML models
"""

import os
import sys
import json
import subprocess
import tempfile
import traceback
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

# ML and AI libraries
try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers/torch not installed. Install with: pip install torch transformers")

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Advanced AI frameworks
try:
    from haystack import Document, Pipeline
    from haystack.components.generators import OpenAIGenerator
    from haystack.components.builders import PromptBuilder
    from haystack.components.retrievers import InMemoryBM25Retriever
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    HAS_HAYSTACK = True
except ImportError:
    HAS_HAYSTACK = False
    print("Warning: haystack-ai not installed. Install with: pip install haystack-ai")

try:
    import sympy as sp
    from sympy import symbols, solve, diff, integrate, simplify, expand, factor
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("Warning: sympy not installed. Install with: pip install sympy")

try:
    from ragatouille import RAGPretrainedModel
    HAS_RAGATOUILLE = True
except ImportError:
    HAS_RAGATOUILLE = False
    print("Warning: RAGatouille not installed. Install with: pip install RAGatouille")

# Code execution and analysis
import ast
import re
from io import StringIO
import contextlib

class Language(Enum):
    PYTHON = "python"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    HTML = "html"
    CSS = "css"

@dataclass
class CodeRequest:
    prompt: str
    language: Language
    context: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7

@dataclass
class CodeResponse:
    code: str
    explanation: str
    confidence: float
    execution_result: Optional[str] = None
    error: Optional[str] = None
    math_result: Optional[str] = None
    rag_context: Optional[str] = None

class MathEngine:
    """Mathematical computation engine using SymPy"""
    
    def __init__(self):
        self.has_sympy = HAS_SYMPY
        self.logger = logging.getLogger("MathEngine")
    
    def solve_equation(self, equation_str: str) -> str:
        """Solve mathematical equations using SymPy"""
        if not self.has_sympy:
            return "SymPy not available. Install with: pip install sympy"
        
        try:
            # Define common symbols
            x, y, z, t = sp.symbols('x y z t')
            
            # Parse and solve equation
            if '=' in equation_str:
                left, right = equation_str.split('=')
                eq = sp.Eq(sp.sympify(left), sp.sympify(right))
                solution = sp.solve(eq, x)
            else:
                # Assume it's an expression to simplify
                expr = sp.sympify(equation_str)
                solution = sp.simplify(expr)
            
            return f"Solution: {solution}"
            
        except Exception as e:
            return f"Math error: {str(e)}"
    
    def calculate_derivative(self, expression: str, variable: str = 'x') -> str:
        """Calculate derivative of an expression"""
        if not self.has_sympy:
            return "SymPy not available"
        
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)
            derivative = sp.diff(expr, var)
            return f"d/d{variable}({expression}) = {derivative}"
        except Exception as e:
            return f"Derivative error: {str(e)}"
    
    def calculate_integral(self, expression: str, variable: str = 'x') -> str:
        """Calculate integral of an expression"""
        if not self.has_sympy:
            return "SymPy not available"
        
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)
            integral = sp.integrate(expr, var)
            return f"∫({expression}) d{variable} = {integral}"
        except Exception as e:
            return f"Integral error: {str(e)}"

class RAGEngine:
    """Retrieval-Augmented Generation engine using RAGatouille"""
    
    def __init__(self):
        self.has_ragatouille = HAS_RAGATOUILLE
        self.model = None
        self.document_store = []
        self.logger = logging.getLogger("RAGEngine")
        
        if self.has_ragatouille:
            try:
                self.model = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
                self.logger.info("RAGatouille model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load RAGatouille model: {e}")
                self.has_ragatouille = False
    
    def add_documents(self, documents: List[str]):
        """Add documents to the knowledge base"""
        if not self.has_ragatouille or not self.model:
            return "RAGatouille not available"
        
        try:
            self.document_store.extend(documents)
            # Index documents for retrieval
            self.model.index(
                collection=documents,
                index_name="code_knowledge_base",
                max_document_length=512
            )
            return f"Added {len(documents)} documents to knowledge base"
        except Exception as e:
            return f"RAG indexing error: {str(e)}"
    
    def retrieve_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context for a query"""
        if not self.has_ragatouille or not self.model:
            return "RAGatouille not available"
        
        try:
            if not self.document_store:
                # Add some default programming knowledge
                default_docs = [
                    "Python is a high-level programming language with dynamic semantics.",
                    "Functions in Python are defined using the 'def' keyword.",
                    "Lists in Python are ordered collections that can contain different data types.",
                    "Dictionary comprehensions provide a concise way to create dictionaries.",
                    "Exception handling in Python uses try-except blocks.",
                    "Object-oriented programming in Python uses classes and objects.",
                ]
                self.add_documents(default_docs)
            
            results = self.model.search(query, k=k)
            context = "\n".join([result["content"] for result in results])
            return context
            
        except Exception as e:
            return f"RAG retrieval error: {str(e)}"

class HaystackEngine:
    """Advanced NLP pipeline using Haystack"""
    
    def __init__(self):
        self.has_haystack = HAS_HAYSTACK
        self.document_store = None
        self.pipeline = None
        self.logger = logging.getLogger("HaystackEngine")
        
        if self.has_haystack:
            self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize Haystack pipeline"""
        try:
            # Create document store
            self.document_store = InMemoryDocumentStore()
            
            # Add some programming documentation
            docs = [
                Document(content="Python functions are defined with 'def' keyword and can return values."),
                Document(content="List comprehensions provide a concise way to create lists in Python."),
                Document(content="Exception handling uses try-except blocks to catch and handle errors."),
                Document(content="Classes in Python define objects with attributes and methods."),
                Document(content="Modules in Python allow code organization and reusability."),
            ]
            self.document_store.write_documents(docs)
            
            # Create retrieval pipeline
            retriever = InMemoryBM25Retriever(document_store=self.document_store)
            prompt_builder = PromptBuilder(
                template="""
                Given the following context, answer the question about programming:
                Context: {{context}}
                Question: {{question}}
                Answer:
                """
            )
            
            self.pipeline = Pipeline()
            self.pipeline.add_component("retriever", retriever)
            self.pipeline.add_component("prompt_builder", prompt_builder)
            
            self.pipeline.connect("retriever", "prompt_builder.context")
            
            self.logger.info("Haystack pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Haystack pipeline: {e}")
            self.has_haystack = False
    
    def search_knowledge(self, query: str) -> str:
        """Search programming knowledge using Haystack"""
        if not self.has_haystack or not self.pipeline:
            return "Haystack not available"
        
        try:
            result = self.pipeline.run({
                "retriever": {"query": query},
                "prompt_builder": {"question": query}
            })
            
            # Extract context from retrieved documents
            context = ""
            if "retriever" in result and "documents" in result["retriever"]:
                docs = result["retriever"]["documents"]
                context = "\n".join([doc.content for doc in docs[:3]])
            
            return context or "No relevant context found"
            
        except Exception as e:
            return f"Haystack search error: {str(e)}"

class LocalAIEngine:
    """Enhanced Local AI engine with Haystack, SymPy, and RAGatouille integration"""
    
    def __init__(self, model_name: str = "microsoft/CodeGPT-small-py"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger = self._setup_logger()
        
        # Initialize enhanced engines
        self.math_engine = MathEngine()
        self.rag_engine = RAGEngine()
        self.haystack_engine = HaystackEngine()
        
        if HAS_TRANSFORMERS:
            self._load_model()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("AIEngine")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_model(self):
        """Load the AI model for code generation"""
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            # Fallback to a smaller model
            try:
                self.model_name = "gpt2"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.logger.info("Fallback model loaded")
            except Exception as e2:
                self.logger.error(f"Failed to load fallback model: {e2}")
    
    def generate_code(self, request: CodeRequest) -> CodeResponse:
        """Generate code with enhanced AI capabilities"""
        try:
            # Check if it's a math-related request
            math_keywords = ['solve', 'equation', 'derivative', 'integral', 'calculate', 'math']
            if any(keyword in request.prompt.lower() for keyword in math_keywords):
                math_result = self._handle_math_request(request.prompt)
            else:
                math_result = None
            
            # Get RAG context for better code generation
            rag_context = self.rag_engine.retrieve_context(request.prompt)
            haystack_context = self.haystack_engine.search_knowledge(request.prompt)
            
            # Combine contexts
            combined_context = f"{rag_context}\n{haystack_context}" if rag_context != "RAGatouille not available" else haystack_context
            
            if not HAS_TRANSFORMERS or self.model is None:
                response = self._fallback_generation(request)
            else:
                # Enhanced prompt with context
                formatted_prompt = self._format_enhanced_prompt(request, combined_context)
                
                # Tokenize and generate
                inputs = self.tokenizer.encode(formatted_prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + request.max_tokens,
                        temperature=request.temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode generated text
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                generated_code = generated_text[len(formatted_prompt):].strip()
                
                # Clean up the generated code
                cleaned_code = self._clean_generated_code(generated_code, request.language)
                
                response = CodeResponse(
                    code=cleaned_code,
                    explanation=f"Generated {request.language.value} code using {self.model_name} with RAG enhancement",
                    confidence=0.85,
                    math_result=math_result,
                    rag_context=combined_context if combined_context.strip() else None
                )
            
            # Execute if it's Python code
            if request.language == Language.PYTHON:
                response.execution_result = self._execute_python_code(response.code)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return CodeResponse(
                code="# Error generating code",
                explanation="Code generation failed",
                confidence=0.0,
                error=str(e)
            )
    
    def _handle_math_request(self, prompt: str) -> str:
        """Handle mathematical computation requests"""
        prompt_lower = prompt.lower()
        
        if 'derivative' in prompt_lower:
            # Extract expression (simple pattern matching)
            import re
            expr_match = re.search(r'of\s+([^,\s]+)', prompt)
            if expr_match:
                expression = expr_match.group(1)
                return self.math_engine.calculate_derivative(expression)
        
        elif 'integral' in prompt_lower:
            expr_match = re.search(r'of\s+([^,\s]+)', prompt)
            if expr_match:
                expression = expr_match.group(1)
                return self.math_engine.calculate_integral(expression)
        
        elif 'solve' in prompt_lower:
            # Extract equation
            eq_match = re.search(r'solve\s+([^,\n]+)', prompt)
            if eq_match:
                equation = eq_match.group(1)
                return self.math_engine.solve_equation(equation)
        
        return "Math computation completed"
    
    def _format_enhanced_prompt(self, request: CodeRequest, context: str) -> str:
        """Format prompt with enhanced context"""
        base_prompt = self._format_prompt(request)
        
        if context and context.strip() and context != "Haystack not available":
            enhanced_prompt = f"# Context: {context}\n\n{base_prompt}"
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt
    
    def _format_prompt(self, request: CodeRequest) -> str:
        """Format the prompt based on language and context"""
        if request.language == Language.PYTHON:
            prompt = f"# Python code to {request.prompt}\n"
            if request.context:
                prompt += f"# Context: {request.context}\n"
            prompt += "def solve():\n    "
        elif request.language == Language.CPP:
            prompt = f"// C++ code to {request.prompt}\n"
            if request.context:
                prompt += f"// Context: {request.context}\n"
            prompt += "#include <iostream>\nusing namespace std;\n\nint main() {\n    "
        elif request.language == Language.JAVASCRIPT:
            prompt = f"// JavaScript code to {request.prompt}\n"
            if request.context:
                prompt += f"// Context: {request.context}\n"
            prompt += "function solve() {\n    "
        else:
            prompt = f"{request.prompt}\n"
        
        return prompt
    
    def _clean_generated_code(self, code: str, language: Language) -> str:
        """Clean and format generated code"""
        # Remove common artifacts
        code = code.strip()
        
        # Remove incomplete lines at the end
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip() and not line.strip().endswith('...'):
                cleaned_lines.append(line)
            elif not line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _execute_python_code(self, code: str) -> Optional[str]:
        """Safely execute Python code and return output"""
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Create a safe execution environment with SymPy support
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                }
            }
            
            # Add SymPy if available
            if HAS_SYMPY:
                safe_globals.update({
                    'sympy': sp,
                    'symbols': sp.symbols,
                    'solve': sp.solve,
                    'diff': sp.diff,
                    'integrate': sp.integrate,
                    'simplify': sp.simplify,
                })
            
            # Execute the code
            exec(code, safe_globals)
            
            # Restore stdout and get output
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            return output if output.strip() else "Code executed successfully (no output)"
            
        except Exception as e:
            sys.stdout = old_stdout
            return f"Execution error: {str(e)}"
    
    def _fallback_generation(self, request: CodeRequest) -> CodeResponse:
        """Enhanced fallback code generation with math support"""
        templates = {
            Language.PYTHON: {
                "hello world": "print('Hello, World!')",
                "fibonacci": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))""",
                "sort list": """def sort_list(arr):
    return sorted(arr)

numbers = [64, 34, 25, 12, 22, 11, 90]
print(sort_list(numbers))""",
                "math": """import sympy as sp
x = sp.Symbol('x')
expr = x**2 + 2*x + 1
simplified = sp.simplify(expr)
print(f"Simplified: {simplified}")""",
            },
            Language.CPP: {
                "hello world": """#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}""",
                "fibonacci": """#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    cout << fibonacci(10) << endl;
    return 0;
}""",
            }
        }
        
        # Find matching template
        prompt_lower = request.prompt.lower()
        lang_templates = templates.get(request.language, {})
        
        for key, template in lang_templates.items():
            if key in prompt_lower:
                execution_result = None
                if request.language == Language.PYTHON:
                    execution_result = self._execute_python_code(template)
                
                return CodeResponse(
                    code=template,
                    explanation=f"Enhanced template-based {request.language.value} code",
                    confidence=0.7,
                    execution_result=execution_result
                )
        
        # Generic template
        if request.language == Language.PYTHON:
            code = f"# TODO: Implement {request.prompt}\npass"
        elif request.language == Language.CPP:
            code = f"// TODO: Implement {request.prompt}\n#include <iostream>\nusing namespace std;\n\nint main() {{\n    // Your code here\n    return 0;\n}}"
        else:
            code = f"// TODO: Implement {request.prompt}"
        
        return CodeResponse(
            code=code,
            explanation="Enhanced template-based code generation",
            confidence=0.4
        )

class CodeAnalyzer:
    """Enhanced code analyzer with mathematical analysis"""
    
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure and complexity"""
        try:
            tree = ast.parse(code)
            analysis = {
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'lines': len(code.split('\n')),
                'errors': [],
                'math_operations': [],
                'has_sympy': False
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                        if 'sympy' in alias.name:
                            analysis['has_sympy'] = True
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}"
                        analysis['imports'].append(full_name)
                        if 'sympy' in module:
                            analysis['has_sympy'] = True
                elif isinstance(node, ast.BinOp):
                    # Detect mathematical operations
                    if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                        analysis['math_operations'].append(type(node.op).__name__)
            
            # Enhanced complexity calculation
            analysis['complexity'] = (len(analysis['functions']) + 
                                    len(analysis['classes']) + 
                                    len(analysis['math_operations']))
            
            return analysis
            
        except SyntaxError as e:
            return {
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'lines': len(code.split('\n')),
                'errors': [f"Syntax error: {str(e)}"],
                'math_operations': [],
                'has_sympy': False
            }

class AIEngineServer:
    """Enhanced main server class for the AI engine"""
    
    def __init__(self):
        self.ai_engine = LocalAIEngine()
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger("AIEngineServer")
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming requests with enhanced capabilities"""
        try:
            request_type = request_data.get('type', 'generate')
            
            if request_type == 'generate':
                return self._handle_generate_request(request_data)
            elif request_type == 'analyze':
                return self._handle_analyze_request(request_data)
            elif request_type == 'execute':
                return self._handle_execute_request(request_data)
            elif request_type == 'math':
                return self._handle_math_request(request_data)
            elif request_type == 'search':
                return self._handle_search_request(request_data)
            else:
                return {'error': f'Unknown request type: {request_type}'}
                
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {'error': str(e)}
    
    def _handle_generate_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle enhanced code generation requests"""
        request = CodeRequest(
            prompt=data.get('prompt', ''),
            language=Language(data.get('language', 'python')),
            context=data.get('context'),
            max_tokens=data.get('max_tokens', 1000),
            temperature=data.get('temperature', 0.7)
        )
        
        response = self.ai_engine.generate_code(request)
        
        return {
            'code': response.code,
            'explanation': response.explanation,
            'confidence': response.confidence,
            'execution_result': response.execution_result,
            'math_result': response.math_result,
            'rag_context': response.rag_context,
            'error': response.error
        }
    
    def _handle_analyze_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle enhanced code analysis requests"""
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if language == 'python':
            analysis = self.code_analyzer.analyze_python_code(code)
            return {'analysis': analysis}
        else:
            return {'error': f'Analysis not supported for {language}'}
    
    def _handle_execute_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code execution requests"""
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if language == 'python':
            result = self.ai_engine._execute_python_code(code)
            return {'result': result}
        else:
            return {'error': f'Execution not supported for {language}'}
    
    def _handle_math_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mathematical computation requests"""
        expression = data.get('expression', '')
        operation = data.get('operation', 'solve')
        
        if operation == 'solve':
            result = self.ai_engine.math_engine.solve_equation(expression)
        elif operation == 'derivative':
            variable = data.get('variable', 'x')
            result = self.ai_engine.math_engine.calculate_derivative(expression, variable)
        elif operation == 'integral':
            variable = data.get('variable', 'x')
            result = self.ai_engine.math_engine.calculate_integral(expression, variable)
        else:
            result = "Unknown math operation"
        
        return {'result': result}
    
    def _handle_search_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge search requests"""
        query = data.get('query', '')
        
        haystack_result = self.ai_engine.haystack_engine.search_knowledge(query)
        rag_result = self.ai_engine.rag_engine.retrieve_context(query)
        
        return {
            'haystack_context': haystack_result,
            'rag_context': rag_result
        }

def main():
    """Enhanced main entry point"""
    print("AI Engine - Enhanced Python Implementation")
    print("=========================================")
    print("Features: Haystack, SymPy, RAGatouille")
    print("=========================================")
    
    engine = AIEngineServer()
    
    # Example usage with enhanced features
    test_requests = [
        {
            'type': 'generate',
            'prompt': 'create a function to solve quadratic equations using sympy',
            'language': 'python',
            'max_tokens': 300
        },
        {
            'type': 'math',
            'expression': 'x**2 - 4*x + 4',
            'operation': 'solve'
        },
        {
            'type': 'search',
            'query': 'python function definition'
        }
    ]
    
    for i, test_request in enumerate(test_requests, 1):
        print(f"\n--- Test {i}: {test_request['type']} ---")
        result = engine.process_request(test_request)
        
        if test_request['type'] == 'generate':
            print("Generated code:")
            print(result.get('code', 'No code generated'))
            if result.get('execution_result'):
                print("\nExecution result:")
                print(result['execution_result'])
            if result.get('math_result'):
                print("\nMath result:")
                print(result['math_result'])
        elif test_request['type'] == 'math':
            print("Math result:")
            print(result.get('result', 'No result'))
        elif test_request['type'] == 'search':
            print("Search results:")
            print("Haystack:", result.get('haystack_context', 'No context'))
            print("RAG:", result.get('rag_context', 'No context'))

if __name__ == "__main__":
    main()