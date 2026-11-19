import java.util.Arrays;
import java.util.Comparator;
import java.util.SplittableRandom;

/** Tests the public contract without changing the supplied implementation. */
public final class SortContractTest {
    private static long assertions;
    private record Entry(int key, int sequence) implements Comparable<Entry> {
        @Override public int compareTo(Entry other) { return Integer.compare(key, other.key); }
    }

    private static void ensure(boolean condition, String context) {
        assertions++;
        if (!condition) throw new AssertionError(context);
    }

    private static void againstOracle(Integer[] input, int threshold) {
        Integer[] actual = input.clone();
        Integer[] expected = input.clone();
        Arrays.sort(expected);
        MergeSort.sort(actual, threshold);
        ensure(Arrays.equals(actual, expected), "values n=" + input.length + " cutoff=" + threshold);
    }

    public static void main(String[] ignored) {
        for (int size = 0; size <= 6; size++) {
            int possibilities = 1;
            for (int i = 0; i < size; i++) possibilities *= 3;
            for (int encoding = 0; encoding < possibilities; encoding++) {
                Integer[] sequence = new Integer[size];
                int remaining = encoding;
                for (int j = 0; j < size; j++) { sequence[j] = remaining % 3 - 1; remaining /= 3; }
                for (int cutoff = 1; cutoff <= 12; cutoff++) againstOracle(sequence, cutoff);
            }
        }
        SplittableRandom random = new SplittableRandom(918273645L);
        for (int cutoff = 1; cutoff <= 128; cutoff++) {
            for (int delta : new int[]{-1, 0, 1}) {
                int n = Math.max(0, cutoff + delta);
                Integer[] a = new Integer[n];
                for (int i = 0; i < n; i++) a[i] = random.nextInt(-30, 31);
                againstOracle(a, cutoff);
            }
            for (int trial = 0; trial < 16; trial++) {
                Integer[] a = new Integer[random.nextInt(700)];
                for (int i = 0; i < a.length; i++) a[i] = random.nextInt();
                againstOracle(a, cutoff);
            }
            Entry[] tagged = new Entry[350];
            for (int i = 0; i < tagged.length; i++) tagged[i] = new Entry(random.nextInt(13), i);
            Entry[] stableOracle = tagged.clone();
            Arrays.sort(stableOracle, Comparator.comparingInt(Entry::key));
            MergeSort.sort(tagged, cutoff);
            ensure(Arrays.equals(tagged, stableOracle), "stable object identity at " + cutoff);
        }
        for (int cutoff : new int[]{1, 7, 10, 33, 128, Integer.MAX_VALUE}) {
            againstOracle(new Integer[]{Integer.MAX_VALUE, 0, Integer.MIN_VALUE, -1, 1}, cutoff);
            Integer[] large = new Integer[8193];
            for (int i = 0; i < large.length; i++) large[i] = large.length - i;
            againstOracle(large, cutoff == Integer.MAX_VALUE ? 128 : cutoff);
        }
        String[] words = {"zebra", "a", "á", "a", "Merge", "sort"};
        String[] expectedWords = words.clone();
        Arrays.sort(expectedWords);
        MergeSort.sort(words, 10);
        ensure(Arrays.equals(words, expectedWords), "generic String contract");
        for (int invalid : new int[]{Integer.MIN_VALUE, -5, 0}) {
            try { MergeSort.sort(new Integer[0], invalid); throw new AssertionError("accepted cutoff"); }
            catch (IllegalArgumentException expected) { ensure(true, "rejected cutoff"); }
        }
        try { MergeSort.sort((Integer[]) null, 1); throw new AssertionError("accepted null array"); }
        catch (NullPointerException expected) { ensure(true, "rejected null"); }
        System.out.println("SUCCESS: " + assertions + " independent contract checks");
        System.out.println("Coverage: exhaustive ternary inputs, every cutoff 1..128, cutoff boundaries, stability, generics, invalid arguments and long descending input.");
    }
}
