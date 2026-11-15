/**
 * STAGE 53: ROCK-SOLID DEMO QUESTIONS & CONVERSATIONAL LOOPING VERIFICATION
 * Tests Science, Maths, and Coding with full conversational rephrasings,
 * multi-turn follow-ups, anaphora, language conversions, and zero Wikipedia leaks.
 */

const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');

let passed = 0;
let failed = 0;
const failureDetails = [];

function assert(condition, testId, prompt, failMsg) {
  if (condition) {
    passed++;
    console.log(`  ✅ [PASS #${String(passed).padStart(2, '0')}] [${testId}] "${prompt}"`);
  } else {
    failed++;
    console.error(`  ❌ [FAIL #${String(failed).padStart(2, '0')}] [${testId}] "${prompt}" -> ${failMsg}`);
    failureDetails.push({ testId, prompt, failMsg });
  }
}

async function runDemoLoopingVerification() {
  console.log('='.repeat(80));
  console.log('🚀 RUNNING STAGE 53 DEMO SUITE & CONVERSATIONAL LOOPING BENCHMARK');
  console.log('='.repeat(80));
  console.log('');

  const brain = new ClumsyBrainEngine();
  let r = null;
  const startTime = Date.now();

  // ---------------------------------------------------------------------------
  // 1. MATHEMATICS DEMO & CONVERSATIONAL LOOPS
  // ---------------------------------------------------------------------------
  console.log('\n--- 1. MATHEMATICS DEMO QUESTIONS & CONVERSATIONAL LOOPS ---');

  // 1.1 Base Trig: cos 60
  r = await brain.processSmartQuery("what is the value of cos 60");
  assert(r && r.response && (r.response.includes("0.5") || r.response.includes("1/2")), "M-01a", "what is the value of cos 60", "Expected cos(60) = 0.5");

  // 1.1 Loop 1: bare cos 60
  r = await brain.processSmartQuery("cos 60");
  assert(r && r.response && (r.response.includes("0.5") || r.response.includes("1/2")), "M-01b", "cos 60", "Expected bare cos 60 = 0.5");

  // 1.1 Loop 2: conversational follow-up "what about sin 30?"
  r = await brain.processSmartQuery("what about sin 30?");
  assert(r && r.response && (r.response.includes("0.5") || r.response.includes("1/2")), "M-01c", "what about sin 30?", "Expected sin(30) = 0.5");

  // 1.1 Loop 3: conversational follow-up "now cos 30"
  r = await brain.processSmartQuery("now cos 30");
  assert(r && r.response && (r.response.includes("√3") || r.response.includes("0.866")), "M-01d", "now cos 30", "Expected cos(30) = √3/2");

  // 1.1 Loop 4: conversational follow-up "and tan 45?"
  r = await brain.processSmartQuery("and tan 45?");
  assert(r && r.response && r.response.includes("1"), "M-01e", "and tan 45?", "Expected tan(45) = 1");

  // 1.1 Loop 5: spelled out "cosine of 60"
  r = await brain.processSmartQuery("what is the cosine of 60");
  assert(r && r.response && (r.response.includes("0.5") || r.response.includes("1/2")), "M-01f", "what is the cosine of 60", "Expected cosine of 60 = 0.5");

  // 1.2 Quadratic Base: solve x^2 - 5x + 6 = 0
  r = await brain.processSmartQuery("solve x^2 - 5x + 6 = 0");
  assert(r && r.response && r.response.includes("2") && r.response.includes("3") && !r.response.includes("Rational root theorem"), "M-02a", "solve x^2 - 5x + 6 = 0", "Expected roots 2 and 3");

  // 1.2 Loop 1: "find the roots of x^2 - 5x + 6 = 0"
  r = await brain.processSmartQuery("find the roots of x^2 - 5x + 6 = 0");
  assert(r && r.response && r.response.includes("2") && r.response.includes("3") && !r.response.includes("Rational root theorem"), "M-02b", "find the roots of x^2 - 5x + 6 = 0", "Expected roots 2 and 3 without Wikipedia leak");

  // 1.2 Loop 2: "what are the solutions to x^2 - 5x + 6 = 0"
  r = await brain.processSmartQuery("what are the solutions to x^2 - 5x + 6 = 0");
  assert(r && r.response && r.response.includes("2") && r.response.includes("3"), "M-02c", "what are the solutions to x^2 - 5x + 6 = 0", "Expected roots 2 and 3");

  // 1.2 Loop 3: "roots of 2x^2 + 5x - 3 = 0"
  r = await brain.processSmartQuery("roots of 2x^2 + 5x - 3 = 0");
  assert(r && r.response && (r.response.includes("-3") && (r.response.includes("0.5") || r.response.includes("1/2"))), "M-02d", "roots of 2x^2 + 5x - 3 = 0", "Expected roots -3 and 0.5");

  // 1.3 Derivatives: "what is the derivative of x^3"
  r = await brain.processSmartQuery("what is the derivative of x^3");
  assert(r && r.response && (r.response.includes("3x^2") || r.response.includes("3x²")), "M-03a", "what is the derivative of x^3", "Expected 3x^2");

  // 1.3 Loop 1: "derivative of x^4"
  r = await brain.processSmartQuery("derivative of x^4");
  assert(r && r.response && r.response.includes("4x^3"), "M-03b", "derivative of x^4", "Expected 4x^3");

  // 1.4 Power arithmetic: "what is 2^10"
  r = await brain.processSmartQuery("what is 2^10");
  assert(r && r.response && r.response.includes("1024"), "M-04a", "what is 2^10", "Expected 1024");

  // 1.4 Loop 1: bare "2^10"
  r = await brain.processSmartQuery("2^10");
  assert(r && r.response && r.response.includes("1024"), "M-04b", "2^10", "Expected 1024");

  // 1.4 Loop 2: "what is 2 to the power of 10"
  r = await brain.processSmartQuery("what is 2 to the power of 10");
  assert(r && r.response && r.response.includes("1024"), "M-04c", "what is 2 to the power of 10", "Expected 1024");

  // 1.5 Euler's identity: "what is Euler's identity"
  r = await brain.processSmartQuery("what is Euler's identity");
  assert(r && r.response && (r.response.includes("e^{i\\pi}") || r.response.includes("e^(i*pi)") || r.response.includes("+ 1 = 0") || r.response.includes("Euler")), "M-05a", "what is Euler's identity", "Expected Euler's identity");

  // 1.5 Loop 1: "explain eulers formula"
  r = await brain.processSmartQuery("explain eulers formula");
  assert(r && r.response && (r.response.includes("Euler") || r.response.includes("formula")), "M-05b", "explain eulers formula", "Expected Euler's formula");

  // ---------------------------------------------------------------------------
  // 2. SCIENCE DEMO QUESTIONS (PHYSICS, CHEMISTRY, BIOLOGY) & CONVERSATIONAL LOOPS
  // ---------------------------------------------------------------------------
  console.log('\n--- 2. SCIENCE DEMO QUESTIONS & CONVERSATIONAL LOOPS ---');

  // 2.1 Newton's Second Law Base
  r = await brain.processSmartQuery("what is Newton's second law");
  assert(r && r.response && (r.response.includes("F = ma") || r.response.includes("momentum") || r.response.includes("force")), "S-01a", "what is Newton's second law", "Expected Newton's second law");

  // 2.1 Loop 1: "can you explain newton's second law?"
  r = await brain.processSmartQuery("can you explain newton's second law?");
  assert(r && r.response && (r.response.includes("F = ma") || r.response.includes("Newton") || r.response.includes("force")), "S-01b", "can you explain newton's second law?", "Expected Newton's second law with conversational wrapper");

  // 2.1 Loop 2: "what about newtons third law?"
  r = await brain.processSmartQuery("what about newtons third law?");
  assert(r && r.response && (r.response.includes("action") || r.response.includes("reaction") || r.response.includes("equal and opposite")), "S-01c", "what about newtons third law?", "Expected Newton's third law");

  // 2.2 Mass Energy Equivalence Base
  r = await brain.processSmartQuery("what is Einstein's mass energy equivalence");
  assert(r && r.response && (r.response.includes("E = mc^2") || r.response.includes("E = mc²") || r.response.includes("Einstein")), "S-02a", "what is Einstein's mass energy equivalence", "Expected E = mc^2");

  // 2.2 Loop 1: "explain E = mc^2"
  r = await brain.processSmartQuery("explain E = mc^2");
  assert(r && r.response && (r.response.includes("mass") || r.response.includes("energy") || r.response.includes("light")), "S-02b", "explain E = mc^2", "Expected E = mc^2 explanation");

  // 2.3 Chemical Formula of Glucose Base
  r = await brain.processSmartQuery("what is the chemical formula for glucose");
  assert(r && r.response && r.response.toLowerCase().includes("c6h12o6"), "S-03a", "what is the chemical formula for glucose", "Expected C6H12O6");

  // 2.3 Loop 1: "tell me the chemical formula of glucose"
  r = await brain.processSmartQuery("tell me the chemical formula of glucose");
  assert(r && r.response && r.response.toLowerCase().includes("c6h12o6"), "S-03b", "tell me the chemical formula of glucose", "Expected C6H12O6 with conversational wrapper");

  // 2.4 Avogadro's Number Base
  r = await brain.processSmartQuery("what is Avogadro's number");
  assert(r && r.response && (r.response.includes("6.022") || r.response.includes("mole")), "S-04a", "what is Avogadro's number", "Expected 6.022 x 10^23");

  // 2.4 Loop 1: "value of avogadro number"
  r = await brain.processSmartQuery("value of avogadro number");
  assert(r && r.response && (r.response.includes("6.022") || r.response.includes("mole")), "S-04b", "value of avogadro number", "Expected 6.022 x 10^23");

  // 2.5 Central Dogma of Molecular Biology Base
  r = await brain.processSmartQuery("what is the central dogma of molecular biology");
  assert(r && r.response && (r.response.includes("DNA") && r.response.includes("RNA") && r.response.includes("protein")), "S-05a", "what is the central dogma of molecular biology", "Expected DNA -> RNA -> Protein");

  // 2.5 Loop 1: "explain central dogma of biology"
  r = await brain.processSmartQuery("explain central dogma of biology");
  assert(r && r.response && (r.response.includes("DNA") && r.response.includes("RNA")), "S-05b", "explain central dogma of biology", "Expected DNA -> RNA -> Protein");

  // 2.6 DNA Base Pairs Base
  r = await brain.processSmartQuery("what are the DNA base pairs");
  assert(r && r.response && (r.response.toLowerCase().includes("adenine") || r.response.toLowerCase().includes("thymine") || r.response.toLowerCase().includes("base pairs")), "S-06a", "what are the DNA base pairs", "Expected A, T, G, C base pairing");

  // 2.7 Photosynthesis Equation Base
  r = await brain.processSmartQuery("what is photosynthesis equation");
  assert(r && r.response && (r.response.includes("CO2") || r.response.includes("H2O") || r.response.includes("glucose") || r.response.includes("photosynthesis")), "S-07a", "what is photosynthesis equation", "Expected photosynthesis reaction");

  // ---------------------------------------------------------------------------
  // 3. CODING DEMO & CONVERSATIONAL LANGUAGE SWITCHING LOOPS
  // ---------------------------------------------------------------------------
  console.log('\n--- 3. CODING DEMO & MULTI-TURN LANGUAGE SWITCHING LOOPS ---');

  // 3.1 Website Generator: Oil business
  r = await brain.processSmartQuery("can you code me a basic website for my oil business");
  assert(r && r.response && (r.response.includes("<!DOCTYPE html>") || r.response.includes("```html")) && !r.response.includes("Governor of Rivers State"), "C-01a", "can you code me a basic website for my oil business", "Expected responsive petroleum website HTML without Wikipedia leak");

  // 3.1 Loop 1: "create a landing page for oil company"
  r = await brain.processSmartQuery("create a landing page for oil company");
  assert(r && r.response && (r.response.includes("<!DOCTYPE html>") || r.response.includes("```html")), "C-01b", "create a landing page for oil company", "Expected HTML landing page");

  // 3.2 Multi-Turn Conversational Language Switching Loop
  console.log('  Testing 5-step conversational language switching chain (Python -> C++ -> Java -> Rust -> JS)...');
  const codeBrain = new ClumsyBrainEngine();

  // Step 1: Base Python binary search
  const step1 = await codeBrain.processSmartQuery("write a Python code for binary search");
  assert(step1 && step1.response && step1.response.includes("```python") && step1.response.includes("def binary_search"), "C-02a", "write a Python code for binary search", "Expected Python binary search");

  // Step 2: Language Switch -> C++
  const step2 = await codeBrain.processSmartQuery("now in C++");
  assert(step2 && step2.response && (step2.response.includes("```cpp") || step2.response.includes("binarySearch") || step2.response.includes("#include")), "C-02b", "now in C++", "Expected C++ binary search conversion");

  // Step 3: Language Switch -> Java
  const step3 = await codeBrain.processSmartQuery("now in Java");
  assert(step3 && step3.response && (step3.response.includes("```java") || step3.response.includes("public static int") || step3.response.includes("binarySearch")), "C-02c", "now in Java", "Expected Java binary search conversion");

  // Step 4: Language Switch -> Rust
  const step4 = await codeBrain.processSmartQuery("now in Rust");
  assert(step4 && step4.response && (step4.response.includes("```rust") || step4.response.includes("fn binary_search")), "C-02d", "now in Rust", "Expected Rust binary search conversion");

  // Step 5: Language Switch -> JavaScript
  const step5 = await codeBrain.processSmartQuery("in JavaScript");
  assert(step5 && step5.response && (step5.response.toLowerCase().includes("binarysearch") || step5.response.includes("```javascript")), "C-02e", "in JavaScript", "Expected JavaScript binary search conversion");

  // 3.3 Two Sum LeetCode
  r = await brain.processSmartQuery("write a Python code for two sum using hash map");
  assert(r && r.response && (r.response.includes("two_sum") || r.response.includes("seen") || r.response.includes("hash")), "C-03a", "write a Python code for two sum using hash map", "Expected Python Two Sum hash map");

  // 3.4 Dijkstra Graph Algorithm
  r = await brain.processSmartQuery("write a Python code for Dijkstra shortest path algorithm");
  assert(r && r.response && (r.response.toLowerCase().includes("dijkstra") || r.response.includes("heapq") || r.response.includes("distances")), "C-04a", "write a Python code for Dijkstra shortest path algorithm", "Expected Python Dijkstra with min-heap");

  // 3.5 Dark Mode Toggle UI Component
  r = await brain.processSmartQuery("write a JavaScript code for dark mode toggle with css variables");
  assert(r && r.response && (r.response.includes("```javascript") || r.response.includes("classList") || r.response.includes("theme")), "C-05a", "write a JavaScript code for dark mode toggle with css variables", "Expected JavaScript dark mode toggle");

  // 3.6 Systems Concurrency (Mutex Lock in C++)
  r = await brain.processSmartQuery("write a CPP code for mutex lock and spinlock implementation");
  assert(r && r.response && (r.response.includes("mutex") || r.response.includes("lock") || r.response.includes("spinlock") || r.response.includes("thread")), "C-06a", "write a CPP code for mutex lock and spinlock implementation", "Expected C++ Mutex Lock implementation");

  // ---------------------------------------------------------------------------
  // 4. ELEVENLABS AMELIA VOICE & IDENTITY VERIFICATION
  // ---------------------------------------------------------------------------
  console.log('\n--- 4. ELEVENLABS AMELIA VOICE & IDENTITY ---');

  r = await brain.processSmartQuery("who is your voice");
  assert(r && r.response && r.response.includes("Amelia") && r.response.includes("ZF6FPAbjXT4488VcRRnw"), "V-01a", "who is your voice", "Expected Amelia ZF6FPAbjXT4488VcRRnw voice identification");

  r = await brain.processSmartQuery("what voice are you using");
  assert(r && r.response && r.response.includes("Amelia"), "V-01b", "what voice are you using", "Expected Amelia voice");

  r = await brain.processSmartQuery("elevenlabs voice");
  assert(r && r.response && r.response.includes("Amelia") && r.response.includes("ElevenLabs"), "V-01c", "elevenlabs voice", "Expected ElevenLabs Amelia voice acknowledgment");

  r = await brain.processSmartQuery("who are you");
  assert(r && r.response && r.response.includes("CLUMSY-7X Omni"), "V-02a", "who are you", "Expected CLUMSY-7X Omni identity");

  // ---------------------------------------------------------------------------
  // SUMMARY
  // ---------------------------------------------------------------------------
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
  const total = passed + failed;
  const pct = ((passed / total) * 100).toFixed(1);

  console.log('');
  console.log('='.repeat(80));
  console.log(`🏆 DEMO LOOPING BENCHMARK: ${passed}/${total} PASSED (${pct}%) | ${failed} FAILED | ${elapsed}s`);
  console.log('='.repeat(80));

  if (failed === 0) {
    console.log('\n✨ ALL DEMO QUESTIONS AND CONVERSATIONAL LOOPS PASSED WITH 100% SUCCESS! ROCK-SOLID FOR HACKATHONS! ✨\n');
  } else {
    console.error(`\n⚠️  ${failed} TESTS FAILED. Inspect failure details above.`);
    process.exit(1);
  }
}

runDemoLoopingVerification().catch(err => {
  console.error("FATAL ERROR in benchmark runner:", err);
  process.exit(1);
});
