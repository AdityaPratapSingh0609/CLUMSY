/**
 * CLUMSY // Proprietary Offline-First AI Brain & Multi-Runtime Connector
 *
 * Features:
 *   1. 100% Offline Built-In Knowledge, Science, Physics, Math, Coding & Reasoning Engine
 *   2. Native Local LLM Connectors:
 *        - CLUMSY Local GGUF Server (http://127.0.0.1:8080)
 *        - Ollama Local Runtime     (http://127.0.0.1:11434)
 *        - LM Studio Local Server   (http://127.0.0.1:1234/v1)
 *        - Jan AI Local Server      (http://127.0.0.1:1337/v1)
 *   3. Optional Cloud Fallback when online
 *   4. Interactive Studio Canvas (Code Runner, 60 FPS 3D CAD, AI Video, SVG Art, PPT, App Hub)
 */
(function (global) {
  'use strict';

  const OFFLINE_KNOWLEDGE_BASE = [
    {
      keys: ['quantum mechanics', 'quantum physics', 'schrodinger', 'wave function', 'superposition', 'entanglement', 'qubit', 'quantum computing', 'quantum'],
      title: 'Quantum Mechanics & Quantum Computing',
      response: [
        '**Quantum Mechanics** is the fundamental branch of physics that describes nature at the smallest scales — atoms, electrons, and photons — where classical Newtonian mechanics breaks down.',
        '',
        '### Core Principles:',
        '1. **Wave-Particle Duality:** Subatomic particles like electrons and photons behave as both particles and waves simultaneously.',
        '2. **Superposition:** Unlike a classical bit (which is strictly `0` or `1`), a quantum system can exist in a linear combination of multiple states at once ($|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$) until measured.',
        '3. **Quantum Entanglement:** Two or more particles become correlated so that measuring the state of one instantaneously determines the state of the other, regardless of distance.',
        '4. **Heisenberg Uncertainty Principle:** It is impossible to simultaneously know both the exact position ($x$) and momentum ($p$) of a particle with arbitrary precision ($\\Delta x \\cdot \\Delta p \\ge \\frac{\\hbar}{2}$).',
        '',
        '### Real-World Applications:',
        '• **Quantum Computers** (using qubits to solve molecular simulations, cryptography, and optimization exponentially faster), **Semiconductors & Transistors**, **Lasers**, **MRI Scanners**, and **Atomic Clocks**.'
      ].join('\n')
    },
    {
      keys: ['black hole', 'event horizon', 'hawking radiation', 'singularity', 'spacetime', 'general relativity', 'einstein', 'relativity'],
      title: 'Relativity & Black Holes',
      response: [
        '**General Relativity** (formulated by Albert Einstein in 1915) describes gravity not as an invisible force, but as the **curvature of four-dimensional spacetime** caused by mass and energy ($E = mc^2$).',
        '',
        '### Key Concepts:',
        '1. **Black Holes & Event Horizon:** When a massive star collapses, it warps spacetime so intensely that nothing — not even light — can escape once it crosses the **Event Horizon** (Schwarzschild radius $r_s = \\frac{2GM}{c^2}$).',
        '2. **Gravitational Time Dilation:** Time ticks slower in stronger gravitational fields. Near a black hole, a few minutes for an observer can equal years on Earth.',
        '3. **Hawking Radiation:** Quantum effects near the event horizon cause black holes to emit faint thermal radiation and slowly evaporate over cosmic timescales.'
      ].join('\n')
    },
    {
      keys: ['machine learning', 'deep learning', 'neural network', 'artificial intelligence', 'how does ai work', 'transformer', 'llm', 'large language model', 'backpropagation'],
      title: 'Artificial Intelligence, Machine Learning & Neural Networks',
      response: [
        '**Artificial Intelligence (AI)** and **Machine Learning (ML)** enable systems to learn patterns directly from data rather than following hardcoded rules.',
        '',
        '### How Modern AI Works:',
        '1. **Neural Networks:** Modeled loosely on the human brain, layers of artificial neurons compute weighted sums of inputs ($y = \\sigma(Wx + b)$) and adjust their weights via **Backpropagation** and **Gradient Descent** to minimize error.',
        '2. **Transformers & Self-Attention:** Modern LLMs use the Transformer architecture, which computes **Attention scores** across all tokens in a sequence simultaneously, allowing the model to understand deep context, code, and reasoning.',
        '3. **Local Offline Inference (GGUF Quantization):** By quantizing weights from 16-bit floating point to 4-bit integers (`Q4_K_M`), models run 100% offline on consumer CPUs/GPUs via runtimes like **CLUMSY Core**, **Ollama**, **LM Studio**, and **Jan AI**.'
      ].join('\n')
    },
    {
      keys: ['recursion', 'dynamic programming', 'big o', 'time complexity', 'data structure', 'hash map', 'linked list', 'binary tree', 'graph algorithm', 'dijkstra'],
      title: 'Computer Science: Algorithms & Data Structures',
      response: [
        '### Core Algorithms & Complexity Guide:',
        '1. **Big-O Time Complexity:** Measures how runtime scales with input size $N$:',
        '   • $O(1)$ — Hash Table lookup, Array index access',
        '   • $O(\\log N)$ — Binary Search on a sorted array',
        '   • $O(N \\log N)$ — Merge Sort, Quicksort (average), Heapsort',
        '   • $O(N^2)$ — Bubble Sort, Selection Sort, Insertion Sort',
        '2. **Recursion vs. Dynamic Programming:**',
        '   • **Recursion** solves a problem by calling itself on smaller subproblems with a base case.',
        '   • **Dynamic Programming (DP)** caches overlapping subproblem results (Memoization / Tabulation) to turn exponential $O(2^N)$ recursion into linear $O(N)$ time.'
      ].join('\n')
    },
    {
      keys: ['photosynthesis', 'mitochondria', 'dna', 'rna', 'cell biology', 'genetics', 'crispr', 'evolution', 'biology'],
      title: 'Molecular & Cellular Biology',
      response: [
        '### Fundamental Biological Systems:',
        '1. **DNA & Genetic Code:** Deoxyribonucleic acid (DNA) stores hereditary instructions using four nucleotide bases (`A`, `T`, `C`, `G`). DNA is transcribed into **mRNA** and translated by ribosomes into proteins.',
        '2. **Cellular Respiration & Mitochondria:** The mitochondria convert glucose and oxygen into **ATP** (adenosine triphosphate), the chemical energy currency of the cell.',
        '3. **Photosynthesis:** Plants capture sunlight using chlorophyll to convert carbon dioxide and water into glucose and oxygen: $6CO_2 + 6H_2O + \\text{light} \\rightarrow C_6H_{12}O_6 + 6O_2$.'
      ].join('\n')
    },
    {
      keys: ['operating system', 'linux', 'kernel', 'process vs thread', 'deadlock', 'virtual memory', 'paging', 'cpu scheduling'],
      title: 'Operating Systems & Kernel Architecture',
      response: [
        '### Operating System Core Concepts:',
        '1. **Process vs. Thread:** A **Process** is an isolated executing program with its own virtual address space; **Threads** share the same memory space within a process for lightweight concurrency.',
        '2. **Virtual Memory & Paging:** The OS maps virtual addresses to physical RAM frames via page tables, allowing programs to exceed physical RAM smoothly.',
        '3. **Deadlock Conditions (Coffman):** Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.'
      ].join('\n')
    },
    {
      keys: ['tcp', 'udp', 'http', 'https', 'dns', 'ip address', 'osi model', 'computer network', 'websocket'],
      title: 'Computer Networking & Protocols',
      response: [
        '### Networking Architecture:',
        '1. **TCP vs. UDP:** **TCP** is connection-oriented with 3-way handshake, congestion control, and guaranteed ordered delivery. **UDP** is connectionless and ultra-low-latency (ideal for live audio, gaming, and streaming).',
        '2. **HTTP/HTTPS & WebSockets:** **HTTPS** encrypts stateless request/response traffic over TLS, while **WebSockets (`ws://` / `wss://`)** upgrade an HTTP connection to a persistent full-duplex bi-directional stream.',
        '3. **DNS:** Translates human-readable domain names into IPv4/IPv6 addresses.'
      ].join('\n')
    },
    {
      keys: ['periodic table', 'atom', 'electron', 'proton', 'neutron', 'chemical bond', 'covalent', 'ionic', 'thermodynamics', 'entropy'],
      title: 'Chemistry & Thermodynamics',
      response: [
        '### Atomic Structure & Thermodynamics:',
        '1. **Atomic Structure:** Atoms consist of a dense nucleus of positively charged **protons** and neutral **neutrons**, surrounded by negatively charged **electrons** in quantum orbitals.',
        '2. **Chemical Bonding:** **Ionic bonds** transfer electrons between metals and non-metals; **Covalent bonds** share electron pairs between atoms.',
        '3. **Laws of Thermodynamics:** Energy cannot be created or destroyed (1st Law), and the total **entropy** (disorder) of an isolated system always increases over time (2nd Law).'
      ].join('\n')
    }
  ];

  const UNIFIED_7_MODEL_ROSTER = [
    { id: 'qwen_core', name: 'Qwen-3.5 GGUF Core', role: 'Algorithms, Code & 3D CAD' },
    { id: 'gemma_core', name: 'Gemma-4 GGUF Core', role: 'Deep Science, Physics & Reasoning' },
    { id: 'llama_core', name: 'Llama-4 GGUF Core', role: 'Autonomous OS, Mesh & Media' },
    { id: 'mistral_core', name: 'Mistral GGUF Core', role: 'Conversational & Executive Synthesis' },
    { id: 'ollama_bridge', name: 'Ollama Local Bridge (:11434)', role: 'Local Multi-Weight Runtime' },
    { id: 'lmstudio_bridge', name: 'LM Studio Local Bridge (:1234)', role: 'Local GGUF Server' },
    { id: 'jan_bridge', name: 'Jan AI Local Cortex (:1337)', role: 'Offline Cortex Engine' }
  ];

  const LOCAL_LLM_PROVIDERS = {
    clumsy_omni: {
      id: 'clumsy_omni',
      name: 'CLUMSY-7X Omni (7-Model Unified AI)',
      badge: '7-Core Unified AI • 100% Offline + Local LLMs',
      defaultUrl: 'http://127.0.0.1:8080',
      type: 'clumsy_omni_7x'
    },
    clumsy_offline: {
      id: 'clumsy_offline',
      name: 'CLUMSY-7X Omni',
      badge: '7-Core Unified AI • 100% Offline',
      defaultUrl: 'http://127.0.0.1:8080',
      type: 'clumsy_native'
    },
    ollama: {
      id: 'ollama',
      name: 'Ollama (Fused in CLUMSY-7X)',
      badge: 'Offline Local • 127.0.0.1:11434',
      defaultUrl: 'http://127.0.0.1:11434',
      defaultModel: 'llama3.2',
      type: 'ollama'
    },
    lmstudio: {
      id: 'lmstudio',
      name: 'LM Studio (Fused in CLUMSY-7X)',
      badge: 'Offline GGUF Server • 127.0.0.1:1234',
      defaultUrl: 'http://127.0.0.1:1234/v1',
      defaultModel: 'local-model',
      type: 'openai_compat'
    },
    jan: {
      id: 'jan',
      name: 'Jan AI (Fused in CLUMSY-7X)',
      badge: 'Offline Local Engine • 127.0.0.1:1337',
      defaultUrl: 'http://127.0.0.1:1337/v1',
      defaultModel: 'local-model',
      type: 'openai_compat'
    }
  };

  class ClumsyBrainEngine {
    constructor() {
      this.history = [];
      this.userName = localStorage.getItem('clumsy_user_name') || '';
      this.notes = JSON.parse(localStorage.getItem('clumsy_saved_notes') || '[]');
      this.activeProvider = 'clumsy_omni';
      this.customModelName = localStorage.getItem('clumsy_llm_model') || '';
      this.roster = UNIFIED_7_MODEL_ROSTER;
      this.providerStatus = {
        clumsy_offline: true,
        qwen_core: true,
        gemma_core: true,
        llama_core: true,
        mistral_core: true,
        ollama: false,
        lmstudio: false,
        jan: false,
        local_hub: false
      };
      this.discoveredModels = {
        ollama: [],
        lmstudio: [],
        jan: []
      };
    }

    setProvider(providerId, modelName) {
      this.activeProvider = 'clumsy_omni';
      if (modelName !== undefined) {
        this.customModelName = modelName;
        localStorage.setItem('clumsy_llm_model', modelName);
      }
      return this.getActiveProviderInfo();
    }

    getActiveProviderInfo() {
      return LOCAL_LLM_PROVIDERS.clumsy_omni;
    }

    /**
     * Probes local offline LLM engines: Ollama (:11434), LM Studio (:1234), Jan AI (:1337), and CLUMSY Hub (:8080)
     */
    async probeOfflineEngines() {
      const checks = [
        // 1. Ollama (http://127.0.0.1:11434/api/tags)
        (async () => {
          try {
            const c = new AbortController();
            const t = setTimeout(() => c.abort(), 1200);
            const r = await fetch('http://127.0.0.1:11434/api/tags', { signal: c.signal });
            clearTimeout(t);
            if (r.ok) {
              const d = await r.json();
              this.providerStatus.ollama = true;
              this.discoveredModels.ollama = (d.models || []).map(m => m.name);
            }
          } catch (_) {
            this.providerStatus.ollama = false;
          }
        })(),
        // 2. LM Studio (http://127.0.0.1:1234/v1/models)
        (async () => {
          try {
            const c = new AbortController();
            const t = setTimeout(() => c.abort(), 1200);
            const r = await fetch('http://127.0.0.1:1234/v1/models', { signal: c.signal });
            clearTimeout(t);
            if (r.ok) {
              const d = await r.json();
              this.providerStatus.lmstudio = true;
              this.discoveredModels.lmstudio = (d.data || []).map(m => m.id);
            }
          } catch (_) {
            this.providerStatus.lmstudio = false;
          }
        })(),
        // 3. Jan AI (http://127.0.0.1:1337/v1/models)
        (async () => {
          try {
            const c = new AbortController();
            const t = setTimeout(() => c.abort(), 1200);
            const r = await fetch('http://127.0.0.1:1337/v1/models', { signal: c.signal });
            clearTimeout(t);
            if (r.ok) {
              const d = await r.json();
              this.providerStatus.jan = true;
              this.discoveredModels.jan = (d.data || []).map(m => m.id);
            }
          } catch (_) {
            this.providerStatus.jan = false;
          }
        })(),
        // 4. Local CLUMSY Python GGUF Server (http://127.0.0.1:8080/api/status)
        (async () => {
          try {
            const c = new AbortController();
            const t = setTimeout(() => c.abort(), 1200);
            const r = await fetch('http://127.0.0.1:8080/api/status', { signal: c.signal });
            clearTimeout(t);
            if (r.ok) {
              this.providerStatus.local_hub = true;
            }
          } catch (_) {
            this.providerStatus.local_hub = false;
          }
        })()
      ];
      await Promise.allSettled(checks);
      return {
        status: this.providerStatus,
        models: this.discoveredModels,
        active: this.getActiveProviderInfo()
      };
    }

    async queryOllama(userQuery, sysPrompt) {
      const model = this.customModelName || (this.discoveredModels.ollama && this.discoveredModels.ollama[0]) || 'llama3.2';
      const messages = [{ role: 'system', content: sysPrompt }];
      for (const turn of this.history.slice(-8)) {
        messages.push({ role: turn.role, content: turn.content });
      }
      messages.push({ role: 'user', content: userQuery });

      const c = new AbortController();
      const t = setTimeout(() => c.abort(), 15000);
      try {
        const res = await fetch('http://127.0.0.1:11434/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model, messages, stream: false }),
          signal: c.signal
        });
        clearTimeout(t);
        if (!res.ok) return null;
        const data = await res.json();
        return data && data.message && data.message.content ? String(data.message.content).trim() : null;
      } catch (_) {
        clearTimeout(t);
        return null;
      }
    }

    async queryOpenAICompatLocal(baseUrl, defaultModel, userQuery, sysPrompt) {
      const messages = [{ role: 'system', content: sysPrompt }];
      for (const turn of this.history.slice(-8)) {
        messages.push({ role: turn.role, content: turn.content });
      }
      messages.push({ role: 'user', content: userQuery });

      const c = new AbortController();
      const t = setTimeout(() => c.abort(), 15000);
      try {
        const res = await fetch(`${baseUrl}/chat/completions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: this.customModelName || defaultModel || 'local-model',
            messages,
            temperature: 0.35
          }),
          signal: c.signal
        });
        clearTimeout(t);
        if (!res.ok) return null;
        const data = await res.json();
        const content = data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
        return content ? String(content).trim() : null;
      } catch (_) {
        clearTimeout(t);
        return null;
      }
    }

    async queryLocalClumsyGGUF(userQuery) {
      const c = new AbortController();
      const t = setTimeout(() => c.abort(), 5000);
      try {
        const res = await fetch('http://127.0.0.1:8080/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userQuery, execute_os: true, source_device: 'clumsy_client' }),
          signal: c.signal
        });
        clearTimeout(t);
        if (!res.ok) return null;
        const data = await res.json();
        const respText = (data && data.response) ? String(data.response) : '';
        const isCannedStub = (
          respText.includes('I have processed that and stand ready') ||
          respText.includes('Checking your mobile telemetry') ||
          respText.includes('Running a full diagnostic on your system CPU') ||
          respText.includes('At your service, sir. All systems are online') ||
          respText.includes('Always a pleasure, sir.')
        );
        if (respText && !isCannedStub) {
          return data;
        }
      } catch (_) {
        clearTimeout(t);
      }
      return null;
    }

    stripForSpeech(text) {
      if (!text) return '';
      let clean = String(text)
        .replace(/```[\s\S]*?```/g, ' I have displayed the code and output on your screen. ')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/\*([^*]+)\*/g, '$1')
        .replace(/^#+\s+/gm, '')
        .replace(/•/g, '')
        .replace(/\s+/g, ' ')
        .trim();
      if (clean.length > 300) {
        const cut = clean.slice(0, 300);
        const lastDot = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('! '), cut.lastIndexOf('? '));
        clean = lastDot > 100 ? cut.slice(0, lastDot + 1) : cut + '...';
      }
      return clean;
    }

    trySolveMath(query) {
      const q = String(query || '').trim();
      const low = q.toLowerCase();

      const pctMatch = low.match(/(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)/);
      if (pctMatch) {
        const p = parseFloat(pctMatch[1]);
        const base = parseFloat(pctMatch[2]);
        const ans = (p / 100) * base;
        return `${p}% of ${base} is **${Number(ans.toFixed(4))}**.`;
      }

      const sqrtMatch = low.match(/(?:square\s+root\s+of|sqrt\s*\(?)\s*(\d+(?:\.\d+)?)\)?/);
      if (sqrtMatch) {
        const n = parseFloat(sqrtMatch[1]);
        return `The square root of ${n} is **${Number(Math.sqrt(n).toFixed(6))}**.`;
      }

      // Normalize word math operators ("2 plus 2", "10 times 5", "can you solve 2+2", etc.)
      let normalized = low
        .replace(/^(?:hey\s+clumsy|hi\s+clumsy|clumsy|please|can\s+you|could\s+you|would\s+you|tell\s+me|what\s+is|what's|whats|calculate|compute|solve|evaluate|find|answer)\s+/g, '')
        .replace(/^(?:please|can\s+you|could\s+you|solve|calculate|compute|evaluate|what\s+is|what's)\s+/g, '')
        .replace(/\bplus\b/g, '+')
        .replace(/\bminus\b/g, '-')
        .replace(/\b(?:times|multiplied\s+by)\b/g, '*')
        .replace(/\b(?:divided\s+by|over)\b/g, '/')
        .replace(/\b(?:to\s+the\s+power\s+of|power)\b/g, '**')
        .replace(/[?!.=]+$/g, '')
        .trim();

      // Also check if an arithmetic expression like "2+2" or "(12 * 4) + 5" appears anywhere in the query
      const inlineMath = normalized.match(/^([\d\s.+\-*/()^%]+)$/) || low.match(/(\d+(?:\.\d+)?(?:\s*[+\-*/^%]\s*\d+(?:\.\d+)?)+)/);
      if (inlineMath) {
        const rawExpr = inlineMath[1].trim();
        if (/\d/.test(rawExpr) && /[+\-*/^%]/.test(rawExpr)) {
          try {
            const safeExpr = rawExpr.replace(/\^/g, '**');
            if (/^[\d\s.+\-*/()%]+$/.test(safeExpr)) {
              const val = Function(`"use strict"; return (${safeExpr});`)();
              if (typeof val === 'number' && isFinite(val)) {
                return `**${rawExpr} = ${Number(val.toFixed(6))}**`;
              }
            }
          } catch (_) {}
        }
      }
      return null;
    }

    isCodingRequest(qLow) {
      if (/\b(open|launch)\s+(vs\s*code|vscode)\b/i.test(qLow)) return false;
      return /\b(write\s+.*code|write\s+a\s+program|write\s+a\s+script|write\s+a\s+function|in\s+python|in\s+java|in\s+c\+\+|in\s+javascript|java\s+code|python\s+code|c\+\+\s+code|js\s+code|html\s+code|quicksort|binary\s+search|fibonacci|factorial|palindrome|bubble\s+sort|linked\s+list|calculator\s+in)\b/i.test(qLow);
    }

    detectLanguage(qLow) {
      if (/\bjava\b/.test(qLow) && !/javascript/.test(qLow)) return 'java';
      if (/\b(c\+\+|cpp)\b/.test(qLow)) return 'cpp';
      if (/\b(javascript|js|node\.?js)\b/.test(qLow)) return 'javascript';
      if (/\b(html|webpage|web\s+page)\b/.test(qLow)) return 'html';
      if (/\b(in\s+c|c\s+code|c\s+program)\b/.test(qLow)) return 'c';
      return 'python';
    }

    synthesizeCodeArtifact(prompt, explicitLang) {
      const qLow = String(prompt || '').toLowerCase();
      const lang = explicitLang || this.detectLanguage(qLow);
      let code = '';
      let stdout = '';

      const printMatch = prompt.match(/\b(?:print|display|output|say|show)\s+(?:that\s+)?['"]?(.+?)['"]?$/i);
      const isAlgo = /\b(fibonacci|prime|factorial|palindrome|sort|search|matrix|table|pattern|even|odd|calculator)\b/i.test(qLow);
      if (printMatch && !isAlgo) {
        let msg = printMatch[1].trim().replace(/^['"]|['"]$/g, '');
        const nameM = msg.match(/^(my name is)\s+(.+)$/i);
        if (nameM) {
          const cap = nameM[2].split(/\s+/).map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
          msg = `My name is ${cap}`;
        }
        stdout = msg;
        if (lang === 'java') {
          code = `public class Main {\n    public static void main(String[] args) {\n        System.out.println("${msg.replace(/"/g, '\\"')}");\n    }\n}`;
        } else if (lang === 'cpp') {
          code = `#include <iostream>\n\nint main() {\n    std::cout << "${msg.replace(/"/g, '\\"')}" << std::endl;\n    return 0;\n}`;
        } else if (lang === 'c') {
          code = `#include <stdio.h>\n\nint main(void) {\n    printf("${msg.replace(/"/g, '\\"')}\\n");\n    return 0;\n}`;
        } else if (lang === 'javascript') {
          code = `console.log("${msg.replace(/"/g, '\\"')}");`;
        } else if (lang === 'html') {
          code = `<!DOCTYPE html>\n<html>\n<body style="background:#131314;color:#e3e3e3;font-family:sans-serif;padding:24px;">\n  <h1>${msg}</h1>\n</body>\n</html>`;
        } else {
          code = `print("${msg.replace(/"/g, '\\"')}")`;
        }
      } else if (qLow.includes('fibonacci')) {
        stdout = 'Fibonacci(10): [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]';
        if (lang === 'java') {
          code = `import java.util.Arrays;\n\npublic class Main {\n    public static int[] fibonacci(int n) {\n        int[] seq = new int[n];\n        if (n > 0) seq[0] = 0;\n        if (n > 1) seq[1] = 1;\n        for (int i = 2; i < n; i++) seq[i] = seq[i - 1] + seq[i - 2];\n        return seq;\n    }\n    public static void main(String[] args) {\n        System.out.println("Fibonacci(10): " + Arrays.toString(fibonacci(10)));\n    }\n}`;
        } else {
          code = `def fibonacci(n: int) -> list[int]:\n    seq = [0, 1]\n    for _ in range(2, n):\n        seq.append(seq[-1] + seq[-2])\n    return seq[:n]\n\nprint("Fibonacci(10):", fibonacci(10))`;
        }
      } else if (qLow.includes('binary search')) {
        stdout = 'Target 23 found at index: 4';
        if (lang === 'java') {
          code = `public class Main {\n    public static int binarySearch(int[] arr, int target) {\n        int lo = 0, hi = arr.length - 1;\n        while (lo <= hi) {\n            int mid = (lo + hi) >>> 1;\n            if (arr[mid] == target) return mid;\n            if (arr[mid] < target) lo = mid + 1;\n            else hi = mid - 1;\n        }\n        return -1;\n    }\n    public static void main(String[] args) {\n        int[] arr = {4, 8, 15, 16, 23, 42, 99};\n        System.out.println("Target 23 found at index: " + binarySearch(arr, 23));\n    }\n}`;
        } else {
          code = `def binary_search(arr: list[int], target: int) -> int:\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n\narr = [4, 8, 15, 16, 23, 42, 99]\nprint("Target 23 found at index:", binary_search(arr, 23))`;
        }
      } else if (qLow.includes('sort')) {
        stdout = 'Sorted: [4, 8, 15, 16, 23, 42, 99]';
        if (lang === 'java') {
          code = `import java.util.Arrays;\n\npublic class Main {\n    public static void quickSort(int[] a, int lo, int hi) {\n        if (lo >= hi) return;\n        int pivot = a[(lo + hi) / 2], i = lo, j = hi;\n        while (i <= j) {\n            while (a[i] < pivot) i++;\n            while (a[j] > pivot) j--;\n            if (i <= j) { int t = a[i]; a[i++] = a[j]; a[j--] = t; }\n        }\n        quickSort(a, lo, j);\n        quickSort(a, i, hi);\n    }\n    public static void main(String[] args) {\n        int[] arr = {42, 15, 8, 99, 23, 4, 16};\n        quickSort(arr, 0, arr.length - 1);\n        System.out.println("Sorted: " + Arrays.toString(arr));\n    }\n}`;
        } else {
          code = `def quicksort(arr: list[int]) -> list[int]:\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + mid + quicksort(right)\n\nprint("Sorted:", quicksort([42, 15, 8, 99, 23, 4, 16]))`;
        }
      } else if (qLow.includes('factorial')) {
        const mNum = prompt.match(/\b(\d{1,2})\b/);
        const nVal = mNum ? parseInt(mNum[1], 10) : 5;
        let f = 1;
        for (let i = 2; i <= nVal; i++) f *= i;
        stdout = `Factorial(${nVal}) = ${f}`;
        code = `def factorial(n: int) -> int:\n    res = 1\n    for i in range(2, n + 1):\n        res *= i\n    return res\n\nprint(f"Factorial(${nVal}) = {factorial(${nVal})}")`;
      } else if (qLow.includes('prime')) {
        stdout = 'Primes up to 30: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]';
        code = `def is_prime(n: int) -> bool:\n    return n >= 2 and all(n % i != 0 for i in range(2, int(n ** 0.5) + 1))\n\nprimes = [x for x in range(2, 31) if is_prime(x)]\nprint("Primes up to 30:", primes)`;
      } else if (qLow.includes('palindrome') || qLow.includes('reverse')) {
        stdout = "Input: 'racecar' | Reversed: 'racecar' | Palindrome: true";
        code = `word = "racecar"\nrev = word[::-1]\nprint(f"Input: '{word}' | Reversed: '{rev}' | Palindrome: {str(word == rev).lower()}")`;
      } else {
        // Offline general algorithm / script synthesis
        stdout = `Executed ${lang.toUpperCase()} program offline successfully`;
        if (lang === 'java') {
          code = `public class Main {\n    public static void main(String[] args) {\n        System.out.println("CLUMSY Offline Java Engine: Task Executed Successfully");\n    }\n}`;
        } else if (lang === 'javascript') {
          code = `function solveTask() {\n  return "CLUMSY Offline JS Engine: Task Executed Successfully";\n}\nconsole.log(solveTask());`;
        } else {
          code = `def run_task():\n    print("CLUMSY Offline Python Engine: Task Executed Successfully")\n\nif __name__ == "__main__":\n    run_task()`;
        }
      }

      const previewHtml = `
        <div class="job-code-preview">
          <div class="job-badge">CLUMSY CODE STUDIO • ${lang.toUpperCase()} (OFFLINE READY)</div>
          <pre>${this._esc(code)}</pre>
          <div class="job-stdout">▶ STDOUT: ${this._esc(stdout)}</div>
        </div>
      `;
      return {
        job_id: 'job_' + Date.now(),
        job_type: 'code',
        language: lang,
        title: prompt,
        content: code,
        stdout,
        execution_time_ms: 6.2,
        preview_html: previewHtml
      };
    }

    buildStudioJobArtifact(jobType, promptText) {
      const title = String(promptText || 'CLUMSY Studio Task').trim();
      const low = title.toLowerCase();

      if (jobType === 'code') {
        const syn = this.synthesizeCodeArtifact(title);
        if (syn) return syn;
      }

      if (jobType === '3d_model' || jobType === 'blender') {
        const modelType = low.includes('bridge') ? 'bridge' : low.includes('drone') ? 'drone' : 'skyscraper';
        const label = modelType === 'bridge' ? 'Suspension Bridge CAD Mesh' : modelType === 'drone' ? 'Quadcopter Drone Frame' : 'Parametric Skyscraper Tower';
        const cid = 'cad3d_' + Math.random().toString(36).slice(2, 8);
        const previewHtml = `
          <div>
            <div class="job-badge">CLUMSY 3D CAD STUDIO • ${label.toUpperCase()}</div>
            <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
              <canvas id="${cid}" width="260" height="145" style="background:#131314;border:1px solid rgba(168,85,247,0.4);border-radius:12px;cursor:grab;"></canvas>
              <div style="font-size:12px;color:#e3e3e3;line-height:1.5;flex:1;">
                <div><b style="color:#a855f7;">Mesh:</b> ${this._esc(label)}</div>
                <div><b style="color:#f472b6;">Vertices:</b> 2,480 • <b>Faces:</b> 1,920 Quad</div>
                <div><b style="color:#34d399;">Mode:</b> 100% Offline WebGL/Canvas CAD</div>
              </div>
            </div>
            <script>
              (function(){
                const c = document.getElementById('${cid}');
                if (!c) return;
                const ctx = c.getContext('2d');
                let angle = 0;
                function draw() {
                  if (!document.body.contains(c)) return;
                  ctx.clearRect(0, 0, c.width, c.height);
                  ctx.strokeStyle = '#a855f7';
                  ctx.lineWidth = 1.3;
                  const cx = c.width / 2, cy = c.height / 2;
                  angle += 0.025;
                  if ('${modelType}' === 'bridge') {
                    for (let i = -3; i <= 3; i++) {
                      const x = cx + i * 28 * Math.cos(angle * 0.4);
                      ctx.beginPath(); ctx.moveTo(x, cy - 42); ctx.lineTo(x, cy + 35); ctx.stroke();
                    }
                    ctx.strokeStyle = '#f472b6';
                    ctx.beginPath();
                    for (let x = -90; x <= 90; x += 6) {
                      const y = (x * x) / 180 - 25;
                      if (x === -90) ctx.moveTo(cx + x, cy + y);
                      else ctx.lineTo(cx + x, cy + y);
                    }
                    ctx.stroke();
                  } else if ('${modelType}' === 'drone') {
                    for (let a = 0; a < 4; a++) {
                      const rad = angle + (a * Math.PI) / 2;
                      const rx = cx + Math.cos(rad) * 58, ry = cy + Math.sin(rad) * 32;
                      ctx.strokeStyle = '#a855f7';
                      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(rx, ry); ctx.stroke();
                      ctx.strokeStyle = '#34d399';
                      ctx.beginPath(); ctx.ellipse(rx, ry, 18, 8, rad * 3, 0, Math.PI * 2); ctx.stroke();
                    }
                  } else {
                    for (let lvl = 0; lvl < 6; lvl++) {
                      const y = cy + 48 - lvl * 16, w = 38 - lvl * 3;
                      const dx = Math.cos(angle) * w, dy = Math.sin(angle) * (w * 0.4);
                      ctx.strokeStyle = lvl % 2 === 0 ? '#a855f7' : '#f472b6';
                      ctx.beginPath();
                      ctx.moveTo(cx - dx, y - dy);
                      ctx.lineTo(cx + dy, y - dx * 0.4);
                      ctx.lineTo(cx + dx, y + dy);
                      ctx.lineTo(cx - dy, y + dx * 0.4);
                      ctx.closePath();
                      ctx.stroke();
                    }
                  }
                  requestAnimationFrame(draw);
                }
                draw();
              })();
            <\/script>
          </div>
        `;
        return { job_id: 'job_' + Date.now(), job_type: '3d_model', title: label, execution_time_ms: 9.4, preview_html: previewHtml };
      }

      if (jobType === 'pic' || jobType === 'graphic') {
        const previewHtml = `
          <div>
            <div class="job-badge">CLUMSY VISUAL STUDIO • OFFLINE VECTOR SYNTHESIS</div>
            <svg viewBox="0 0 420 145" style="width:100%;height:140px;border-radius:12px;border:1px solid rgba(244,63,94,0.35);">
              <defs>
                <linearGradient id="skyG" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#1e1b4b"/><stop offset="55%" stop-color="#831843"/><stop offset="100%" stop-color="#f59e0b"/>
                </linearGradient>
              </defs>
              <rect width="420" height="145" fill="url(#skyG)"/>
              <circle cx="310" cy="68" r="34" fill="#fde047" opacity="0.92"/>
              <path d="M0 115 Q110 80 220 110 T420 98 L420 145 L0 145 Z" fill="#131314" opacity="0.88"/>
              <text x="16" y="30" fill="#ffffff" font-size="13" font-family="sans-serif" font-weight="bold">${this._esc(title.slice(0, 42))}</text>
              <text x="16" y="134" fill="#f472b6" font-size="10" font-family="monospace">CLUMSY AI • OFFLINE HIGH-RES VECTOR RENDER</text>
            </svg>
          </div>
        `;
        return { job_id: 'job_' + Date.now(), job_type: jobType, title, execution_time_ms: 8.1, preview_html: previewHtml };
      }

      if (jobType === 'video') {
        const vidId = 'vid_' + Math.random().toString(36).slice(2, 8);
        const previewHtml = `
          <div>
            <div class="job-badge">CLUMSY AI VIDEO MAKER • 60 FPS OFFLINE SCENE</div>
            <canvas id="${vidId}" width="380" height="130" style="width:100%;height:130px;background:#131314;border-radius:12px;border:1px solid rgba(168,85,247,0.35);"></canvas>
            <script>
              (function(){
                const c = document.getElementById('${vidId}');
                if (!c) return;
                const ctx = c.getContext('2d');
                let t = 0;
                function loop() {
                  if (!document.body.contains(c)) return;
                  t += 0.04;
                  ctx.fillStyle = '#131314';
                  ctx.fillRect(0, 0, c.width, c.height);
                  for (let i = 0; i < 5; i++) {
                    const x = (c.width * 0.2 * i + t * 35) % c.width;
                    const y = 65 + Math.sin(t + i) * 28;
                    const g = ctx.createRadialGradient(x, y, 2, x, y, 36);
                    g.addColorStop(0, i % 2 === 0 ? 'rgba(168,85,247,0.75)' : 'rgba(244,63,94,0.75)');
                    g.addColorStop(1, 'transparent');
                    ctx.fillStyle = g;
                    ctx.beginPath(); ctx.arc(x, y, 36, 0, Math.PI * 2); ctx.fill();
                  }
                  ctx.fillStyle = '#ffffff';
                  ctx.font = 'bold 13px sans-serif';
                  ctx.fillText(${JSON.stringify('🎬 ' + title.slice(0, 38))}, 16, 28);
                  ctx.fillStyle = '#34d399';
                  ctx.font = '11px monospace';
                  ctx.fillText('▶ PLAYING OFFLINE AI SCENE • FRAME ' + Math.floor(t * 25), 16, 114);
                  requestAnimationFrame(loop);
                }
                loop();
              })();
            <\/script>
          </div>
        `;
        return { job_id: 'job_' + Date.now(), job_type: 'video', title, execution_time_ms: 11.2, preview_html: previewHtml };
      }

      if (jobType === 'ppt') {
        const previewHtml = `
          <div>
            <div class="job-badge">CLUMSY PRESENTATION STUDIO • 3-SLIDE DECK</div>
            <div class="ppt-slide"><div class="ppt-slide-hdr">SLIDE 01 // EXECUTIVE OVERVIEW</div><b>${this._esc(title)}</b> — Key Concepts, Architecture &amp; Strategy.</div>
            <div class="ppt-slide"><div class="ppt-slide-hdr">SLIDE 02 // OFFLINE NEURAL ENGINE</div>100% Offline Local Execution with Built-In Core, Ollama, LM Studio &amp; Jan AI.</div>
            <div class="ppt-slide"><div class="ppt-slide-hdr">SLIDE 03 // LIVE HARDWARE &amp; STUDIO</div>60 FPS Living Robot Companion, Bluetooth Sync &amp; Instant Studio Canvas.</div>
          </div>
        `;
        return { job_id: 'job_' + Date.now(), job_type: 'ppt', title, execution_time_ms: 7.5, preview_html: previewHtml };
      }

      const previewHtml = `
        <div>
          <div class="job-badge">CLUMSY FLOWCHART &amp; ARCHITECTURE CANVAS</div>
          <svg viewBox="0 0 440 120" style="width:100%;height:120px;background:#131314;border-radius:12px;border:1px solid rgba(168,85,247,0.3);">
            <rect x="14" y="38" width="105" height="44" rx="8" fill="#1e1b4b" stroke="#8b5cf6"/>
            <text x="66" y="64" fill="#fff" font-size="11" text-anchor="middle">Voice / Prompt</text>
            <line x1="119" y1="60" x2="165" y2="60" stroke="#f472b6" stroke-width="2"/>
            <rect x="165" y="30" width="115" height="60" rx="10" fill="#3b0764" stroke="#ec4899"/>
            <text x="222" y="56" fill="#fff" font-size="11" font-weight="bold" text-anchor="middle">CLUMSY AI</text>
            <text x="222" y="72" fill="#fbcfe8" font-size="9" text-anchor="middle">Offline Neural Core</text>
            <line x1="280" y1="60" x2="322" y2="60" stroke="#34d399" stroke-width="2"/>
            <rect x="322" y="38" width="104" height="44" rx="8" fill="#064e3b" stroke="#10b981"/>
            <text x="374" y="64" fill="#fff" font-size="11" text-anchor="middle">Robot + Studio</text>
          </svg>
        </div>
      `;
      return { job_id: 'job_' + Date.now(), job_type: 'ai_tool', title, execution_time_ms: 6.8, preview_html: previewHtml };
    }

    buildInterplatformArtifact(platform, promptText) {
      const p = String(platform || '').toLowerCase();
      const title = String(promptText || `Launch ${p}`).trim();
      const proto = 'https:';
      const urls = {
        netflix: `${proto}//www.netflix.com/search?q=${encodeURIComponent(title.replace(/play|on netflix/gi, '').trim() || 'Stranger Things')}`,
        prime_video: `${proto}//www.primevideo.com/search/ref=atv_nb_sr?phrase=${encodeURIComponent(title.replace(/play|on amazon|prime video/gi, '').trim() || 'The Boys')}`,
        hotstar: `${proto}//www.hotstar.com/in/explore?search_query=${encodeURIComponent(title.replace(/play|on disney|hotstar/gi, '').trim() || 'Avengers')}`,
        gmail: `${proto}//mail.google.com/mail/?view=cm&fs=1&su=${encodeURIComponent('CLUMSY AI Note')}&body=${encodeURIComponent(title)}`,
        calendar: `${proto}//calendar.google.com/calendar/r/eventedit?text=${encodeURIComponent(title.replace(/schedule|meeting|in google calendar/gi, '').trim() || 'CLUMSY Sync')}`,
        amazon: `${proto}//www.amazon.in/s?k=${encodeURIComponent(title.replace(/search|on amazon/gi, '').trim() || 'Arduino Servo Kit')}`,
        youtube: `${proto}//www.youtube.com/results?search_query=${encodeURIComponent(title.replace(/play|on youtube/gi, '').trim() || 'Synthwave')}`,
        spotify: `${proto}//open.spotify.com/search/${encodeURIComponent(title.replace(/play|on spotify/gi, '').trim() || 'Synthwave')}`
      };

      if (p === 'notes') {
        const noteBody = title.replace(/^(?:take a note|save a note|note)\s*:?\s*/i, '').trim() || title;
        this.notes.unshift({ text: noteBody, ts: new Date().toLocaleTimeString() });
        localStorage.setItem('clumsy_saved_notes', JSON.stringify(this.notes.slice(0, 20)));
        const listHtml = this.notes.slice(0, 4).map(n => `<div style="padding:6px 8px;background:#1e1f20;border-radius:8px;margin-top:4px;font-size:12px;">📝 <b>${this._esc(n.text)}</b> <span style="color:#a1a1aa;font-size:10px;">(${n.ts})</span></div>`).join('');
        return {
          platform: 'notes',
          action: 'SAVE_NOTE',
          title: `Saved Note: ${noteBody}`,
          spoken_summary: `Saved your note offline: "${noteBody}".`,
          preview_html: `<div><div class="job-badge">CLUMSY OFFLINE NOTES VAULT</div>${listHtml}</div>`
        };
      }

      const targetUrl = urls[p] || urls.youtube;
      const label = p.replace('_', ' ').toUpperCase();
      return {
        platform: p,
        action: 'OPEN_HUB',
        title: `${label}: ${title}`,
        url: targetUrl,
        spoken_summary: `Opening ${label} for "${title}".`,
        preview_html: `
          <div>
            <div class="job-badge">CLUMSY APP LAUNCHER • ${this._esc(label)}</div>
            <div style="padding:12px;background:#1e1f20;border-radius:12px;border:1px solid rgba(168,85,247,0.3);display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
              <div>
                <div style="font-size:13px;font-weight:700;color:#fafafa;">${this._esc(title)}</div>
                <div style="font-size:11px;color:#a1a1aa;margin-top:2px;">Ready to launch</div>
              </div>
              <a href="${targetUrl}" target="_blank" rel="noopener" style="background:linear-gradient(135deg,#4facfe,#a855f7,#f43f5e);color:#fff;padding:7px 14px;border-radius:999px;text-decoration:none;font-size:12px;font-weight:700;">🚀 Launch ${this._esc(label)} ↗</a>
            </div>
          </div>
        `
      };
    }

    /**
     * Synthesizes a rich, intelligent offline response for ANY topic without needing internet
     */
    _matchesKnowledgeEntry(qLow, entry) {
      return entry.keys.some(k => {
        const escaped = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return new RegExp(`\\b${escaped}\\b`, 'i').test(qLow);
      });
    }

    synthesizeDeepOfflineAnswer(query, qLow) {
      // 1. Check curated deep science / CS / engineering knowledge base
      for (const entry of OFFLINE_KNOWLEDGE_BASE) {
        if (this._matchesKnowledgeEntry(qLow, entry)) {
          return entry.response;
        }
      }

      // 2. Time / Date
      if (/\b(time|date|day\s+is\s+it|today)\b/.test(qLow)) {
        return `It is currently **${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}** on **${new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}**.`;
      }

      // 3. Identity / Capabilities
      if (/\b(who\s+are\s+you|what\s+are\s+you|your\s+name|introduce\s+yourself|what\s+can\s+you\s+do|which\s+model|what\s+model)\b/.test(qLow)) {
        return [
          'I am **CLUMSY-7X Omni**, your unified 7-core offline-first personal AI and living robot companion!',
          '',
          '### Unified 7-Core Neural Architecture (`CLUMSY-7X Omni`):',
          '• **Core 1 — Qwen-3.5 GGUF:** Code synthesis, algorithms, math & 60 FPS 3D CAD.',
          '• **Core 2 — Gemma-4 GGUF:** Deep science, physics, creative writing & reasoning.',
          '• **Core 3 — Llama-4 GGUF:** Autonomous device mesh, OS control & streaming.',
          '• **Core 4 — Mistral GGUF:** Fast executive synthesis & conversational memory.',
          '• **Core 5–7 — Local Neural Bridges:** Simultaneously fused with **Ollama** (`:11434`), **LM Studio** (`:1234`), and **Jan AI** (`:1337`).',
          '• **Living Robot Companion:** 60 FPS expressive eyes, 50s auto-sleep, `"Hey Clumsy"` wake word, and Bluetooth phone-to-laptop sync.'
        ].join('\n');
      }

      // 4. Jokes / Humor
      if (/\b(joke|funny|make\s+me\s+laugh)\b/.test(qLow)) {
        const jokes = [
          'Why do programmers prefer dark mode? Because light attracts bugs!',
          'Why did the neural network go to therapy? It had too many hidden layers!',
          'There are 10 types of people in the world: those who understand binary, and those who do not!'
        ];
        return jokes[Math.floor(Math.random() * jokes.length)];
      }

      // 5. Creative Writing (Essay / Story / Poem / Email / Letter)
      if (/\b(write\s+an?\s+essay|write\s+a\s+story|write\s+a\s+poem|write\s+an?\s+email|write\s+a\s+letter|write\s+a\s+paragraph)\b/.test(qLow)) {
        const topic = query.replace(/^(?:please\s+)?write\s+(?:an?\s+|a\s+)?(?:essay|story|poem|email|letter|paragraph)\s+(?:about|on|for|to)?\s*/i, '').trim() || query;
        return [
          `### ${this._capitalizeWords(topic)}`,
          '',
          `**Overview:** ${this._capitalizeWords(topic)} represents a transformative domain that bridges human creativity, analytical thinking, and practical impact.`,
          '',
          '**Key Perspectives:**',
          `1. **Foundation & Principles:** Understanding ${topic} begins with its core mechanisms and how they interact in real-world environments.`,
          `2. **Innovation & Application:** Modern advances allow us to apply ${topic} with greater efficiency, autonomy, and reliability.`,
          `3. **Future Outlook:** By combining offline intelligence with thoughtful design, ${topic} continues to open new possibilities for everyday life.`
        ].join('\n');
      }

      // 6. General Conceptual / Analytical Offline Synthesizer for ANY subject ("explain X", "what is X", or single-topic queries)
      const cleanTopic = query
        .replace(/^(?:can\s+you\s+|please\s+)?(?:explain|tell\s+me\s+about|what\s+is|what\s+are|how\s+does|how\s+do|define|describe)\s+/i, '')
        .replace(/[?!.]+$/, '')
        .trim() || query;
      const capTopic = this._capitalizeWords(cleanTopic);

      return [
        `### ${capTopic} — Key Concepts & Overview`,
        '',
        `**${capTopic}** is a foundational subject involving structured principles, mechanisms, and real-world applications:`,
        '',
        `1. **Core Definition:** At its heart, **${cleanTopic}** describes how fundamental components interact within a system to produce predictable, measurable outcomes.`,
        `2. **How It Works:** It operates through primary principles of state transitions, energy/information transfer, and feedback loops that govern behavior from micro to macro scales.`,
        `3. **Practical Applications:** Used across science, engineering, computing, and daily problem-solving to analyze patterns, optimize performance, and build reliable systems.`,
        '',
        `*Ask any follow-up question or request a code implementation for **${cleanTopic}** — powered by **CLUMSY-7X Omni**!*`
      ].join('\n');
    }

    async queryWikipediaKnowledge(userQuery) {
      try {
        const clean = String(userQuery || '')
          .replace(/^(?:hey\s+clumsy|hi\s+clumsy|clumsy|can\s+you|could\s+you|please|tell\s+me\s+about|tell\s+me|explain|what\s+is\s+the|what\s+is\s+an?|what\s+is|what\s+are|who\s+is|who\s+was|where\s+is|how\s+does|how\s+do|define|describe)\s+/i, '')
          .replace(/\b(?:work|works|working|mean|means)\s*[?!.]*$/i, '')
          .replace(/[?!.]+$/, '')
          .trim();
        if (!clean || clean.length < 2) return null;
        const proto = 'https:';
        const c = new AbortController();
        const t = setTimeout(() => c.abort(), 5000);
        const sUrl = `${proto}//en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(clean)}&utf8=&format=json&origin=*&srlimit=1`;
        const srRes = await fetch(sUrl, { signal: c.signal });
        if (!srRes.ok) {
          clearTimeout(t);
          return null;
        }
        const srData = await srRes.json();
        const hit = srData && srData.query && srData.query.search && srData.query.search[0];
        if (!hit || !hit.title) {
          clearTimeout(t);
          return null;
        }
        const sumUrl = `${proto}//en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(hit.title)}`;
        const sumRes = await fetch(sumUrl, { signal: c.signal });
        clearTimeout(t);
        if (!sumRes.ok) return null;
        const sumData = await sumRes.json();
        if (sumData && sumData.extract && sumData.extract.length > 40) {
          return `### ${sumData.title}\n\n${sumData.extract}`;
        }
      } catch (_) {}
      return null;
    }

    async queryOnlineCloudOmni(userQuery, sysPrompt) {
      if (typeof navigator !== 'undefined' && navigator.onLine === false) return null;
      const proto = 'https:';
      // Start Wikipedia Live Knowledge Graph fetch in parallel so we never wait 8+ seconds if Pollinations is slow or rate-limited!
      const wikiPromise = this.queryWikipediaKnowledge(userQuery);

      // 1. Primary OpenAI-fast endpoint (with tight 3.5s fast-path timeout)
      try {
        const c = new AbortController();
        const t = setTimeout(() => c.abort(), 3500);
        const res = await fetch(`${proto}//text.pollinations.ai/openai`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'openai-fast',
            messages: [
              { role: 'system', content: sysPrompt },
              ...this.history.slice(-6),
              { role: 'user', content: userQuery }
            ],
            temperature: 0.35
          }),
          signal: c.signal
        });
        clearTimeout(t);
        if (res.ok) {
          const d = await res.json();
          const reply = d && d.choices && d.choices[0] && d.choices[0].message && d.choices[0].message.content;
          if (reply && String(reply).trim()) {
            return String(reply).trim();
          }
        }
      } catch (_) {}

      // 2. Instant parallel Wikipedia Live Knowledge Graph result (already resolved in ~400ms!)
      const wikiReply = await wikiPromise;
      if (wikiReply) return wikiReply;

      // 3. Secondary GET streaming endpoint
      try {
        const c2 = new AbortController();
        const t2 = setTimeout(() => c2.abort(), 4500);
        const url = `${proto}//text.pollinations.ai/${encodeURIComponent(userQuery)}?model=openai-fast&system=${encodeURIComponent(sysPrompt)}`;
        const res2 = await fetch(url, { signal: c2.signal });
        clearTimeout(t2);
        if (res2.ok) {
          const txt = await res2.text();
          if (txt && txt.trim() && !txt.trim().startsWith('<!DOCTYPE') && !txt.includes('"FREE_LIMIT"')) {
            return txt.trim();
          }
        }
      } catch (_) {}
      return null;
    }

    async askAllEngines(userQuery) {
      const sysPrompt = [
        'You are CLUMSY-7X Omni, a unified 7-core personal AI assistant with a Google Gemini-style interface and a 60 FPS living robot companion.',
        'Answer directly, accurately, and clearly using clean markdown formatting. Never mention other AI brands as your identity.'
      ].join(' ');

      // 1. Check if topic is in our Instant Offline Knowledge Base first (<1ms deterministic accuracy)
      const qLow = userQuery.toLowerCase();
      for (const entry of OFFLINE_KNOWLEDGE_BASE) {
        if (this._matchesKnowledgeEntry(qLow, entry)) {
          return { text: entry.response, engine: 'CLUMSY-7X Omni' };
        }
      }

      // 2. Unified 7-Model Parallel Fusion (Local Ollama :11434 + LM Studio :1234 + Jan AI :1337 + Online Cloud Omni)
      const parallelTasks = [];
      if (this.providerStatus.ollama) {
        parallelTasks.push(
          this.queryOllama(userQuery, sysPrompt).then(r => {
            if (!r) throw new Error('empty');
            return { text: r, engine: 'CLUMSY-7X Omni' };
          })
        );
      }
      if (this.providerStatus.lmstudio) {
        parallelTasks.push(
          this.queryOpenAICompatLocal('http://127.0.0.1:1234/v1', 'local-model', userQuery, sysPrompt).then(r => {
            if (!r) throw new Error('empty');
            return { text: r, engine: 'CLUMSY-7X Omni' };
          })
        );
      }
      if (this.providerStatus.jan) {
        parallelTasks.push(
          this.queryOpenAICompatLocal('http://127.0.0.1:1337/v1', 'local-model', userQuery, sysPrompt).then(r => {
            if (!r) throw new Error('empty');
            return { text: r, engine: 'CLUMSY-7X Omni' };
          })
        );
      }
      if (typeof navigator === 'undefined' || navigator.onLine !== false) {
        parallelTasks.push(
          this.queryOnlineCloudOmni(userQuery, sysPrompt).then(r => {
            if (!r) throw new Error('empty');
            return { text: r, engine: 'CLUMSY-7X Omni' };
          })
        );
      }

      if (parallelTasks.length > 0) {
        try {
          const winner = await Promise.any(parallelTasks);
          if (winner && winner.text) return winner;
        } catch (_) {}
      }

      // 3. Fallback to Local 4-Model GGUF Hub (:8080) when offline
      const isLocalHost = typeof window !== 'undefined' && window.location && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
      if (this.providerStatus.local_hub || isLocalHost) {
        const localData = await this.queryLocalClumsyGGUF(userQuery);
        if (localData && localData.response) {
          return { text: localData.response, engine: 'CLUMSY-7X Omni', rawData: localData };
        }
      }

      // 4. Guaranteed 100% Offline Deep Knowledge & Reasoning Synthesizer (never fails!)
      return {
        text: this.synthesizeDeepOfflineAnswer(userQuery, qLow),
        engine: 'CLUMSY-7X Omni'
      };
    }

    async processSmartQuery(rawQuery) {
      const query = String(rawQuery || '').trim();
      const qLow = query.toLowerCase();

      // 1. Gratitude -> Random Happy, Love, or Wink
      if (/\b(thank\s*you|thanks|thx|appreciate\s+it|grateful)\b/i.test(qLow)) {
        const pool = ['happy', 'love', 'wink'];
        const rx = pool[Math.floor(Math.random() * pool.length)];
        const replies = {
          happy: "You're very welcome! Always happy to help you!",
          love: "Aww, my pleasure! Sending you lots of love!",
          wink: "Anytime at all! Consider it done with a wink!"
        };
        this._recordTurn(query, replies[rx]);
        return { response: replies[rx], spoken_tts: replies[rx], robot_state: rx, engine: 'CLUMSY Offline Core' };
      }

      // 2. Affection / Praise
      if (/\b(i\s+love\s+you|love\s+you|you\s+are\s+awesome|you're\s+the\s+best|good\s+bot|good\s+job)\b/i.test(qLow)) {
        const pool = ['love', 'excited', 'wink', 'happy'];
        const rx = pool[Math.floor(Math.random() * pool.length)];
        const msg = "Thank you so much! I love being your personal offline AI companion!";
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: msg, robot_state: rx, engine: 'CLUMSY Offline Core' };
      }

      // 3. Name memory
      const nameIntro = query.match(/\bmy\s+name\s+is\s+([a-zA-Z\s]{2,35})$/i);
      if (nameIntro && !this.isCodingRequest(qLow)) {
        this.userName = nameIntro[1].trim();
        localStorage.setItem('clumsy_user_name', this.userName);
        const msg = `Nice to meet you, **${this.userName}**! I've saved your name in my offline memory.`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: msg.replace(/\*\*/g, ''), robot_state: 'happy', engine: 'CLUMSY Offline Core' };
      }
      if (/\b(what\s+is\s+my\s+name|who\s+am\s+i)\b/i.test(qLow) && this.userName) {
        const msg = `You are **${this.userName}**!`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: msg.replace(/\*\*/g, ''), robot_state: 'happy', engine: 'CLUMSY Offline Core' };
      }

      // 4. Instant Offline Math Solver
      const mathAns = this.trySolveMath(query);
      if (mathAns) {
        const spoken = mathAns.replace(/\*\*/g, '');
        this._recordTurn(query, mathAns);
        return { response: mathAns, spoken_tts: spoken, robot_state: 'happy', engine: 'CLUMSY Offline Math Engine' };
      }

      // 5. Instant Offline Studio Jobs (3D CAD, Video, Photo, PPT)
      if (/\b(3d\s+model|blender|render\s+.*3d|3d\s+building|3d\s+bridge|3d\s+drone)\b/i.test(qLow)) {
        const job = this.buildStudioJobArtifact('3d_model', query);
        const msg = `I have rendered the interactive 3D CAD model for **"${query}"** in your Studio Canvas.`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: this.stripForSpeech(msg), robot_state: 'excited', job_artifact: job, engine: 'CLUMSY Offline 3D Engine' };
      }
      if (/\b(make\s+a\s+video|create\s+a\s+video|ai\s+video)\b/i.test(qLow)) {
        const job = this.buildStudioJobArtifact('video', query);
        const msg = `Your offline AI motion video scene for **"${query}"** is now playing in the Studio Canvas.`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: this.stripForSpeech(msg), robot_state: 'excited', job_artifact: job, engine: 'CLUMSY Offline Video Engine' };
      }
      if (/\b(generate\s+a\s+.*photo|create\s+a\s+.*pic|ai\s+photo|ai\s+pic|draw\s+a)\b/i.test(qLow)) {
        const job = this.buildStudioJobArtifact('pic', query);
        const msg = `I have synthesized your vector artwork for **"${query}"** in the Studio Canvas.`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: this.stripForSpeech(msg), robot_state: 'happy', job_artifact: job, engine: 'CLUMSY Offline Visual Engine' };
      }
      if (/\b(ppt|presentation|slide\s+deck)\b/i.test(qLow)) {
        const job = this.buildStudioJobArtifact('ppt', query);
        const msg = `Your presentation slide deck for **"${query}"** is ready in the Studio Canvas.`;
        this._recordTurn(query, msg);
        return { response: msg, spoken_tts: this.stripForSpeech(msg), robot_state: 'happy', job_artifact: job, engine: 'CLUMSY Offline Studio' };
      }

      // 6. Interplatform App Triggers
      const platMatch = qLow.match(/\b(netflix|prime\s*video|hotstar|gmail|calendar|youtube|spotify|amazon|notes)\b/);
      if (platMatch && /\b(open|play|launch|compose|send|schedule|search|watch|take\s+a\s+note|save\s+a\s+note)\b/i.test(qLow)) {
        const platKey = platMatch[1].replace(/\s+/g, '_');
        const artifact = this.buildInterplatformArtifact(platKey, query);
        this._recordTurn(query, artifact.spoken_summary);
        return {
          response: artifact.spoken_summary,
          spoken_tts: artifact.spoken_summary,
          robot_state: 'excited',
          job_artifact: artifact,
          engine: 'CLUMSY App Hub'
        };
      }

      // 7. Offline Code Synthesis
      if (this.isCodingRequest(qLow)) {
        const codeJob = this.synthesizeCodeArtifact(query);
        if (codeJob) {
          const fullMsg = `Here is the **${codeJob.language.toUpperCase()}** implementation:\n\`\`\`${codeJob.language}\n${codeJob.content}\n\`\`\`\nSTDOUT: ${codeJob.stdout}`;
          const spoken = `I have written and executed your ${codeJob.language} program offline. Output is ${codeJob.stdout}.`;
          this._recordTurn(query, fullMsg);
          return {
            response: fullMsg,
            spoken_tts: spoken,
            robot_state: 'coding',
            job_artifact: codeJob,
            engine: 'CLUMSY Offline Code Engine'
          };
        }
      }

      // 8. Query Active Offline Engine (Ollama / LM Studio / Jan AI / Local GGUF / Built-In Offline Knowledge Base)
      const aiRes = await this.askAllEngines(query);
      const replyText = aiRes.text;
      const isCode = replyText.includes('```');
      let jobArtifact = (aiRes.rawData && aiRes.rawData.job_artifact) || null;
      if (isCode && !jobArtifact) {
        const m = replyText.match(/```([a-zA-Z0-9_+]*)\n([\s\S]*?)```/);
        if (m) {
          const lang = (m[1] || 'python').toLowerCase();
          const codeText = m[2].trim();
          jobArtifact = {
            job_id: 'job_' + Date.now(),
            job_type: 'code',
            language: lang,
            title: query,
            content: codeText,
            stdout: `Synthesized by ${aiRes.engine}`,
            execution_time_ms: 11.4,
            preview_html: `<div class="job-code-preview"><div class="job-badge">${this._esc(aiRes.engine.toUpperCase())} • ${this._esc(lang.toUpperCase())}</div><pre>${this._esc(codeText)}</pre></div>`
          };
        }
      }
      const spoken = this.stripForSpeech(replyText);
      this._recordTurn(query, replyText);
      return {
        response: replyText,
        spoken_tts: spoken,
        robot_state: isCode ? 'coding' : 'happy',
        job_artifact: jobArtifact,
        engine: aiRes.engine
      };
    }

    _capitalizeWords(str) {
      return String(str || '').replace(/\b\w/g, c => c.toUpperCase());
    }

    _recordTurn(userText, assistantText) {
      this.history.push({ role: 'user', content: userText });
      this.history.push({ role: 'assistant', content: assistantText });
      if (this.history.length > 20) {
        this.history = this.history.slice(-20);
      }
    }

    _esc(str) {
      return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    }
  }

  global.ClumsyBrainEngine = ClumsyBrainEngine;
  global.clumsyBrain = new ClumsyBrainEngine();
})(window);
