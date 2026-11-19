import java.io.BufferedWriter;
import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Properties;
import java.util.Random;

/** One independently launched JVM. Only calls to the supplied sorter are timed. */
public final class MeasureTrial {
    private static volatile long observed;
    private record Sample(String id, String family, int size, long seed,
                          Integer[] original, Integer[] answer) { }

    private static List<Sample> load(Path index) throws IOException {
        List<String> records = Files.readAllLines(index, StandardCharsets.UTF_8);
        List<Sample> samples = new ArrayList<>();
        if (!records.get(0).equals("id,distribution,length,seed,path,sha256"))
            throw new IOException("Unexpected dataset index header");
        for (String record : records.subList(1, records.size())) {
            String[] field = record.split(",", -1);
            int n = Integer.parseInt(field[2]);
            List<String> values = Files.readAllLines(index.getParent().resolve(field[4]), StandardCharsets.UTF_8);
            if (values.size() != n + 1 || !values.get(0).equals("value"))
                throw new IOException("Malformed dataset " + field[0]);
            Integer[] input = new Integer[n];
            for (int i = 0; i < n; i++) input[i] = Integer.valueOf(values.get(i + 1));
            Integer[] answer = input.clone();
            Arrays.sort(answer);
            samples.add(new Sample(field[0], field[1], n, Long.parseLong(field[3]), input, answer));
        }
        return samples;
    }

    private static void metadata(Path destination, int process, Properties plan) throws IOException {
        Properties record = new Properties();
        for (String key : List.of("java.version", "java.vendor", "java.vm.name", "os.name", "os.version", "os.arch"))
            record.setProperty(key, System.getProperty(key));
        record.setProperty("process", Integer.toString(process));
        record.setProperty("utc.start", Instant.now().toString());
        record.setProperty("heap.limit", Long.toString(Runtime.getRuntime().maxMemory()));
        record.setProperty("jvm.flags", String.join(" ", java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments()));
        record.setProperty("repetitions", plan.getProperty("repetitions"));
        try (BufferedWriter writer = Files.newBufferedWriter(destination, StandardCharsets.UTF_8)) {
            record.store(writer, "Observed Java runtime for this process");
        }
    }

    private static void warm(List<Sample> samples, List<Integer> cutoffs, int milliseconds) {
        int smallest = samples.stream().mapToInt(Sample::size).min().orElseThrow();
        List<Sample> pool = samples.stream().filter(s -> s.size == smallest).toList();
        long began = System.nanoTime();
        int iteration = 0;
        do {
            for (int cutoff : cutoffs) {
                Sample sample = pool.get(iteration++ % pool.size());
                Integer[] copy = sample.original.clone();
                MergeSort.sort(copy, cutoff);
                observed += copy[copy.length / 2];
            }
        } while (System.nanoTime() - began < milliseconds * 1_000_000L);
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 4) throw new IllegalArgumentException("index.csv plan.properties process output-prefix");
        Properties plan = new Properties();
        try (Reader reader = Files.newBufferedReader(Path.of(args[1]), StandardCharsets.UTF_8)) { plan.load(reader); }
        int process = Integer.parseInt(args[2]);
        Path prefix = Path.of(args[3]);
        int repeats = Integer.parseInt(plan.getProperty("repetitions"));
        int practice = Integer.parseInt(plan.getProperty("practice"));
        List<Integer> thresholds = new ArrayList<>();
        for (String value : plan.getProperty("thresholds").split(",")) thresholds.add(Integer.parseInt(value));
        List<Sample> samples = load(Path.of(args[0]));
        Random order = new Random(Long.parseLong(plan.getProperty("order.seed")) + 1009L * process);
        metadata(Path.of(prefix + ".properties"), process, plan);
        warm(samples, thresholds, Integer.parseInt(plan.getProperty("warmup.ms")));
        Collections.shuffle(samples, order);
        try (BufferedWriter csv = Files.newBufferedWriter(Path.of(prefix + ".csv"), StandardCharsets.UTF_8)) {
            csv.write("process,dataset,distribution,length,seed,cutoff,repetition,order_position,batch_size,elapsed_ns,nanos_per_sort,digest\n");
            int completed = 0;
            for (Sample sample : samples) {
                int batch = Math.max(1, Math.min(8, (6000 + sample.size - 1) / sample.size));
                for (int repetition = -practice; repetition < repeats; repetition++) {
                    List<Integer> schedule = new ArrayList<>(thresholds);
                    Collections.shuffle(schedule, order);
                    for (int position = 0; position < schedule.size(); position++) {
                        int cutoff = schedule.get(position);
                        Integer[][] working = new Integer[batch][];
                        for (int k = 0; k < batch; k++) working[k] = sample.original.clone();
                        long before = System.nanoTime();
                        for (Integer[] array : working) MergeSort.sort(array, cutoff);
                        long duration = System.nanoTime() - before;
                        long digest = 0;
                        for (Integer[] array : working) {
                            if (!Arrays.equals(array, sample.answer))
                                throw new AssertionError("Incorrect output " + sample.id + " cutoff " + cutoff);
                            digest += Arrays.hashCode(array);
                        }
                        observed ^= digest;
                        if (repetition >= 0) csv.write(String.format(Locale.ROOT,
                            "%d,%s,%s,%d,%d,%d,%d,%d,%d,%d,%.6f,%d%n", process, sample.id,
                            sample.family, sample.size, sample.seed, cutoff, repetition, position,
                            batch, duration, duration / (double) batch, digest));
                    }
                }
                csv.flush();
                System.out.println("Finished dataset " + (++completed) + "/" + samples.size() + " " + sample.id);
            }
        }
        System.out.println("Measurement process " + process + " succeeded; retained=" + observed);
    }
}
