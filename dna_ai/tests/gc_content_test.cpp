#include <gtest/gtest.h>
#include <string>

double gc_content(const std::string&);

TEST(GCContent, HandlesBasic) {
    EXPECT_DOUBLE_EQ(gc_content("GCGC"), 1.0);
}

TEST(GCContent, MixedCase) {
    EXPECT_DOUBLE_EQ(gc_content("gCat"), 0.5);
}

TEST(GCContent, RNABases) {
    EXPECT_DOUBLE_EQ(gc_content("GGUU"), 0.5);
}

TEST(GCContent, IgnoresInvalid) {
    EXPECT_DOUBLE_EQ(gc_content("ABCDXYZ"), 0.25);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
