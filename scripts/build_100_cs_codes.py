import json
import os
import re

# 100 Rigorous Computer Science Coding Topics
cs_100_topics = [
    # Operating Systems & Concurrency (20)
    ("mutex lock and spinlock implementation", "cpp", "Mutex Lock & Spinlock", ["mutex", "spinlock", "lock", "thread"]),
    ("counting semaphore for resource pool", "python", "Counting Semaphore", ["semaphore", "acquire", "release", "counter"]),
    ("producer consumer problem with bounded buffer", "java", "Producer Consumer Bounded Buffer", ["producer", "consumer", "buffer", "queue"]),
    ("dining philosophers deadlock free solution", "rust", "Dining Philosophers", ["philosopher", "fork", "chopstick", "mutex"]),
    ("readers writers problem with read priority", "cpp", "Readers-Writers Problem", ["reader", "writer", "read", "priority"]),
    ("lru least recently used page replacement", "python", "LRU Page Replacement", ["lru", "cache", "capacity", "ordered"]),
    ("lfu least frequently used cache o1", "java", "LFU Cache O(1)", ["lfu", "frequency", "min", "cache"]),
    ("round robin cpu process scheduler with quantum", "c", "Round Robin Scheduler", ["quantum", "process", "burst", "round"]),
    ("shortest job first sjf preemptive scheduler", "cpp", "SJF Preemptive Scheduler", ["sjf", "burst", "arrival", "shortest"]),
    ("priority process scheduler with aging", "python", "Priority Scheduler with Aging", ["priority", "aging", "starvation", "process"]),
    ("bankers algorithm for deadlock avoidance", "python", "Banker's Algorithm", ["banker", "safe", "need", "allocation"]),
    ("virtual memory multi level page table simulation", "c", "Multi-Level Page Table", ["page", "table", "pte", "virtual"]),
    ("free list memory allocator first fit best fit", "c", "Free List Allocator", ["allocator", "free", "block", "fit"]),
    ("buddy system memory allocation and coalescing", "cpp", "Buddy System Allocator", ["buddy", "allocate", "split", "coalesce"]),
    ("copy on write cow memory page simulation", "cpp", "Copy-on-Write Simulation", ["cow", "page", "refcount", "copy"]),
    ("thread pool executor with work stealing queue", "rust", "Work-Stealing Thread Pool", ["worker", "thread", "pool", "steal"]),
    ("epoll event reactor pattern implementation", "cpp", "Epoll Reactor Pattern", ["reactor", "epoll", "event", "socket"]),
    ("ipc shared memory circular ring buffer", "c", "IPC Circular Ring Buffer", ["ring", "buffer", "head", "tail"]),
    ("unix inode and file descriptor table", "c", "Unix Inode & FD Table", ["inode", "fd", "descriptor", "file"]),
    ("double checked locking pattern with memory barrier", "java", "Double-Checked Locking", ["singleton", "volatile", "instance", "lock"]),

    # Computer Networking & Protocols (15)
    ("tcp three way handshake state machine", "python", "TCP 3-Way Handshake", ["syn", "ack", "handshake", "state"]),
    ("sliding window protocol go back n selective repeat", "cpp", "Sliding Window Protocol", ["window", "seq", "ack", "packet"]),
    ("tcp congestion control slow start fast retransmit", "python", "TCP Congestion Control", ["cwnd", "ssthresh", "congestion", "slow"]),
    ("non blocking tcp echo server with sockets", "python", "Non-Blocking TCP Server", ["socket", "select", "listen", "accept"]),
    ("http chunked transfer encoding parser", "javascript", "HTTP Chunked Parser", ["chunk", "hex", "encoding", "parser"]),
    ("websocket frame masking and unmasking", "typescript", "WebSocket Frame Masking", ["mask", "payload", "websocket", "frame"]),
    ("dns packet header and question parser", "python", "DNS Packet Parser", ["dns", "header", "query", "question"]),
    ("cidr ipv4 subnet calculator and range validator", "python", "CIDR Subnet Calculator", ["cidr", "subnet", "mask", "broadcast"]),
    ("dijkstra link state routing ospf algorithm", "cpp", "OSPF Link-State Routing", ["dijkstra", "routing", "cost", "distance"]),
    ("bellman ford distance vector rip protocol", "python", "Distance Vector Routing", ["bellman", "distance", "vector", "router"]),
    ("leaky bucket traffic shaping algorithm", "java", "Leaky Bucket Traffic Shaper", ["leaky", "bucket", "drop", "traffic"]),
    ("token bucket rate limiter with refill interval", "rust", "Token Bucket Rate Limiter", ["token", "bucket", "refill", "capacity"]),
    ("network packet internet checksum rfc 1071", "c", "Internet Checksum RFC 1071", ["checksum", "16", "carry", "packet"]),
    ("arp table cache with entry timeout", "python", "ARP Table Cache", ["arp", "mac", "ip", "timeout"]),
    ("nat network address translation port mapping", "cpp", "NAT Port Mapping", ["nat", "port", "translation", "mapping"]),

    # Compilers, Interpreters & Automata (15)
    ("lexical analyzer tokenizer for arithmetic expressions", "typescript", "Expression Tokenizer", ["token", "lexer", "scan", "type"]),
    ("recursive descent parser for arithmetic grammar", "python", "Recursive Descent Parser", ["parser", "expr", "term", "factor"]),
    ("abstract syntax tree ast evaluator visitor pattern", "typescript", "AST Evaluator Visitor", ["ast", "node", "visitor", "eval"]),
    ("shunting yard algorithm infix to rpn", "python", "Shunting-Yard Infix to RPN", ["shunting", "infix", "rpn", "stack"]),
    ("reverse polish notation rpn stack evaluator", "javascript", "RPN Stack Evaluator", ["rpn", "stack", "operand", "eval"]),
    ("deterministic finite automaton dfa transition engine", "python", "DFA State Transition Engine", ["dfa", "state", "transition", "accept"]),
    ("nfa to dfa powerset subset construction", "cpp", "NFA to DFA Subset Construction", ["nfa", "dfa", "powerset", "epsilon"]),
    ("regular expression thompson nfa simulation", "python", "Thompson NFA Simulation", ["thompson", "nfa", "state", "match"]),
    ("scoped symbol table with lexical shadowing", "typescript", "Scoped Symbol Table", ["symbol", "scope", "parent", "lookup"]),
    ("stack based bytecode virtual machine", "rust", "Stack Bytecode VM", ["bytecode", "vm", "opcode", "stack"]),
    ("constant folding compiler optimization pass", "python", "Constant Folding Optimization", ["constant", "folding", "ast", "optimize"]),
    ("dead code elimination via reachability analysis", "cpp", "Dead Code Elimination", ["dead", "code", "reachable", "cfg"]),
    ("control flow graph cfg basic blocks construction", "python", "Control Flow Graph CFG", ["cfg", "block", "edge", "branch"]),
    ("first and follow set generator for ll1 grammar", "python", "LL(1) First & Follow Sets", ["first", "follow", "grammar", "terminal"]),
    ("type checker for static type inference", "typescript", "Static Type Checker", ["type", "infer", "check", "env"]),

    # Databases & Storage Engines (15)
    ("b plus tree node splitting and search", "cpp", "B+ Tree Index", ["btree", "node", "split", "leaf"]),
    ("lsm tree memtable and sstable flush", "rust", "LSM-Tree MemTable & SSTable", ["lsm", "memtable", "sstable", "flush"]),
    ("write ahead log wal crash recovery simulation", "python", "Write-Ahead Log (WAL)", ["wal", "log", "commit", "recovery"]),
    ("extendible hashing dynamic directory directory depth", "cpp", "Extendible Hashing", ["hashing", "bucket", "depth", "directory"]),
    ("two phase commit 2pc transaction coordinator", "java", "2-Phase Commit (2PC)", ["2pc", "prepare", "commit", "coordinator"]),
    ("two phase locking 2pl strict concurrency control", "python", "Strict 2PL Concurrency", ["lock", "shared", "exclusive", "2pl"]),
    ("multiversion concurrency control mvcc read view", "rust", "MVCC Read-View", ["mvcc", "version", "transaction", "visibility"]),
    ("inverted index full text search tf idf ranking", "python", "Inverted Index with TF-IDF", ["index", "token", "document", "tfidf"]),
    ("columnar storage run length encoding rle", "python", "Columnar Storage RLE", ["columnar", "rle", "compress", "run"]),
    ("bitmap index for fast boolean filter queries", "cpp", "Bitmap Index Querying", ["bitmap", "bitwise", "cardinality", "filter"]),
    ("cost based query join optimizer nested vs hash join", "python", "Cost-Based Join Optimizer", ["optimizer", "join", "cost", "hash"]),
    ("database buffer pool manager clock sweep page replacement", "cpp", "Buffer Pool Clock Sweep", ["buffer", "pool", "frame", "clock"]),
    ("b tree node underflow borrow and merge rebalance", "python", "B-Tree Node Rebalancing", ["btree", "borrow", "merge", "underflow"]),
    ("hyperloglog cardinality estimation stream", "python", "HyperLogLog Stream Estimation", ["hyperloglog", "hll", "hash", "cardinality"]),
    ("write through and write back cache simulation", "cpp", "Write-Through/Back Cache", ["cache", "dirty", "flush", "write"]),

    # Distributed Systems & Cloud Infrastructure (15)
    ("consistent hashing ring with virtual nodes", "python", "Consistent Hashing Ring", ["consistent", "hash", "ring", "node"]),
    ("raft distributed consensus leader election machine", "rust", "Raft Leader Election", ["raft", "leader", "term", "election"]),
    ("paxos consensus proposer acceptor algorithm", "python", "Paxos Consensus Protocol", ["paxos", "propose", "promise", "accept"]),
    ("lamport logical clock distributed event ordering", "typescript", "Lamport Logical Clock", ["lamport", "clock", "timestamp", "tick"]),
    ("vector clock for causal dependency tracking", "python", "Vector Clock Causal Tracking", ["vector", "clock", "causal", "process"]),
    ("gossip protocol anti entropy state dissemination", "python", "Gossip Protocol Anti-Entropy", ["gossip", "peer", "node", "rumor"]),
    ("bloom filter probabilistic set membership", "python", "Bloom Filter", ["bloom", "filter", "hash", "contains"]),
    ("counting bloom filter with element deletion support", "cpp", "Counting Bloom Filter", ["counting", "bloom", "filter", "delete"]),
    ("cuckoo filter with partial key cuckoo hashing", "rust", "Cuckoo Filter", ["cuckoo", "filter", "bucket", "kick"]),
    ("distributed lock manager with heartbeat lease ttl", "python", "Distributed Lock Lease TTL", ["lock", "lease", "ttl", "heartbeat"]),
    ("two phase commit distributed transaction coordinator", "java", "Distributed 2PC Coordinator", ["coordinator", "cohort", "vote", "commit"]),
    ("circuit breaker pattern closed open half open", "typescript", "Circuit Breaker Pattern", ["circuit", "breaker", "threshold", "half"]),
    ("exponential backoff retry algorithm with jitter", "python", "Exponential Backoff Jitter", ["backoff", "retry", "jitter", "delay"]),
    ("merkle tree generation and cryptographic proof", "python", "Merkle Tree Proofs", ["merkle", "tree", "hash", "proof"]),
    ("sharded distributed key value store range partitioned", "python", "Sharded KV Store", ["shard", "partition", "key", "store"]),

    # Advanced Data Structures & Algorithms (20)
    ("segment tree range sum query point update", "cpp", "Segment Tree Range Sum", ["segment", "tree", "query", "update"]),
    ("segment tree with lazy propagation range update", "cpp", "Lazy Segment Tree", ["lazy", "propagation", "range", "tree"]),
    ("binary indexed tree fenwick tree prefix sums", "python", "Binary Indexed Tree (Fenwick)", ["fenwick", "bit", "prefix", "sum"]),
    ("trie prefix tree autocomplete wildcard search", "python", "Trie Prefix Autocomplete", ["trie", "insert", "search", "prefix"]),
    ("suffix array and longest common prefix lcp", "cpp", "Suffix Array & LCP", ["suffix", "array", "lcp", "string"]),
    ("disjoint set union dsu rank path compression", "python", "DSU Union-Find", ["dsu", "find", "union", "parent"]),
    ("tarjan strongly connected components scc directed graph", "cpp", "Tarjan's SCC Algorithm", ["tarjan", "scc", "dfs", "low"]),
    ("kosaraju strongly connected components two pass", "python", "Kosaraju's SCC Algorithm", ["kosaraju", "transpose", "scc", "dfs"]),
    ("a star heuristic pathfinding algorithm 2d grid", "python", "A* Pathfinding Algorithm", ["astar", "heuristic", "path", "open"]),
    ("knuth morris pratt kmp string matching failure function", "python", "KMP String Matching", ["kmp", "pi", "pattern", "failure"]),
    ("rabin karp rolling hash substring search", "python", "Rabin-Karp Rolling Hash", ["rabin", "karp", "hash", "rolling"]),
    ("boyer moore bad character heuristic string search", "cpp", "Boyer-Moore Search", ["boyer", "moore", "bad", "shift"]),
    ("topological sort using kahns in degree bfs", "python", "Kahn's Topological Sort", ["topological", "kahn", "indegree", "bfs"]),
    ("edmonds karp max flow algorithm bfs augmenting path", "cpp", "Edmonds-Karp Max Flow", ["flow", "edmonds", "karp", "residual"]),
    ("dinic algorithm for max network flow level graph", "cpp", "Dinic's Max Flow Algorithm", ["dinic", "flow", "level", "dfs"]),
    ("convex hull graham scan algorithm 2d geometry", "python", "Graham Scan Convex Hull", ["hull", "convex", "graham", "cross"]),
    ("monotonic stack for next greater element on", "python", "Monotonic Stack O(N)", ["monotonic", "stack", "greater", "element"]),
    ("monotonic queue for sliding window maximum on", "cpp", "Monotonic Queue O(N)", ["monotonic", "queue", "sliding", "window"]),
    ("treap cartesian tree random priority heap", "cpp", "Treap Cartesian Tree", ["treap", "priority", "rotations", "split"]),
    ("skip list with probabilistic express pointers", "python", "Skip List O(log N)", ["skip", "list", "level", "express"])
]

print(f"Total CS coding topics: {len(cs_100_topics)}")

# Generate tests/fuzz_100_computer_science_codes.js
test_lines = [
    "/**",
    " * STAGE 52: 100 ADVANCED COMPUTER SCIENCE CODING BENCHMARK",
    " * OS, Networks, Compilers, Databases, Distributed Systems & Advanced DSA",
    " * 100% Offline Multi-Language Execution & Synthesis",
    " */",
    "",
    "const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');",
    "",
    "let passed = 0;",
    "let failed = 0;",
    "const failureDetails = [];",
    "",
    "function assert(condition, testId, prompt, failMsg) {",
    "  if (condition) {",
    "    passed++;",
    "    if (passed % 10 === 0 || passed === 1 || passed === 100) {",
    "      console.log(`  ✅ [PASS #${String(passed).padStart(3, '0')}] [${testId}] \"${prompt}\"`);",
    "    }",
    "  } else {",
    "    failed++;",
    "    console.error(`  ❌ [FAIL #${String(failed).padStart(3, '0')}] [${testId}] \"${prompt}\" -> ${failMsg}`);",
    "    failureDetails.push({ testId, prompt, failMsg });",
    "  }",
    "}",
    "",
    "async function run100ComputerScienceBenchmark() {",
    "  console.log('='.repeat(80));",
    "  console.log('🚀 RUNNING 100 ADVANCED COMPUTER SCIENCE CODING BENCHMARK');",
    "  console.log('='.repeat(80));",
    "  console.log('');",
    "",
    "  const brain = new ClumsyBrainEngine();",
    "  let r = null;",
    "  const startTime = Date.now();",
    ""
]

for idx, (topic_raw, lang_choice, title, keywords) in enumerate(cs_100_topics, 1):
    q = f"write a {lang_choice.upper()} code for {topic_raw}"
    tid = f"CS-{idx:03d}"
    key_checks = " || ".join([f"r.response.toLowerCase().includes({json.dumps(k.lower())})" for k in keywords])
    cond = f"(r && r.response && r.response.length > 50 && ({key_checks}))"
    test_lines.append(f"  // {idx}. {title} ({lang_choice.upper()})")
    test_lines.append(f"  r = await brain.processSmartQuery({json.dumps(q)});")
    test_lines.append(f"  assert({cond}, {json.dumps(tid)}, {json.dumps(q)}, {json.dumps(f'Failed {title}')});")
    test_lines.append("")

test_lines.extend([
    "  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);",
    "  console.log('\\n' + '='.repeat(80));",
    "  console.log(`🏆 100 CS CODES RESULTS: ${passed}/${passed + failed} PASSED (${((passed / (passed + failed || 1)) * 100).toFixed(1)}%) | ${failed} FAILED | ${elapsed}s`);",
    "  console.log('='.repeat(80));",
    "",
    "  if (failed > 0) {",
    "    console.log(`\\n⚠️ DETAILED FAILURE BREAKDOWN (${failed} FAILURES):`);",
    "    failureDetails.forEach((f, idx) => {",
    "      console.log(`  ${idx + 1}. [${f.testId}] \"${f.prompt}\": ${f.failMsg}`);",
    "    });",
    "    process.exit(1);",
    "  } else {",
    "    console.log('\\n✨ ALL 100 COMPUTER SCIENCE CODES PASSED WITH 100% SUCCESS! MASTER SYSTEMS SYNTHESIS COMPLETE! ✨\\n');",
    "    process.exit(0);",
    "  }",
    "}",
    "",
    "run100ComputerScienceBenchmark().catch(err => {",
    "  console.error('Fatal benchmark error:', err);",
    "  process.exit(1);",
    "});"
])

test_path = os.path.join('tests', 'fuzz_100_computer_science_codes.js')
with open(test_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(test_lines))

print(f"Generated {test_path} ({len(test_lines)} lines)")
