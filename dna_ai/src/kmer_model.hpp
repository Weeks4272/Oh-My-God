#pragma once
#include <array>
#include <string>
#include <unordered_map>

class KmerModel {
public:
    void load(const std::string& path);
    void save(const std::string& path) const;
    void update(const std::string& ctx, char next);
    char predict(const std::string& ctx) const;

private:
    std::unordered_map<std::string, std::array<size_t,4>> table_;
    static int index(char base);
    static char base_from_index(int idx);
};
