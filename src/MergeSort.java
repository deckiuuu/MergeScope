import java.util.Objects;

public final class MergeSort {
    private MergeSort() { }

    public static <T extends Comparable<? super T>> void sort(T[] a, int cutoff) {
        Objects.requireNonNull(a, "array");
        if (cutoff < 1) throw new IllegalArgumentException("cutoff must be >= 1");
        @SuppressWarnings("unchecked")
        T[] aux = (T[]) new Comparable<?>[a.length];
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    private static <T extends Comparable<? super T>> void sort(
            T[] a, T[] aux, int lo, int hi, int cutoff) {
        if (hi - lo < cutoff) {
            insertionSort(a, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);
        merge(a, aux, lo, mid, hi);
    }

    private static <T extends Comparable<? super T>> void insertionSort(
            T[] a, int lo, int hi) {
        for (int i = lo; i <= hi; i++) {
            for (int j = i; j > lo && less(a[j], a[j - 1]); j--) {
                T temp = a[j];
                a[j] = a[j - 1];
                a[j - 1] = temp;
            }
        }
    }

    private static <T extends Comparable<? super T>> void merge(
            T[] a, T[] aux, int lo, int mid, int hi) {
        for (int k = lo; k <= hi; k++) aux[k] = a[k];
        int i = lo;
        int j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid) a[k] = aux[j++];
            else if (j > hi) a[k] = aux[i++];
            else if (less(aux[j], aux[i])) a[k] = aux[j++];
            else a[k] = aux[i++];
        }
    }

    private static <T extends Comparable<? super T>> boolean less(T v, T w) {
        return v.compareTo(w) < 0;
    }
}
