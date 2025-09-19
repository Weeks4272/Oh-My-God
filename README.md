# DNA/RNA Research AI


Lightweight C++ tool for fetching nucleotide sequences and computing GC content.

## Features
- Fetches data from NCBI or a local FASTA file
- Calculates GC content and sequence length
- Writes results to a compressed `summary.gz`

## Installation
1. Install a C++17 compiler, CMake, libcurl, and zlib
2. Build:


This project provides a lightweight C++ tool for fetching nucleotide sequences from the NCBI databases and performing basic analysis, optimized for data‑science workflows.

## Features
- **High performance C++ core** compiled with `-O3 -march=native` for optimal speed.
- Fetches sequence data over HTTPS using libcurl with a custom user agent and optional `NCBI_API_KEY` for higher request limits, or reads a local FASTA file when a path is provided.
- Computes GC content and sequence length.
- Streams results directly into a compressed `summary.gz` via zlib to minimize storage.
- RAII and standard library containers ensure safe memory management and no leaks.

## Installation
1. Ensure a C++17 compiler, CMake, `libcurl`, and `zlib` are installed.
2. Build the project:

   ```bash
   mkdir build && cd build
   cmake ../dna_ai
   make
   ```

   
## Usage
Fetch an accession:
```bash
./dna_ai NM_007294.4
```
Analyze a local file:


## Usage Example
```bash
./dna_ai NM_007294.4
```
This retrieves the BRCA1 mRNA sequence, calculates GC content, prints the results, and writes a compressed summary to `summary.gz`.

To analyze an offline FASTA file:

```bash
./dna_ai path/to/local.fasta
```


## Optimization
- Compiled with `-O3 -march=native`
- Streams output directly into gzip

## Debugging
- Build with debug info: `cmake -DCMAKE_BUILD_TYPE=Debug ../dna_ai && make`
- Run under gdb: `gdb ./dna_ai`
- Network errors show curl messages; test offline with a local FASTA file

## Optimization Strategies
- Compilation with `-O3 -march=native` and warnings enabled for performance and safety.
- Minimal dynamic allocation and use of `std::string` for efficient memory.
- Streaming compression with zlib reduces disk footprint without extra buffers.

## Debugging Notes
- Network errors and HTTP status codes are reported explicitly with descriptive messages.
- The build uses standard warnings to catch potential issues early.

## Future Work
- Incorporate multi-threaded sequence analysis.
- Add parsers for additional data formats (JSON, XML).
- Extend analytics (motif search, secondary structure prediction).

## Limitations
- Requires access to the NCBI web APIs.
- Only basic GC-content analysis is currently implemented.


