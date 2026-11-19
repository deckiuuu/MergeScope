import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.SplittableRandom;

/** Captures comparisons made by the real, unmodified MergeSort class. */
public final class TraceCapture {
    private static final StackWalker WALKER = StackWalker.getInstance();
    private static final class Token implements Comparable<Token> {
        final int key, identity;
        final Recording owner;
        Token(int key, int identity, Recording owner) { this.key=key; this.identity=identity; this.owner=owner; }
        @Override public int compareTo(Token right) {
            int result=Integer.compare(key,right.key);
            owner.capture(this,right,result);
            return result;
        }
    }

    private static final class Recording {
        Token[] working;
        int comparisons;
        final List<String> events=new ArrayList<>();
        void capture(Token left,Token right,int outcome) {
            List<StackWalker.StackFrame> frames=WALKER.walk(stream -> stream
                .filter(frame -> frame.getClassName().equals("MergeSort")).toList());
            String phase=frames.stream().anyMatch(frame -> frame.getMethodName().equals("insertionSort")) ? "insert" : "merge";
            int depth=Math.max(0,(int)frames.stream().filter(frame -> frame.getMethodName().equals("sort")).count()-2);
            comparisons++;
            events.add("{\"type\":\"comparison\",\"phase\":\""+phase+"\",\"depth\":"+depth+
                ",\"count\":"+comparisons+",\"left\":["+left.key+","+left.identity+"],\"right\":["+right.key+","+right.identity+
                "],\"outcome\":"+outcome+",\"array\":"+snapshot()+"}");
        }
        String snapshot() {
            StringBuilder out=new StringBuilder("[");
            for(int i=0;i<working.length;i++) {
                if(i>0) out.append(',');
                out.append('[').append(working[i].key).append(',').append(working[i].identity).append(']');
            }
            return out.append(']').toString();
        }
        String run(int[] input,int cutoff) {
            working=new Token[input.length];
            for(int i=0;i<input.length;i++) working[i]=new Token(input[i],i,this);
            Token[] expected=working.clone();
            Arrays.sort(expected,Comparator.comparingInt(token -> token.key));
            events.add("{\"type\":\"initial\",\"phase\":\"start\",\"depth\":0,\"count\":0,\"array\":"+snapshot()+"}");
            MergeSort.sort(working,cutoff);
            if(!Arrays.equals(working,expected)) throw new AssertionError("Trace disagrees with independent stable oracle");
            events.add("{\"type\":\"complete\",\"phase\":\"done\",\"depth\":0,\"count\":"+comparisons+",\"array\":"+snapshot()+"}");
            return "["+String.join(",",events)+"]";
        }
    }

    public static void main(String[] args) throws Exception {
        if(args.length!=1) throw new IllegalArgumentException("Output JSON path required");
        List<String> cases=new ArrayList<>();
        int tested=0,unique=0;
        for(int n:new int[]{16,33}) {
            SplittableRandom random=new SplittableRandom(7654321L+n);
            int[] base=new int[n];
            for(int i=0;i<n;i++) base[i]=random.nextInt(1,26);
            for(String family:List.of("mixed","ascending","descending")) {
                int[] input=base.clone();
                if(!family.equals("mixed")) Arrays.sort(input);
                if(family.equals("descending")) for(int i=0;i<n/2;i++) {
                    int value=input[i];input[i]=input[n-1-i];input[n-1-i]=value;
                }
                Map<String,Integer> uniqueTraces=new LinkedHashMap<>();
                List<String> references=new ArrayList<>();
                for(int cutoff=1;cutoff<=128;cutoff++) {
                    String trace=new Recording().run(input,cutoff);
                    Integer index=uniqueTraces.get(trace);
                    if(index==null) { index=uniqueTraces.size();uniqueTraces.put(trace,index); }
                    references.add("\""+cutoff+"\":"+index);
                    tested++;
                }
                unique+=uniqueTraces.size();
                cases.add("{\"id\":\""+family+"-"+n+"\",\"family\":\""+family+"\",\"size\":"+n+
                    ",\"aliases\":{"+String.join(",",references)+"},\"recordings\":["+String.join(",",uniqueTraces.keySet())+"]}");
            }
        }
        Files.writeString(Path.of(args[0]),"{\"source\":\"Unmodified MergeSort with logging Comparable values\",\"cases\":["+
            String.join(",",cases)+"],\"verified_runs\":"+tested+",\"distinct_recordings\":"+unique+"}",StandardCharsets.UTF_8);
        System.out.println("SUCCESS: "+tested+" actual MergeSort runs verified; "+unique+" distinct comparison recordings.");
        System.out.println("Identical recordings are deduplicated only after complete event streams match byte for byte.");
    }
}
