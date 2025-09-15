#include <curl/curl.h>
#include <zlib.h>
#include <cctype>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <chrono>
#include "kmer_model.hpp"

// RAII wrapper for global curl init/cleanup
struct CurlGlobal {
    CurlGlobal() { curl_global_init(CURL_GLOBAL_DEFAULT); }
    ~CurlGlobal() { curl_global_cleanup(); }
};

// Write callback for libcurl
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    size_t totalSize = size * nmemb;
    std::string* s = static_cast<std::string*>(userp);
    s->append(static_cast<char*>(contents), totalSize);
    return totalSize;
}

std::string fetch_sequence(const std::string& accession) {
    namespace fs = std::filesystem;
    if (fs::exists(accession)) {
        std::ifstream file(accession);
        if (!file.is_open()) {
            throw std::runtime_error("Failed to open file: " + accession);
        }
        std::ostringstream ss;
        ss << file.rdbuf();
        return ss.str();
    }

    CURL* raw = curl_easy_init();
    if (!raw) throw std::runtime_error("Failed to init curl");
    std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> curl(raw, curl_easy_cleanup);
    std::string buffer;

    std::string url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=" + accession + "&rettype=fasta&retmode=text";
    if (const char* api_key = std::getenv("NCBI_API_KEY")) {
        url += "&api_key=" + std::string(api_key);
    }

    curl_easy_setopt(curl.get(), CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl.get(), CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl.get(), CURLOPT_WRITEDATA, &buffer);
    curl_easy_setopt(curl.get(), CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl.get(), CURLOPT_USERAGENT, "dna_ai/1.0 (https://example.com)");
    curl_easy_setopt(curl.get(), CURLOPT_FAILONERROR, 1L);

    CURLcode res = CURLE_OK;
    for (int attempt = 0; attempt < 3; ++attempt) {
        res = curl_easy_perform(curl.get());
        if (res == CURLE_OK) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(100 * (1 << attempt)));
    }
    if (res != CURLE_OK) {
        throw std::runtime_error("Network error while fetching sequence");
    }

    long http_code = 0;
    curl_easy_getinfo(curl.get(), CURLINFO_RESPONSE_CODE, &http_code);
    if (http_code != 200) {
        throw std::runtime_error("HTTP response code: " + std::to_string(http_code));
    }

    return buffer;
}

double gc_content(const std::string& sequence) {
    size_t gc = 0, total = 0;
    for (char c : sequence) {
        char upper = std::toupper(static_cast<unsigned char>(c));
        if (upper == 'G' || upper == 'C') gc++;
        if (upper == 'A' || upper == 'T' || upper == 'G' || upper == 'C' || upper == 'U') total++;
    }
    if (total == 0) return 0.0;
    return static_cast<double>(gc) / static_cast<double>(total);
}

#ifndef UNIT_TESTING
int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <accession>" << std::endl;
        return 1;
    }

    CurlGlobal curlGlobal; // ensure global cleanup

    try {
        std::string fasta = fetch_sequence(argv[1]);
        std::string raw;
        raw.reserve(fasta.size());
        for (size_t i = 0; i < fasta.size(); ++i) {
            if (fasta[i] == '>') {
                while (i < fasta.size() && fasta[i] != '\n') ++i; // skip header line
            } else if (std::isalpha(static_cast<unsigned char>(fasta[i]))) {
                raw += std::toupper(static_cast<unsigned char>(fasta[i]));
            }
        }

        KmerModel model;
        model.load("kmer_model.txt");
        std::string sequence = raw;
        if (sequence.size() >= 2) {
            for (size_t i = 2; i < sequence.size(); ++i) {
                std::string ctx{sequence[i-2], sequence[i-1]};
                char base = sequence[i];
                if (base != 'A' && base != 'C' && base != 'G' && base != 'T') {
                    char guess = model.predict(ctx);
                    if (guess != 'N') base = sequence[i] = guess;
                }
                if (base == 'U') base = sequence[i] = 'T';
                model.update(ctx, base);
            }
        }
        model.save("kmer_model.txt");

        double gc = gc_content(sequence);
        std::string summary = "Length: " + std::to_string(sequence.size()) + "\nGC Content: " + std::to_string(gc);

        gzFile gz = gzopen("summary.gz", "wb");
        if (!gz) throw std::runtime_error("Failed to open output file");
        if (gzwrite(gz, summary.data(), static_cast<unsigned>(summary.size())) == 0) {
            int err = 0; const char* msg = gzerror(gz, &err);
            gzclose(gz);
            throw std::runtime_error(std::string("gzwrite failed: ") + (msg ? msg : ""));
        }
        gzclose(gz);

        std::cout << summary << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
#endif

