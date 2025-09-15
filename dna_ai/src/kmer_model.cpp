#include "kmer_model.hpp"
#include <fstream>
#include <sstream>

int KmerModel::index(char base) {
    switch (base) {
        case 'A': return 0;
        case 'C': return 1;
        case 'G': return 2;
        case 'T': return 3;
        default: return -1;
    }
}

char KmerModel::base_from_index(int idx) {
    static const char* bases = "ACGT";
    return (idx >=0 && idx <4) ? bases[idx] : 'N';
}

void KmerModel::load(const std::string& path) {
    std::ifstream in(path);
    if (!in) return;
    std::string ctx; char base; size_t count;
    while (in >> ctx >> base >> count) {
        int idx = index(base);
        if (idx >= 0) {
            table_[ctx][idx] = count;
        }
    }
}

void KmerModel::save(const std::string& path) const {
    std::ofstream out(path, std::ios::trunc);
    for (const auto& [ctx, arr] : table_) {
        for (int i = 0; i < 4; ++i) {
            if (arr[i] > 0) {
                out << ctx << ' ' << base_from_index(i) << ' ' << arr[i] << '\n';
            }
        }
    }
}

void KmerModel::update(const std::string& ctx, char next) {
    int idx = index(next);
    if (idx >= 0) {
        table_[ctx][idx]++;
    }
}

char KmerModel::predict(const std::string& ctx) const {
    auto it = table_.find(ctx);
    if (it == table_.end()) return 'N';
    const auto& arr = it->second;
    size_t best = 0; int idx = -1;
    for (int i = 0; i < 4; ++i) {
        if (arr[i] > best) {
            best = arr[i]; idx = i;
        }
    }
    return base_from_index(idx);
}
