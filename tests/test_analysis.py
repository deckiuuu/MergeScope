"""Independent numerical invariants for the statistical analysis."""
import math
import unittest
from labcore.statistics import bootstrap_ratio,leaf_profile,quantile,structural_groups


class AnalysisProperties(unittest.TestCase):
    def test_recursion_boundary_examples(self):
        self.assertEqual(leaf_profile(9,4),((2,1),(3,1),(4,1)))
        self.assertEqual(structural_groups([16],range(1,17)),[[1],[2,3],[4,5,6,7],list(range(8,16)),[16]])

    def test_partition_preserves_length(self):
        for n in [1,17,2053,150053]:
            for cutoff in [1,7,10,19,40,128]:
                profile=leaf_profile(n,cutoff)
                self.assertEqual(sum(length*count for length,count in profile),n)
                self.assertTrue(all(0<length<=cutoff for length,count in profile))

    def test_constant_speed_ratio_has_exact_interval(self):
        configuration={'processes':4,'seeds':[11,29,41],'families':['a','b'],'lengths':[17,93]}
        medians={}
        for f in range(4):
            for seed in configuration['seeds']:
                for family in configuration['families']:
                    for n in configuration['lengths']:
                        base=(f+1)*seed*n
                        medians[family,n,seed,f,1]=base*2
                        medians[family,n,seed,f,20]=base
        point,low,high=bootstrap_ratio(medians,configuration,1,20,500,5)
        for value in [point,low,high]: self.assertAlmostEqual(value,2,places=12)

    def test_interpolated_quartiles(self):
        self.assertEqual(quantile([0,10,20,30],.25),7.5)
        self.assertEqual(quantile([0,10,20,30],.5),15)


if __name__=='__main__': unittest.main()
