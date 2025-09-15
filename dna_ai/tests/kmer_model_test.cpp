#include "kmer_model.hpp"
#include <gtest/gtest.h>

TEST(KmerModel, PredictsMostFrequent) {
    KmerModel model;
    model.update("AA", 'C');
    model.update("AA", 'G');
    model.update("AA", 'G');
    EXPECT_EQ('G', model.predict("AA"));
}

