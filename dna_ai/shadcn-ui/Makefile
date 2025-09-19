# Makefile for AI Engine C++ Implementation
# Supports multiple compilers and build configurations

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
INCLUDES = -I./include
LIBS = -lpthread

# Optional library flags (uncomment if available)
# TENSORFLOW_FLAGS = -ltensorflow_cc -ltensorflow_framework
# ONNX_FLAGS = -lonnxruntime
# JSON_FLAGS = -DHAS_JSON

# Source and target
SOURCE = ai_engine.cpp
TARGET = ai_engine
DEBUG_TARGET = ai_engine_debug

# Build directories
BUILD_DIR = build
OBJ_DIR = $(BUILD_DIR)/obj

# Default target
all: $(TARGET)

# Release build
$(TARGET): $(SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(BUILD_DIR)/$(TARGET) $(SOURCE) $(LIBS)
	@echo "Built release version: $(BUILD_DIR)/$(TARGET)"

# Debug build
debug: CXXFLAGS += -g -DDEBUG -O0
debug: $(DEBUG_TARGET)

$(DEBUG_TARGET): $(SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(BUILD_DIR)/$(DEBUG_TARGET) $(SOURCE) $(LIBS)
	@echo "Built debug version: $(BUILD_DIR)/$(DEBUG_TARGET)"

# Build with TensorFlow support (requires TensorFlow C++ installation)
tensorflow: CXXFLAGS += -DHAS_TENSORFLOW
tensorflow: LIBS += $(TENSORFLOW_FLAGS)
tensorflow: $(TARGET)

# Build with ONNX support (requires ONNX Runtime)
onnx: CXXFLAGS += -DHAS_ONNX
onnx: LIBS += $(ONNX_FLAGS)
onnx: $(TARGET)

# Build with JSON support (requires nlohmann/json)
json: CXXFLAGS += -DHAS_JSON
json: $(TARGET)

# Full build with all optional dependencies
full: CXXFLAGS += -DHAS_TENSORFLOW -DHAS_ONNX -DHAS_JSON
full: LIBS += $(TENSORFLOW_FLAGS) $(ONNX_FLAGS)
full: $(TARGET)

# Run the program
run: $(TARGET)
	./$(BUILD_DIR)/$(TARGET)

# Run debug version
run-debug: debug
	./$(BUILD_DIR)/$(DEBUG_TARGET)

# Clean build files
clean:
	rm -rf $(BUILD_DIR)
	@echo "Cleaned build directory"

# Install dependencies (Ubuntu/Debian)
install-deps:
	sudo apt-get update
	sudo apt-get install -y build-essential cmake pkg-config
	sudo apt-get install -y libtensorflow-dev  # Optional
	sudo apt-get install -y nlohmann-json3-dev  # Optional

# Install dependencies (macOS with Homebrew)
install-deps-mac:
	brew install cmake pkg-config
	brew install tensorflow  # Optional
	brew install nlohmann-json  # Optional

# Format code
format:
	clang-format -i $(SOURCE)
	@echo "Formatted source code"

# Static analysis
analyze:
	cppcheck --enable=all --std=c++17 $(SOURCE)

# Performance profiling build
profile: CXXFLAGS += -pg -O2
profile: $(TARGET)

# Memory debugging build (requires valgrind)
memcheck: debug
	valgrind --leak-check=full --show-leak-kinds=all ./$(BUILD_DIR)/$(DEBUG_TARGET)

# Create documentation (requires doxygen)
docs:
	doxygen Doxyfile

# Test build (compile only, don't run)
test-compile: $(SOURCE)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -fsyntax-only $(SOURCE)
	@echo "Syntax check passed"

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build release version (default)"
	@echo "  debug        - Build debug version"
	@echo "  tensorflow   - Build with TensorFlow support"
	@echo "  onnx         - Build with ONNX Runtime support"
	@echo "  json         - Build with JSON support"
	@echo "  full         - Build with all optional dependencies"
	@echo "  run          - Build and run release version"
	@echo "  run-debug    - Build and run debug version"
	@echo "  clean        - Remove build files"
	@echo "  install-deps - Install dependencies (Ubuntu/Debian)"
	@echo "  install-deps-mac - Install dependencies (macOS)"
	@echo "  format       - Format source code"
	@echo "  analyze      - Run static analysis"
	@echo "  profile      - Build with profiling support"
	@echo "  memcheck     - Run with memory debugging"
	@echo "  docs         - Generate documentation"
	@echo "  test-compile - Test compilation without building"
	@echo "  help         - Show this help message"

.PHONY: all debug tensorflow onnx json full run run-debug clean install-deps install-deps-mac format analyze profile memcheck docs test-compile help