# DNA/RNA Research AI

Lightweight C++ tool for fetching nucleotide sequences and computing GC content.

## Features
- Fetches data from NCBI or a local FASTA file
- Calculates GC content and sequence length
- Writes results to a compressed `summary.gz`
- Learns from ambiguous bases using a simple k-mer model and refines predictions over time

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

The tool stores k-mer statistics in `kmer_model.txt` and uses them to guess unknown bases on later runs.

## Optimization
- Compiled with `-O3 -march=native`
- Streams output directly into gzip

## Debugging
- Build with debug info: `cmake -DCMAKE_BUILD_TYPE=Debug ../dna_ai && make`
- Run under gdb: `gdb ./dna_ai`
- Network errors show curl messages; test offline with a local FASTA file

## Web App
A lightweight Streamlit interface wraps the C++ engine.

1. Build `dna_ai` as above
2. Install the app's dependency and launch:
   ```bash
   cd streamlit_template
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. Enter an accession or upload a FASTA file to view GC content and sequence length

