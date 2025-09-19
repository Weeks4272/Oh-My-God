#!/usr/bin/env python3
"""
Universal AI Engine - Multi-Language Code Generation
Supports 30+ programming languages with execution environments
"""

import os
import sys
import json
import subprocess
import tempfile
import traceback
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass
from enum import Enum
import shutil
import docker
from pathlib import Path

# Enhanced language support
class Language(Enum):
    # Systems Programming
    PYTHON = "python"
    CPP = "cpp"
    C = "c"
    RUST = "rust"
    GO = "go"
    ASSEMBLY = "assembly"
    
    # Web Development
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    PHP = "php"
    RUBY = "ruby"
    PERL = "perl"
    DART = "dart"
    
    # Enterprise & Mobile
    JAVA = "java"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    CSHARP = "csharp"
    SCALA = "scala"
    
    # Data & AI
    R = "r"
    JULIA = "julia"
    MATLAB = "matlab"
    OCTAVE = "octave"
    
    # Functional Programming
    HASKELL = "haskell"
    LISP = "lisp"
    CLOJURE = "clojure"
    FSHARP = "fsharp"
    ERLANG = "erlang"
    ELIXIR = "elixir"
    
    # Scripting & Automation
    BASH = "bash"
    POWERSHELL = "powershell"
    LUA = "lua"
    TCL = "tcl"
    
    # Emerging Languages
    ZIG = "zig"
    NIM = "nim"
    CRYSTAL = "crystal"
    
    # Database & Query
    SQL = "sql"
    GRAPHQL = "graphql"
    MONGODB = "mongodb"
    
    # Configuration & Markup
    YAML = "yaml"
    TOML = "toml"
    XML = "xml"
    JSON = "json"
    DOCKERFILE = "dockerfile"

@dataclass
class LanguageConfig:
    """Configuration for each programming language"""
    name: str
    extension: str
    compile_cmd: Optional[str] = None
    run_cmd: str = ""
    docker_image: Optional[str] = None
    interpreter: Optional[str] = None
    package_manager: Optional[str] = None
    hello_world: str = ""
    comment_style: str = "//"

class UniversalLanguageManager:
    """Manages all programming languages and their configurations"""
    
    def __init__(self):
        self.languages = self._initialize_languages()
        self.docker_client = None
        self.logger = logging.getLogger("UniversalLanguageManager")
        
        try:
            self.docker_client = docker.from_env()
            self.logger.info("Docker client initialized")
        except Exception as e:
            self.logger.warning(f"Docker not available: {e}")
    
    def _initialize_languages(self) -> Dict[Language, LanguageConfig]:
        """Initialize all supported languages with their configurations"""
        return {
            # Systems Programming
            Language.PYTHON: LanguageConfig(
                name="Python",
                extension=".py",
                run_cmd="python3 {file}",
                docker_image="python:3.11-slim",
                interpreter="python3",
                package_manager="pip",
                hello_world='print("Hello, World!")',
                comment_style="#"
            ),
            Language.CPP: LanguageConfig(
                name="C++",
                extension=".cpp",
                compile_cmd="g++ -o {output} {file} -std=c++17",
                run_cmd="./{output}",
                docker_image="gcc:latest",
                hello_world='#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}'
            ),
            Language.C: LanguageConfig(
                name="C",
                extension=".c",
                compile_cmd="gcc -o {output} {file}",
                run_cmd="./{output}",
                docker_image="gcc:latest",
                hello_world='#include <stdio.h>\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}'
            ),
            Language.RUST: LanguageConfig(
                name="Rust",
                extension=".rs",
                compile_cmd="rustc {file} -o {output}",
                run_cmd="./{output}",
                docker_image="rust:latest",
                package_manager="cargo",
                hello_world='fn main() {\n    println!("Hello, World!");\n}'
            ),
            Language.GO: LanguageConfig(
                name="Go",
                extension=".go",
                compile_cmd="go build -o {output} {file}",
                run_cmd="./{output}",
                docker_image="golang:latest",
                package_manager="go mod",
                hello_world='package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}'
            ),
            
            # Web Development
            Language.JAVASCRIPT: LanguageConfig(
                name="JavaScript",
                extension=".js",
                run_cmd="node {file}",
                docker_image="node:18-slim",
                interpreter="node",
                package_manager="npm",
                hello_world='console.log("Hello, World!");'
            ),
            Language.TYPESCRIPT: LanguageConfig(
                name="TypeScript",
                extension=".ts",
                compile_cmd="tsc {file}",
                run_cmd="node {output}.js",
                docker_image="node:18-slim",
                package_manager="npm",
                hello_world='console.log("Hello, World!");'
            ),
            Language.PHP: LanguageConfig(
                name="PHP",
                extension=".php",
                run_cmd="php {file}",
                docker_image="php:8.2-cli",
                interpreter="php",
                hello_world='<?php\necho "Hello, World!\\n";\n?>'
            ),
            Language.RUBY: LanguageConfig(
                name="Ruby",
                extension=".rb",
                run_cmd="ruby {file}",
                docker_image="ruby:3.2-slim",
                interpreter="ruby",
                package_manager="gem",
                hello_world='puts "Hello, World!"',
                comment_style="#"
            ),
            
            # Enterprise & Mobile
            Language.JAVA: LanguageConfig(
                name="Java",
                extension=".java",
                compile_cmd="javac {file}",
                run_cmd="java {class_name}",
                docker_image="openjdk:17-slim",
                package_manager="maven",
                hello_world='public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}'
            ),
            Language.KOTLIN: LanguageConfig(
                name="Kotlin",
                extension=".kt",
                compile_cmd="kotlinc {file} -include-runtime -d {output}.jar",
                run_cmd="java -jar {output}.jar",
                docker_image="openjdk:17-slim",
                hello_world='fun main() {\n    println("Hello, World!")\n}'
            ),
            Language.SWIFT: LanguageConfig(
                name="Swift",
                extension=".swift",
                compile_cmd="swiftc {file} -o {output}",
                run_cmd="./{output}",
                docker_image="swift:latest",
                hello_world='print("Hello, World!")'
            ),
            Language.CSHARP: LanguageConfig(
                name="C#",
                extension=".cs",
                compile_cmd="csc {file}",
                run_cmd="mono {output}.exe",
                docker_image="mono:latest",
                hello_world='using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}'
            ),
            
            # Data & AI
            Language.R: LanguageConfig(
                name="R",
                extension=".r",
                run_cmd="Rscript {file}",
                docker_image="r-base:latest",
                interpreter="Rscript",
                hello_world='cat("Hello, World!\\n")',
                comment_style="#"
            ),
            Language.JULIA: LanguageConfig(
                name="Julia",
                extension=".jl",
                run_cmd="julia {file}",
                docker_image="julia:latest",
                interpreter="julia",
                hello_world='println("Hello, World!")',
                comment_style="#"
            ),
            
            # Functional Programming
            Language.HASKELL: LanguageConfig(
                name="Haskell",
                extension=".hs",
                compile_cmd="ghc -o {output} {file}",
                run_cmd="./{output}",
                docker_image="haskell:latest",
                hello_world='main = putStrLn "Hello, World!"',
                comment_style="--"
            ),
            Language.CLOJURE: LanguageConfig(
                name="Clojure",
                extension=".clj",
                run_cmd="clojure {file}",
                docker_image="clojure:latest",
                hello_world='(println "Hello, World!")',
                comment_style=";"
            ),
            Language.ERLANG: LanguageConfig(
                name="Erlang",
                extension=".erl",
                compile_cmd="erlc {file}",
                run_cmd="erl -noshell -s {module} start -s init stop",
                docker_image="erlang:latest",
                hello_world='-module(hello).\n-export([start/0]).\n\nstart() ->\n    io:format("Hello, World!~n").'
            ),
            Language.ELIXIR: LanguageConfig(
                name="Elixir",
                extension=".ex",
                run_cmd="elixir {file}",
                docker_image="elixir:latest",
                hello_world='IO.puts "Hello, World!"',
                comment_style="#"
            ),
            
            # Scripting
            Language.BASH: LanguageConfig(
                name="Bash",
                extension=".sh",
                run_cmd="bash {file}",
                docker_image="bash:latest",
                interpreter="bash",
                hello_world='#!/bin/bash\necho "Hello, World!"',
                comment_style="#"
            ),
            Language.POWERSHELL: LanguageConfig(
                name="PowerShell",
                extension=".ps1",
                run_cmd="pwsh {file}",
                docker_image="mcr.microsoft.com/powershell:latest",
                hello_world='Write-Host "Hello, World!"',
                comment_style="#"
            ),
            Language.LUA: LanguageConfig(
                name="Lua",
                extension=".lua",
                run_cmd="lua {file}",
                docker_image="lua:latest",
                hello_world='print("Hello, World!")',
                comment_style="--"
            ),
            
            # Emerging Languages
            Language.ZIG: LanguageConfig(
                name="Zig",
                extension=".zig",
                compile_cmd="zig build-exe {file}",
                run_cmd="./{output}",
                hello_world='const std = @import("std");\n\npub fn main() void {\n    std.debug.print("Hello, World!\\n", .{});\n}'
            ),
            Language.NIM: LanguageConfig(
                name="Nim",
                extension=".nim",
                compile_cmd="nim compile {file}",
                run_cmd="./{output}",
                hello_world='echo "Hello, World!"',
                comment_style="#"
            ),
            Language.CRYSTAL: LanguageConfig(
                name="Crystal",
                extension=".cr",
                compile_cmd="crystal build {file}",
                run_cmd="./{output}",
                hello_world='puts "Hello, World!"',
                comment_style="#"
            ),
            
            # Database & Query
            Language.SQL: LanguageConfig(
                name="SQL",
                extension=".sql",
                run_cmd="sqlite3 < {file}",
                hello_world='SELECT "Hello, World!" AS greeting;',
                comment_style="--"
            ),
            
            # Configuration
            Language.YAML: LanguageConfig(
                name="YAML",
                extension=".yaml",
                hello_world='greeting: "Hello, World!"',
                comment_style="#"
            ),
            Language.JSON: LanguageConfig(
                name="JSON",
                extension=".json",
                hello_world='{\n  "greeting": "Hello, World!"\n}'
            ),
            Language.DOCKERFILE: LanguageConfig(
                name="Dockerfile",
                extension="",
                hello_world='FROM alpine:latest\nRUN echo "Hello, World!"',
                comment_style="#"
            ),
        }
    
    def get_language_config(self, language: Language) -> LanguageConfig:
        """Get configuration for a specific language"""
        return self.languages.get(language, LanguageConfig("Unknown", ".txt"))
    
    def is_language_supported(self, language: Language) -> bool:
        """Check if a language is supported"""
        return language in self.languages
    
    def list_supported_languages(self) -> List[str]:
        """Get list of all supported languages"""
        return [lang.value for lang in self.languages.keys()]

class UniversalCodeExecutor:
    """Execute code in any supported programming language"""
    
    def __init__(self, language_manager: UniversalLanguageManager):
        self.language_manager = language_manager
        self.logger = logging.getLogger("UniversalCodeExecutor")
        self.temp_dir = tempfile.mkdtemp()
    
    def execute_code(self, code: str, language: Language) -> Dict[str, Any]:
        """Execute code in the specified language"""
        try:
            config = self.language_manager.get_language_config(language)
            
            # Create temporary file
            filename = f"code{config.extension}"
            filepath = os.path.join(self.temp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Try Docker execution first, then local
            if self.language_manager.docker_client and config.docker_image:
                return self._execute_with_docker(filepath, config, language)
            else:
                return self._execute_locally(filepath, config, language)
                
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'execution_time': 0
            }
    
    def _execute_with_docker(self, filepath: str, config: LanguageConfig, language: Language) -> Dict[str, Any]:
        """Execute code using Docker container"""
        try:
            import time
            start_time = time.time()
            
            # Prepare volume mount
            container_file = f"/tmp/code{config.extension}"
            volumes = {filepath: {'bind': container_file, 'mode': 'ro'}}
            
            # Prepare command
            if config.compile_cmd:
                # Compiled language
                output_file = "/tmp/output"
                compile_cmd = config.compile_cmd.format(
                    file=container_file,
                    output=output_file
                )
                run_cmd = config.run_cmd.format(output=output_file)
                command = f"{compile_cmd} && {run_cmd}"
            else:
                # Interpreted language
                command = config.run_cmd.format(file=container_file)
            
            # Run container
            result = self.language_manager.docker_client.containers.run(
                config.docker_image,
                command=f"sh -c '{command}'",
                volumes=volumes,
                remove=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': result.decode('utf-8') if isinstance(result, bytes) else str(result),
                'error': '',
                'execution_time': execution_time,
                'method': 'docker'
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f"Docker execution failed: {str(e)}",
                'execution_time': 0
            }
    
    def _execute_locally(self, filepath: str, config: LanguageConfig, language: Language) -> Dict[str, Any]:
        """Execute code locally"""
        try:
            import time
            start_time = time.time()
            
            output_file = filepath.replace(config.extension, "")
            
            # Compile if needed
            if config.compile_cmd:
                compile_cmd = config.compile_cmd.format(
                    file=filepath,
                    output=output_file,
                    class_name=Path(filepath).stem
                )
                
                compile_result = subprocess.run(
                    compile_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'output': compile_result.stdout,
                        'error': f"Compilation failed: {compile_result.stderr}",
                        'execution_time': 0
                    }
            
            # Run the code
            if config.run_cmd:
                run_cmd = config.run_cmd.format(
                    file=filepath,
                    output=output_file,
                    class_name=Path(filepath).stem,
                    module=Path(filepath).stem
                )
                
                run_result = subprocess.run(
                    run_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(filepath)
                )
                
                execution_time = time.time() - start_time
                
                return {
                    'success': run_result.returncode == 0,
                    'output': run_result.stdout,
                    'error': run_result.stderr if run_result.returncode != 0 else '',
                    'execution_time': execution_time,
                    'method': 'local'
                }
            else:
                return {
                    'success': True,
                    'output': 'Code saved successfully (no execution)',
                    'error': '',
                    'execution_time': time.time() - start_time,
                    'method': 'local'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout (30 seconds)',
                'execution_time': 30
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f"Local execution failed: {str(e)}",
                'execution_time': 0
            }

class UniversalCodeGenerator:
    """Generate code templates and examples for any language"""
    
    def __init__(self, language_manager: UniversalLanguageManager):
        self.language_manager = language_manager
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[Language, Dict[str, str]]:
        """Initialize code templates for all languages"""
        return {
            Language.PYTHON: {
                "function": "def {name}({params}):\n    \"\"\"{description}\"\"\"\n    pass",
                "class": "class {name}:\n    \"\"\"{description}\"\"\"\n    \n    def __init__(self):\n        pass",
                "fibonacci": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "factorial": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                "sort": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)"
            },
            Language.JAVA: {
                "function": "public static {return_type} {name}({params}) {\n    // {description}\n    return null;\n}",
                "class": "public class {name} {\n    // {description}\n    \n    public {name}() {\n        // Constructor\n    }\n}",
                "fibonacci": "public static int fibonacci(int n) {\n    if (n <= 1) return n;\n    return fibonacci(n-1) + fibonacci(n-2);\n}",
                "factorial": "public static int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}"
            },
            Language.JAVASCRIPT: {
                "function": "function {name}({params}) {\n    // {description}\n    return null;\n}",
                "class": "class {name} {\n    // {description}\n    \n    constructor() {\n        // Constructor\n    }\n}",
                "fibonacci": "function fibonacci(n) {\n    if (n <= 1) return n;\n    return fibonacci(n-1) + fibonacci(n-2);\n}",
                "factorial": "function factorial(n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}"
            },
            Language.CPP: {
                "function": "{return_type} {name}({params}) {\n    // {description}\n    return {};\n}",
                "class": "class {name} {\npublic:\n    // {description}\n    \n    {name}() {\n        // Constructor\n    }\n};",
                "fibonacci": "int fibonacci(int n) {\n    if (n <= 1) return n;\n    return fibonacci(n-1) + fibonacci(n-2);\n}",
                "factorial": "int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}"
            },
            Language.RUST: {
                "function": "fn {name}({params}) -> {return_type} {\n    // {description}\n    todo!()\n}",
                "struct": "struct {name} {\n    // {description}\n}",
                "fibonacci": "fn fibonacci(n: u32) -> u32 {\n    match n {\n        0 | 1 => n,\n        _ => fibonacci(n-1) + fibonacci(n-2),\n    }\n}",
                "factorial": "fn factorial(n: u32) -> u32 {\n    match n {\n        0 | 1 => 1,\n        _ => n * factorial(n-1),\n    }\n}"
            },
            Language.GO: {
                "function": "func {name}({params}) {return_type} {\n    // {description}\n    return nil\n}",
                "struct": "type {name} struct {\n    // {description}\n}",
                "fibonacci": "func fibonacci(n int) int {\n    if n <= 1 {\n        return n\n    }\n    return fibonacci(n-1) + fibonacci(n-2)\n}",
                "factorial": "func factorial(n int) int {\n    if n <= 1 {\n        return 1\n    }\n    return n * factorial(n-1)\n}"
            }
        }
    
    def generate_template(self, language: Language, template_type: str, **kwargs) -> str:
        """Generate code template for specified language and type"""
        lang_templates = self.templates.get(language, {})
        template = lang_templates.get(template_type, "// Template not available")
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def get_hello_world(self, language: Language) -> str:
        """Get hello world program for any language"""
        config = self.language_manager.get_language_config(language)
        return config.hello_world

class UniversalAIEngine:
    """Main universal AI engine supporting all programming languages"""
    
    def __init__(self):
        self.language_manager = UniversalLanguageManager()
        self.code_executor = UniversalCodeExecutor(self.language_manager)
        self.code_generator = UniversalCodeGenerator(self.language_manager)
        self.logger = logging.getLogger("UniversalAIEngine")
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process universal coding requests"""
        try:
            request_type = request.get('type', 'generate')
            language_str = request.get('language', 'python')
            
            # Parse language
            try:
                language = Language(language_str.lower())
            except ValueError:
                return {
                    'error': f'Unsupported language: {language_str}',
                    'supported_languages': self.language_manager.list_supported_languages()
                }
            
            if request_type == 'generate':
                return self._handle_generate(request, language)
            elif request_type == 'execute':
                return self._handle_execute(request, language)
            elif request_type == 'template':
                return self._handle_template(request, language)
            elif request_type == 'languages':
                return self._handle_languages()
            else:
                return {'error': f'Unknown request type: {request_type}'}
                
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {'error': str(e)}
    
    def _handle_generate(self, request: Dict[str, Any], language: Language) -> Dict[str, Any]:
        """Handle code generation for any language"""
        prompt = request.get('prompt', '')
        
        # Generate appropriate code based on prompt
        if 'hello world' in prompt.lower():
            code = self.code_generator.get_hello_world(language)
        elif 'fibonacci' in prompt.lower():
            code = self.code_generator.generate_template(language, 'fibonacci')
        elif 'factorial' in prompt.lower():
            code = self.code_generator.generate_template(language, 'factorial')
        elif 'function' in prompt.lower():
            code = self.code_generator.generate_template(
                language, 'function',
                name='myFunction',
                params='',
                description='Generated function',
                return_type='void'
            )
        elif 'class' in prompt.lower():
            code = self.code_generator.generate_template(
                language, 'class',
                name='MyClass',
                description='Generated class'
            )
        else:
            # Generic template
            config = self.language_manager.get_language_config(language)
            code = f"{config.comment_style} TODO: Implement {prompt}\n{config.hello_world}"
        
        return {
            'code': code,
            'language': language.value,
            'explanation': f'Generated {language.value} code for: {prompt}',
            'confidence': 0.8
        }
    
    def _handle_execute(self, request: Dict[str, Any], language: Language) -> Dict[str, Any]:
        """Handle code execution for any language"""
        code = request.get('code', '')
        
        if not code:
            return {'error': 'No code provided for execution'}
        
        result = self.code_executor.execute_code(code, language)
        
        return {
            'language': language.value,
            'execution_result': result
        }
    
    def _handle_template(self, request: Dict[str, Any], language: Language) -> Dict[str, Any]:
        """Handle template generation"""
        template_type = request.get('template_type', 'function')
        
        code = self.code_generator.generate_template(
            language,
            template_type,
            **request.get('params', {})
        )
        
        return {
            'code': code,
            'language': language.value,
            'template_type': template_type
        }
    
    def _handle_languages(self) -> Dict[str, Any]:
        """Handle language listing"""
        return {
            'supported_languages': self.language_manager.list_supported_languages(),
            'total_count': len(self.language_manager.languages)
        }

def main():
    """Test the universal AI engine"""
    print("Universal AI Engine - Supporting 30+ Programming Languages")
    print("=" * 60)
    
    engine = UniversalAIEngine()
    
    # Test different languages
    test_languages = [
        Language.PYTHON, Language.JAVA, Language.JAVASCRIPT,
        Language.CPP, Language.RUST, Language.GO, Language.RUBY
    ]
    
    for lang in test_languages:
        print(f"\n--- Testing {lang.value.upper()} ---")
        
        # Generate hello world
        request = {
            'type': 'generate',
            'language': lang.value,
            'prompt': 'hello world'
        }
        
        result = engine.process_request(request)
        print(f"Generated code:\n{result.get('code', 'Error')}")
        
        # Execute if possible
        if result.get('code'):
            exec_request = {
                'type': 'execute',
                'language': lang.value,
                'code': result['code']
            }
            
            exec_result = engine.process_request(exec_request)
            execution = exec_result.get('execution_result', {})
            
            if execution.get('success'):
                print(f"Output: {execution.get('output', 'No output')}")
            else:
                print(f"Execution failed: {execution.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()