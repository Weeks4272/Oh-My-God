"""Minimal Streamlit interface for the dna_ai C++ engine."""
from pathlib import Path
import subprocess
import tempfile

import streamlit as st

BINARY = Path(__file__).resolve().parents[1] / "build" / "dna_ai"


def run_tool(arg: str) -> None:
    """Execute dna_ai with the provided accession or file path."""
    if not BINARY.exists():
        st.error("dna_ai binary not found. Build it first (see README).")
        return
    try:
        result = subprocess.run([str(BINARY), arg], check=True, capture_output=True, text=True)
        st.text(result.stdout)
    except subprocess.CalledProcessError as exc:
        st.error(exc.stderr or "dna_ai returned an error")


st.title("DNA/RNA Analyzer")
acc = st.text_input("NCBI accession")
upload = st.file_uploader("or upload a FASTA file", type=["fasta", "fa", "fna", "txt"])

if st.button("Analyze"):
    if upload is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as tmp:
            tmp.write(upload.read())
            path = tmp.name
        run_tool(path)
    elif acc:
        run_tool(acc)
    else:
        st.warning("Provide an accession or upload a FASTA file.")
