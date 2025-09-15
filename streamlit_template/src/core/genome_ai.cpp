#include "genome_ai.hpp"
#include "utils/profiler.hpp"

#include <iostream>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <thread>

namespace genomeai {

GenomeAI::GenomeAI(const Config& config) : config_(config) {
    // Initialize performance stats
    performance_stats_ = {};
}

GenomeAI::~GenomeAI() {
    if (initialized_) {
        shutdown();
    }
}

bool GenomeAI::initialize() {
    if (initialized_) {
        return true;
    }
    
    try {
        // Setup directories
        if (!setup_directories()) {
            return false;
        }
        
        // Initialize memory pool
        memory_pool_ = std::make_unique<MemoryPool>(config_.memory_pool_size);
        
        // Initialize thread pool
        thread_pool_ = std::make_unique<ThreadPool>(config_.max_threads);
        
        // Initialize core components
        if (!initialize_components()) {
            return false;
        }
        
        initialized_ = true;
        
        std::cout << "GenomeAI initialized successfully" << std::endl;
        std::cout << "  Threads: " << config_.max_threads << std::endl;
        std::cout << "  Memory pool: " << (config_.memory_pool_size / (1024 * 1024)) << " MB" << std::endl;
        std::cout << "  GPU enabled: " << (config_.enable_gpu ? "Yes" : "No") << std::endl;
        std::cout << "  Web scraping: " << (config_.enable_web_scraping ? "Yes" : "No") << std::endl;
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Initialization failed: " + std::string(e.what()));
        return false;
    }
}

void GenomeAI::shutdown() {
    if (!initialized_) {
        return;
    }
    
    shutdown_requested_ = true;
    
    // Cleanup components in reverse order
    cleanup_components();
    
    thread_pool_.reset();
    memory_pool_.reset();
    
    initialized_ = false;
    
    std::cout << "GenomeAI shutdown complete" << std::endl;
}

AnalysisResult GenomeAI::analyze_sequence(const std::string& sequence, SequenceType type) {
    if (!initialized_) {
        throw std::runtime_error("GenomeAI not initialized");
    }
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Update performance stats
    performance_stats_.sequences_processed++;
    
    // Delegate to sequence analyzer
    auto result = sequence_analyzer_->analyze(sequence, type);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    result.processing_time = std::chrono::duration_cast<std::chrono::milliseconds>(
        end_time - start_time);
    
    return result;
}

bool GenomeAI::write_result(const AnalysisResult& result, const std::string& id) {
    namespace fs = std::filesystem;
    try {
        fs::path out = fs::path(config_.output_directory) / (id + ".json");
        std::ofstream ofs(out);
        if (!ofs.is_open()) {
            throw std::runtime_error("Cannot open output file");
        }
        ofs << "{\n"
            << "  \"length\": " << result.length << ",\n"
            << "  \"gc_content\": " << result.gc_content << "\n";
        ofs << "}";
        return true;
    } catch (const std::exception& e) {
        handle_error("Failed to write result: " + std::string(e.what()));
        return false;
    }
}

std::future<AnalysisResult> GenomeAI::analyze_sequence_async(const std::string& sequence, 
                                                           SequenceType type) {
    if (!initialized_) {
        throw std::runtime_error("GenomeAI not initialized");
    }
    
    return thread_pool_->enqueue([this, sequence, type]() {
        return analyze_sequence(sequence, type);
    });
}

BatchResult GenomeAI::analyze_batch(const std::vector<std::string>& sequences, 
                                   SequenceType type) {
    if (!initialized_) {
        throw std::runtime_error("GenomeAI not initialized");
    }
    
    BatchResult batch_result;
    batch_result.results.reserve(sequences.size());
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Process sequences in parallel
    std::vector<std::future<AnalysisResult>> futures;
    futures.reserve(sequences.size());
    
    for (const auto& sequence : sequences) {
        futures.emplace_back(analyze_sequence_async(sequence, type));
    }
    
    // Collect results
    for (auto& future : futures) {
        try {
            batch_result.results.emplace_back(future.get());
            batch_result.successful_analyses++;
        } catch (const std::exception& e) {
            batch_result.failed_analyses++;
            batch_result.errors.emplace_back(e.what());
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    batch_result.total_processing_time = std::chrono::duration_cast<std::chrono::milliseconds>(
        end_time - start_time);
    
    return batch_result;
}

bool GenomeAI::process_fasta_file(const std::string& filepath) {
    if (!initialized_) {
        return false;
    }
    
    try {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            handle_error("Cannot open file: " + filepath);
            return false;
        }
        
        std::string line;
        std::string current_sequence;
        std::string current_header;
        
        while (std::getline(file, line)) {
            if (line.empty()) continue;
            
            if (line[0] == '>') {
                // Process previous sequence if exists
                if (!current_sequence.empty()) {
                    auto result = analyze_sequence(current_sequence, SequenceType::DNA);
                    write_result(result, current_header);
                }
                
                current_header = line.substr(1);
                current_sequence.clear();
            } else {
                current_sequence += line;
            }
        }
        
        // Process last sequence
        if (!current_sequence.empty()) {
            auto result = analyze_sequence(current_sequence, SequenceType::DNA);
            write_result(result, current_header);
        }
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Error processing FASTA file: " + std::string(e.what()));
        return false;
    }
}

bool GenomeAI::process_fastq_file(const std::string& filepath) {
    if (!initialized_) {
        return false;
    }
    
    try {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            handle_error("Cannot open file: " + filepath);
            return false;
        }
        
        std::string line;
        int line_count = 0;
        std::string sequence;
        
        while (std::getline(file, line)) {
            line_count++;

            if (line_count % 4 == 2) { // Sequence line
                sequence = line;
                auto result = analyze_sequence(sequence, SequenceType::DNA);
                write_result(result, "read_" + std::to_string(line_count/4));
            }
        }
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Error processing FASTQ file: " + std::string(e.what()));
        return false;
    }
}

bool GenomeAI::process_vcf_file(const std::string& filepath) {
    if (!initialized_) {
        return false;
    }
    
    try {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            handle_error("Cannot open file: " + filepath);
            return false;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') continue;

            // Parse VCF line and extract variant information
            std::istringstream iss(line);
            std::string chrom, pos, id, ref;
            if (!(iss >> chrom >> pos >> id >> ref)) {
                continue;
            }
            auto result = analyze_sequence(ref, SequenceType::DNA);
            write_result(result, id.empty() ? chrom + ":" + pos : id);
        }
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Error processing VCF file: " + std::string(e.what()));
        return false;
    }
}

ResearchResults GenomeAI::search_literature(const std::string& query, size_t max_results) {
    if (!initialized_ || !config_.enable_web_scraping) {
        throw std::runtime_error("Research engine not available");
    }
    
    return research_engine_->search_literature(query, max_results);
}

std::future<ResearchResults> GenomeAI::search_literature_async(const std::string& query, 
                                                              size_t max_results) {
    if (!initialized_ || !config_.enable_web_scraping) {
        throw std::runtime_error("Research engine not available");
    }
    
    return thread_pool_->enqueue([this, query, max_results]() {
        return search_literature(query, max_results);
    });
}

bool GenomeAI::download_reference_genome(const std::string& species, 
                                        const std::string& assembly) {
    if (!initialized_ || !config_.enable_web_scraping) {
        return false;
    }
    
    return research_engine_->download_reference_genome(species, assembly, 
                                                      config_.cache_directory);
}

PerformanceStats GenomeAI::get_performance_stats() const {
    return performance_stats_;
}

void GenomeAI::reset_performance_stats() {
    performance_stats_ = {};
}

size_t GenomeAI::get_memory_usage() const {
    if (memory_pool_) {
        return memory_pool_->get_used_memory();
    }
    return 0;
}

void GenomeAI::optimize_memory() {
    if (memory_pool_) {
        memory_pool_->optimize();
    }
    
    // Clear caches if memory usage is high
    if (get_memory_usage() > config_.memory_pool_size * 0.8) {
        clear_cache();
    }
}

void GenomeAI::clear_cache() {
    if (research_engine_) {
        research_engine_->clear_cache();
    }
    
    // Clear other caches
    performance_stats_.cache_hits = 0;
    performance_stats_.cache_misses = 0;
}

bool GenomeAI::setup_directories() {
    namespace fs = std::filesystem;
    
    try {
        // Create output directory
        if (!fs::exists(config_.output_directory)) {
            fs::create_directories(config_.output_directory);
        }
        
        // Create cache directory
        if (!fs::exists(config_.cache_directory)) {
            fs::create_directories(config_.cache_directory);
        }
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Failed to setup directories: " + std::string(e.what()));
        return false;
    }
}

bool GenomeAI::initialize_components() {
    try {
        // Initialize sequence analyzer
        SequenceAnalyzer::Config seq_config;
        seq_config.enable_gpu = config_.enable_gpu;
        seq_config.alignment_threads = config_.max_threads;
        
        sequence_analyzer_ = std::make_unique<SequenceAnalyzer>(seq_config);
        if (!sequence_analyzer_->initialize()) {
            return false;
        }
        
        // Initialize research engine (if web scraping enabled)
        if (config_.enable_web_scraping) {
            ResearchEngine::Config research_config;
            research_config.cache_directory = config_.cache_directory;
            research_config.max_concurrent_requests = std::min(config_.max_threads, size_t(10));
            
            research_engine_ = std::make_unique<ResearchEngine>(research_config);
            if (!research_engine_->initialize()) {
                return false;
            }
        }
        
        // Initialize data pipeline
        data_pipeline_ = std::make_unique<DataPipeline>();
        
        return true;
        
    } catch (const std::exception& e) {
        handle_error("Failed to initialize components: " + std::string(e.what()));
        return false;
    }
}

void GenomeAI::cleanup_components() {
    if (sequence_analyzer_) {
        sequence_analyzer_->shutdown();
        sequence_analyzer_.reset();
    }
    
    if (research_engine_) {
        research_engine_->shutdown();
        research_engine_.reset();
    }
    
    data_pipeline_.reset();
}

void GenomeAI::handle_error(const std::string& error_message) {
    std::cerr << "GenomeAI Error: " << error_message << std::endl;
    
    // Log error to file
    std::ofstream log_file(config_.output_directory + "/error.log", std::ios::app);
    if (log_file.is_open()) {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        log_file << std::ctime(&time_t) << ": " << error_message << std::endl;
    }
}

// Utility functions
std::string get_version_info() {
    return "GenomeAI Research System v1.0.0\n"
           "High-performance C++ implementation for DNA/RNA analysis\n"
           "Built with: " + std::string(__VERSION__) + "\n"
           "Build date: " + std::string(__DATE__) + " " + std::string(__TIME__);
}

bool check_system_requirements() {
    // Check available memory
    // Check CPU features (SIMD support)
    // Check GPU availability
    // This would contain actual system checks
    return true;
}

std::vector<std::string> get_available_gpus() {
    std::vector<std::string> gpus;
    
#ifdef USE_CUDA
    int device_count = 0;
    cudaError_t error = cudaGetDeviceCount(&device_count);
    
    if (error == cudaSuccess) {
        for (int i = 0; i < device_count; ++i) {
            cudaDeviceProp prop;
            cudaGetDeviceProperties(&prop, i);
            gpus.push_back(std::string(prop.name));
        }
    }
#endif
    
    return gpus;
}

} // namespace genomeai