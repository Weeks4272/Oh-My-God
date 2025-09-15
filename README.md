# DNA/RNA Research AI

Lightweight C++ tool for fetching nucleotide sequences and computing GC content.

## Features
- Fetches data from NCBI or a local FASTA file
- Calculates GC content and sequence length
- Writes results to a compressed `summary.gz`

## Installation
1. Install a C++17 compiler, CMake, libcurl, and zlib
2. Build:
   
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

