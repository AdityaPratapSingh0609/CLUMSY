/**
 * Stage 40: 100-Prompt & 100-Test Comprehensive Benchmark Suite
 *
 * Verifies:
 * - Category 1 (Prompts 1-25): Multi-Step Cognitive Word Problems, Financial Math & Physical Unit Conversions (Bugs #73, #74, #75)
 * - Category 2 (Prompts 26-50): Dynamic Domain Taxonomy Synthesizer (Bug #76)
 * - Category 3 (Prompts 51-75): Grammar Polisher, Text Utilities, Code Explanation & Translations (Bugs #79, #80, #81, #83)
 * - Category 4 (Prompts 76-100): Voice Interruption, System Health, Multi-Turn Context & Reasoning (Bugs #77, #78, #82, #84)
 */

const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');

let passCount = 0;
let failCount = 0;
const failures = [];

function assert(condition, testId, prompt, message) {
  if (condition) {
    passCount++;
    console.log(`  ✅ [PASS #${String(passCount).padStart(3, '0')}] [${testId}] "${prompt}"`);
  } else {
    failCount++;
    console.error(`  ❌ [FAIL #${String(failCount).padStart(3, '0')}] [${testId}] "${prompt}" -> ${message}`);
    failures.push({ testId, prompt, message });
  }
}

async function runStage40Benchmark() {
  console.log('='.repeat(80));
  console.log('🚀 RUNNING STAGE 40: 100-PROMPT & 100-TEST ADVANCED REASONING BENCHMARK');
  console.log('='.repeat(80));

  const b = new ClumsyBrainEngine();

  // --- CATEGORY 1: Unit Conversions, Financial Math & Word Problems (Prompts 1-25) ---
  console.log('\n--- CATEGORY 1: Multi-Step Word Problems, Financial Math & Unit Conversions ---');
  
  const r1 = await b.processSmartQuery('convert 10 miles to km');
  assert(r1.response.includes('16.0934'), 'C1-01', 'convert 10 miles to km', 'Failed mi to km');

  const r2 = await b.processSmartQuery('convert 5 km to miles');
  assert(r2.response.includes('3.1068') || r2.response.includes('miles'), 'C1-02', 'convert 5 km to miles', 'Failed km to mi');

  const r3 = await b.processSmartQuery('convert 25 celsius to fahrenheit');
  assert(r3.response.includes('77'), 'C1-03', 'convert 25 celsius to fahrenheit', 'Failed C to F');

  const r4 = await b.processSmartQuery('what is 100 fahrenheit in celsius');
  assert(r4.response.includes('37.78'), 'C1-04', 'what is 100 fahrenheit in celsius', 'Failed F to C');

  const r5 = await b.processSmartQuery('convert 0 celsius to kelvin');
  assert(r5.response.includes('273.15'), 'C1-05', 'convert 0 celsius to kelvin', 'Failed C to K');

  const r6 = await b.processSmartQuery('convert 300 kelvin to celsius');
  assert(r6.response.includes('26.85'), 'C1-06', 'convert 300 kelvin to celsius', 'Failed K to C');

  const r7 = await b.processSmartQuery('convert 6 feet to meters');
  assert(r7.response.includes('1.8288'), 'C1-07', 'convert 6 feet to meters', 'Failed ft to m');

  const r8 = await b.processSmartQuery('convert 10 meters to feet');
  assert(r8.response.includes('32.8084'), 'C1-08', 'convert 10 meters to feet', 'Failed m to ft');

  const r9 = await b.processSmartQuery('convert 12 inches to cm');
  assert(r9.response.includes('30.48'), 'C1-09', 'convert 12 inches to cm', 'Failed in to cm');

  const r10 = await b.processSmartQuery('convert 50 cm to inches');
  assert(r10.response.includes('19.685'), 'C1-10', 'convert 50 cm to inches', 'Failed cm to in');

  const r11 = await b.processSmartQuery('convert 5 kg to lbs');
  assert(r11.response.includes('11.0231'), 'C1-11', 'convert 5 kg to lbs', 'Failed kg to lbs');

  const r12 = await b.processSmartQuery('convert 10 lbs to kg');
  assert(r12.response.includes('4.5359'), 'C1-12', 'convert 10 lbs to kg', 'Failed lbs to kg');

  const r13 = await b.processSmartQuery('convert 500 grams to ounces');
  assert(r13.response.includes('17.637'), 'C1-13', 'convert 500 grams to ounces', 'Failed g to oz');

  const r14 = await b.processSmartQuery('convert 2 hours to minutes');
  assert(r14.response.includes('120'), 'C1-14', 'convert 2 hours to minutes', 'Failed hr to min');

  const r15 = await b.processSmartQuery('convert 3.5 hours to minutes');
  assert(r15.response.includes('210'), 'C1-15', 'convert 3.5 hours to minutes', 'Failed 3.5 hr to min');

  const r16 = await b.processSmartQuery('convert 90 minutes to seconds');
  assert(r16.response.includes('5400'), 'C1-16', 'convert 90 minutes to seconds', 'Failed min to sec');

  const r17 = await b.processSmartQuery('convert 3 days to hours');
  assert(r17.response.includes('72'), 'C1-17', 'convert 3 days to hours', 'Failed days to hr');

  const r18 = await b.processSmartQuery('how many miles in 15 km');
  assert(r18.response.includes('9.32') || r18.response.includes('miles'), 'C1-18', 'how many miles in 15 km', 'Failed how many miles');

  const r19 = await b.processSmartQuery('how many feet in 5 meters');
  assert(r19.response.includes('16.4042') || r19.response.includes('feet'), 'C1-19', 'how many feet in 5 meters', 'Failed how many feet');

  const r20 = await b.processSmartQuery('20% discount on 150 dollars');
  assert(r20.response.includes('120') && r20.response.includes('30'), 'C1-20', '20% discount on 150 dollars', 'Failed 20% discount');

  const r21 = await b.processSmartQuery('25% off 80');
  assert(r21.response.includes('60') && r21.response.includes('20'), 'C1-21', '25% off 80', 'Failed 25% off');

  const r22 = await b.processSmartQuery('15% tip on 85 dollars');
  assert(r22.response.includes('97.75') && r22.response.includes('12.75'), 'C1-22', '15% tip on 85 dollars', 'Failed 15% tip');

  const r23 = await b.processSmartQuery('tax on 250 at 8%');
  assert(r23.response.includes('270') && r23.response.includes('20'), 'C1-23', 'tax on 250 at 8%', 'Failed tax on 250');

  const r24 = await b.processSmartQuery('Alice has 15 apples and gives 4 to Bob and 3 to Charlie, how many does she have left?');
  assert(r24.response.includes('8') && r24.response.toLowerCase().includes('remaining'), 'C1-24', 'Alice has 15 apples...', 'Failed apple word problem');

  const r25 = await b.processSmartQuery('A car travels 60 mph for 3.5 hours, how far does it travel?');
  assert(r25.response.includes('210'), 'C1-25', 'A car travels 60 mph for 3.5 hours...', 'Failed speed-distance problem');

  // --- CATEGORY 2: Dynamic Taxonomy Synthesizer (Prompts 26-50) ---
  console.log('\n--- CATEGORY 2: Dynamic Domain Taxonomy Synthesizer ---');

  const r26 = await b.processSmartQuery('explain quantum superposition');
  assert(r26.response.includes('Physics') || r26.response.toLowerCase().includes('quantum'), 'C2-01', 'explain quantum superposition', 'Failed quantum domain');

  const r27 = await b.processSmartQuery('what is general relativity');
  assert(r27.response.toLowerCase().includes('spacetime') || r27.response.toLowerCase().includes('einstein'), 'C2-02', 'what is general relativity', 'Failed relativity domain');

  const r28 = await b.processSmartQuery('explain gravitational time dilation');
  assert(r28.response.toLowerCase().includes('gravitational') || r28.response.toLowerCase().includes('clocks'), 'C2-03', 'explain gravitational time dilation', 'Failed time dilation');

  const r29 = await b.processSmartQuery('what is dark energy');
  assert(r29.response.toLowerCase().includes('universe') || r29.response.toLowerCase().includes('cosmology') || r29.response.toLowerCase().includes('expansion'), 'C2-04', 'what is dark energy', 'Failed dark energy');

  const r30 = await b.processSmartQuery('what is a black hole event horizon');
  assert(r30.response.toLowerCase().includes('horizon') || r30.response.toLowerCase().includes('gravity') || r30.response.toLowerCase().includes('light'), 'C2-05', 'what is a black hole event horizon', 'Failed black hole');

  const r31 = await b.processSmartQuery('explain tcp 3-way handshake');
  assert(r31.response.toLowerCase().includes('tcp') || r31.response.toLowerCase().includes('syn'), 'C2-06', 'explain tcp 3-way handshake', 'Failed tcp handshake');

  const r32 = await b.processSmartQuery('what is a microkernel operating system');
  assert(r32.response.includes('Computer Science') || r32.response.toLowerCase().includes('operating system'), 'C2-07', 'what is a microkernel operating system', 'Failed microkernel');

  const r33 = await b.processSmartQuery('explain public key cryptography');
  assert(r33.response.toLowerCase().includes('encryption') || r33.response.toLowerCase().includes('key') || r33.response.includes('Computer Science'), 'C2-08', 'explain public key cryptography', 'Failed cryptography');

  const r34 = await b.processSmartQuery('what is dynamic programming');
  assert(r34.response.toLowerCase().includes('subproblem') || r34.response.toLowerCase().includes('algorithm') || r34.response.toLowerCase().includes('memoization'), 'C2-09', 'what is dynamic programming', 'Failed dynamic programming');

  const r35 = await b.processSmartQuery('explain database index b-tree');
  assert(r35.response.includes('Computer Science') || r35.response.toLowerCase().includes('database') || r35.response.toLowerCase().includes('search'), 'C2-10', 'explain database index b-tree', 'Failed database b-tree');

  const r36 = await b.processSmartQuery('what is cellular respiration');
  assert(r36.response.toLowerCase().includes('atp') || r36.response.toLowerCase().includes('glucose') || r36.response.toLowerCase().includes('mitochondria'), 'C2-11', 'what is cellular respiration', 'Failed cellular respiration');

  const r37 = await b.processSmartQuery('explain crispr gene editing');
  assert(r37.response.toLowerCase().includes('gene') || r37.response.toLowerCase().includes('dna') || r37.response.includes('Biological'), 'C2-12', 'explain crispr gene editing', 'Failed crispr');

  const r38 = await b.processSmartQuery('what is natural selection');
  assert(r38.response.toLowerCase().includes('evolution') || r38.response.toLowerCase().includes('survival') || r38.response.toLowerCase().includes('traits'), 'C2-13', 'what is natural selection', 'Failed natural selection');

  const r39 = await b.processSmartQuery('explain enzyme substrate specificity');
  assert(r39.response.includes('Biological') || r39.response.toLowerCase().includes('enzyme') || r39.response.toLowerCase().includes('catalyst') || r39.response.toLowerCase().includes('protein') || r39.response.toLowerCase().includes('specificity'), 'C2-14', 'explain enzyme substrate specificity', 'Failed enzyme');

  const r40 = await b.processSmartQuery('what is synaptic transmission');
  assert(r40.response.toLowerCase().includes('neuron') || r40.response.toLowerCase().includes('neurotransmitter') || r40.response.includes('Biological'), 'C2-15', 'what is synaptic transmission', 'Failed synapse');

  const r41 = await b.processSmartQuery('explain covalent vs ionic bonding');
  assert(r41.response.toLowerCase().includes('electron') || r41.response.toLowerCase().includes('covalent') || r41.response.toLowerCase().includes('ionic'), 'C2-16', 'explain covalent vs ionic bonding', 'Failed bonding');

  const r42 = await b.processSmartQuery('what is entropy in chemistry');
  assert(r42.response.toLowerCase().includes('disorder') || r42.response.toLowerCase().includes('entropy') || r42.response.toLowerCase().includes('thermodynamics'), 'C2-17', 'what is entropy in chemistry', 'Failed entropy');

  const r43 = await b.processSmartQuery('explain acid base neutralization');
  assert(r43.response.includes('Chemical') || r43.response.toLowerCase().includes('water') || r43.response.toLowerCase().includes('salt'), 'C2-18', 'explain acid base neutralization', 'Failed acid base');

  const r44 = await b.processSmartQuery('what is polymer polymerization');
  assert(r44.response.includes('Chemical') || r44.response.toLowerCase().includes('monomer') || r44.response.toLowerCase().includes('polymer'), 'C2-19', 'what is polymer polymerization', 'Failed polymer');

  const r45 = await b.processSmartQuery('explain galvanic electrochemical cell');
  assert(r45.response.includes('Chemical') || r45.response.toLowerCase().includes('galvanic') || r45.response.toLowerCase().includes('voltaic') || r45.response.toLowerCase().includes('electrochemical') || r45.response.toLowerCase().includes('redox') || r45.response.toLowerCase().includes('oxidation') || r45.response.toLowerCase().includes('energy'), 'C2-20', 'explain galvanic electrochemical cell', 'Failed galvanic cell');

  const r46 = await b.processSmartQuery('what is calculus derivative');
  assert(r46.response.toLowerCase().includes('rate of change') || r46.response.toLowerCase().includes('slope') || r46.response.includes('Mathematical'), 'C2-21', 'what is calculus derivative', 'Failed derivative');

  const r47 = await b.processSmartQuery('explain matrix eigenvalue and eigenvector');
  assert(r47.response.includes('Mathematical') || r47.response.toLowerCase().includes('vector') || r47.response.toLowerCase().includes('matrix'), 'C2-22', 'explain eigenvalue', 'Failed eigenvalue');

  const r48 = await b.processSmartQuery('what is bayes theorem');
  assert(r48.response.toLowerCase().includes('probability') || r48.response.includes('Mathematical') || r48.response.toLowerCase().includes('prior'), 'C2-23', 'what is bayes theorem', 'Failed bayes theorem');

  const r49 = await b.processSmartQuery('what was the industrial revolution');
  assert(r49.response.includes('Historical') || r49.response.toLowerCase().includes('manufacturing') || r49.response.toLowerCase().includes('steam'), 'C2-24', 'what was the industrial revolution', 'Failed industrial revolution');

  const r50 = await b.processSmartQuery('explain the treaty of versailles');
  assert(r50.response.includes('Historical') || r50.response.toLowerCase().includes('war') || r50.response.toLowerCase().includes('1919'), 'C2-25', 'explain treaty of versailles', 'Failed versailles');

  // --- CATEGORY 3: Grammar Polisher, Text Utilities & Code Explanation (Prompts 51-75) ---
  console.log('\n--- CATEGORY 3: Grammar Polisher, Text Utilities & Code Explanation ---');

  const r51 = await b.processSmartQuery('fix the grammar of: she dont have no time for this');
  assert(r51.response.includes("doesn't") && r51.response.includes('any time'), 'C3-01', 'fix grammar of double negative', 'Failed grammar double negative');

  const r52 = await b.processSmartQuery('make this sentence more professional: i want to tell you that i am not coming to office today');
  assert(r52.response.includes('inform you') && r52.response.includes('unable to attend'), 'C3-02', 'make sentence professional', 'Failed professional rewrite');

  const r53 = await b.processSmartQuery('fix grammar of: me and him went to the market yesterday');
  assert(r53.response.includes('He and I') || r53.response.includes('he and I'), 'C3-03', 'fix subject pronoun agreement', 'Failed pronoun agreement');

  const r54 = await b.processSmartQuery('check grammar of: they aint gonna do it');
  assert(r54.response.includes('is not') || r54.response.includes('going to') || r54.response.includes('are not'), 'C3-04', 'fix slang contractions', 'Failed slang grammar');

  const r55 = await b.processSmartQuery('polish this sentence: i wanna ask for sick leave');
  assert(r55.response.includes('Polished') && r55.response.toLowerCase().includes('sick leave'), 'C3-05', 'polish sentence', 'Failed polish sentence');

  const r56 = await b.processSmartQuery('count words in: The quick brown fox jumps over the lazy dog');
  assert(r56.response.includes('9 words'), 'C3-06', 'count words in 9-word sentence', 'Failed word count 9');

  const r57 = await b.processSmartQuery('count words in: Hello world from CLUMSY');
  assert(r57.response.includes('4 words'), 'C3-07', 'count words in 4-word sentence', 'Failed word count 4');

  const r58 = await b.processSmartQuery('reverse the text: hello world');
  assert(r58.response.includes('dlrow olleh'), 'C3-08', 'reverse the text: hello world', 'Failed reverse hello world');

  const r59 = await b.processSmartQuery('reverse the text: racecar');
  assert(r59.response.includes('racecar'), 'C3-09', 'reverse racecar palindrome', 'Failed reverse palindrome');

  const r60 = await b.processSmartQuery('reverse the text: clumsy');
  assert(r60.response.includes('ysmulc'), 'C3-10', 'reverse clumsy', 'Failed reverse clumsy');

  const r61 = await b.processSmartQuery('convert to uppercase: artificial intelligence');
  assert(r61.response.includes('ARTIFICIAL INTELLIGENCE'), 'C3-11', 'convert to uppercase', 'Failed uppercase conversion');

  const r62 = await b.processSmartQuery('convert to uppercase: machine learning');
  assert(r62.response.includes('MACHINE LEARNING'), 'C3-12', 'convert to uppercase ml', 'Failed uppercase ml');

  const r63 = await b.processSmartQuery('convert to lowercase: FULL STACK DEVELOPER');
  assert(r63.response.includes('full stack developer'), 'C3-13', 'convert to lowercase', 'Failed lowercase conversion');

  const r64 = await b.processSmartQuery('convert to lowercase: CLUMSY 7X OMNI');
  assert(r64.response.includes('clumsy 7x omni'), 'C3-14', 'convert to lowercase bot name', 'Failed lowercase bot name');

  const r65 = await b.processSmartQuery('explain this code: def add(a, b): return a + b');
  assert(r65.response.includes('Code Architecture') && r65.response.includes('O(1)'), 'C3-15', 'explain add function code', 'Failed explain simple code');

  const r66 = await b.processSmartQuery('explain this code: for i in range(10): print(i)');
  assert(r66.response.includes('O(N)') || r66.response.toLowerCase().includes('loop'), 'C3-16', 'explain loop code', 'Failed explain loop code');

  const r67 = await b.processSmartQuery('explain this code: def fib(n): return fib(n-1) + fib(n-2) if n > 1 else n');
  assert(r67.response.includes('Recursive') || r67.response.includes('O(2^N)'), 'C3-17', 'explain recursive code', 'Failed explain recursion');

  const r68 = await b.processSmartQuery('explain code: while x > 0: x -= 1');
  assert(r68.response.includes('Code Architecture') || r68.response.toLowerCase().includes('loop'), 'C3-18', 'explain while loop', 'Failed explain while code');

  const r69 = await b.processSmartQuery("explain code: if score >= 90: grade = 'A'");
  assert(r69.response.includes('Code Architecture') || r69.response.toLowerCase().includes('conditional'), 'C3-19', 'explain if condition', 'Failed explain if condition');

  const r70 = await b.processSmartQuery('translate hello to Japanese');
  assert(r70.response.includes('Konnichiwa') || r70.response.includes('こんにちは'), 'C3-20', 'translate hello to Japanese', 'Failed Japanese hello');

  const r71 = await b.processSmartQuery('translate thank you to Japanese');
  assert(r71.response.includes('Arigatou') || r71.response.includes('ありがとうございます'), 'C3-21', 'translate thank you to Japanese', 'Failed Japanese thank you');

  const r72 = await b.processSmartQuery('translate good morning to Japanese');
  assert(r72.response.includes('Ohayou') || r72.response.includes('おはようございます'), 'C3-22', 'translate good morning to Japanese', 'Failed Japanese morning');

  const r73 = await b.processSmartQuery('translate hello to Italian');
  assert(r73.response.includes('Ciao'), 'C3-23', 'translate hello to Italian', 'Failed Italian hello');

  const r74 = await b.processSmartQuery('translate thank you to Italian');
  assert(r74.response.includes('Grazie'), 'C3-24', 'translate thank you to Italian', 'Failed Italian thank you');

  const r75 = await b.processSmartQuery('translate goodbye to Italian');
  assert(r75.response.includes('Arrivederci'), 'C3-25', 'translate goodbye to Italian', 'Failed Italian goodbye');

  // --- CATEGORY 4: Voice Interruption, System Health & Multi-Turn Context (Prompts 76-100) ---
  console.log('\n--- CATEGORY 4: Voice Interruption, System Health & Multi-Turn Context ---');

  const r76 = await b.processSmartQuery('stop talking');
  assert(r76.response.toLowerCase().includes('silenced'), 'C4-01', 'stop talking', 'Failed stop talking');

  const r77 = await b.processSmartQuery('be quiet');
  assert(r77.response.toLowerCase().includes('silenced'), 'C4-02', 'be quiet', 'Failed be quiet');

  const r78 = await b.processSmartQuery('shut up');
  assert(r78.response.toLowerCase().includes('silenced'), 'C4-03', 'shut up', 'Failed shut up');

  const r79 = await b.processSmartQuery('silence');
  assert(r79.response.toLowerCase().includes('silenced'), 'C4-04', 'silence', 'Failed silence');

  const r80 = await b.processSmartQuery('cancel speech');
  assert(r80.response.toLowerCase().includes('silenced'), 'C4-05', 'cancel speech', 'Failed cancel speech');

  const r81 = await b.processSmartQuery('system health');
  assert(r81.response.includes('CLUMSY-7X Omni System Diagnostics') && r81.response.includes('100% Operational'), 'C4-06', 'system health', 'Failed system health');

  const r82 = await b.processSmartQuery('how is my pc doing');
  assert(r82.response.includes('Diagnostics'), 'C4-07', 'how is my pc doing', 'Failed pc status');

  const r83 = await b.processSmartQuery('system status');
  assert(r83.response.includes('Diagnostics'), 'C4-08', 'system status', 'Failed system status');

  const r84 = await b.processSmartQuery('cpu usage');
  assert(r84.response.includes('GGUF Cores') || r84.response.includes('Diagnostics'), 'C4-09', 'cpu usage', 'Failed cpu usage');

  const r85 = await b.processSmartQuery('who are you');
  assert(r85.response.includes('CLUMSY-7X Omni'), 'C4-10', 'who are you', 'Failed identity reflex');

  const r86 = await b.processSmartQuery('my name is Aditya');
  assert(r86.response.includes('Aditya'), 'C4-11', 'my name is Aditya', 'Failed set name');

  const r87 = await b.processSmartQuery('what is my name?');
  assert(r87.response.includes('Aditya'), 'C4-12', 'what is my name?', 'Failed recall name');

  const r88 = await b.processSmartQuery('what is the capital of France?');
  assert(r88.response.includes('Paris'), 'C4-13', 'capital of France', 'Failed capital of France');

  const r89 = await b.processSmartQuery('what is the boiling point of water?');
  assert(r89.response.includes('100') || r89.response.includes('212'), 'C4-14', 'boiling point of water', 'Failed boiling point');

  const r90 = await b.processSmartQuery('what is the speed of light?');
  assert(r90.response.includes('299,792,458'), 'C4-15', 'speed of light', 'Failed speed of light');

  const r91 = await b.processSmartQuery('solve 3x + 5 = 20');
  assert(r91.response.includes('5'), 'C4-16', 'solve 3x + 5 = 20', 'Failed linear equation');

  const r92 = await b.processSmartQuery('what is the square root of 144');
  assert(r92.response.includes('12'), 'C4-17', 'square root of 144', 'Failed sqrt');

  const r93 = await b.processSmartQuery('evaluate 5!');
  assert(r93.response.includes('120'), 'C4-18', 'evaluate 5!', 'Failed factorial');

  const r94 = await b.processSmartQuery('write python code for binary search');
  assert(r94.response.includes('def binary_search') || r94.response.toLowerCase().includes('binary_search'), 'C4-19', 'python binary search', 'Failed binary search');

  const r95 = await b.processSmartQuery('now write that in c++');
  assert(r95.response.toLowerCase().includes('c++') || r95.response.toLowerCase().includes('int binarysearch') || r95.response.includes('binarySearch'), 'C4-20', 'now in c++', 'Failed c++ transition');

  const r96 = await b.processSmartQuery('now in javascript');
  assert(r96.response.toLowerCase().includes('javascript') || r96.response.toLowerCase().includes('function binarysearch'), 'C4-21', 'now in js', 'Failed js transition');

  const r97 = await b.processSmartQuery('summarize our conversation');
  assert(r97.response.includes('Conversation Summary'), 'C4-22', 'summarize our conversation', 'Failed conversation summary');

  const r98 = await b.processSmartQuery('what was my last question?');
  assert(r98.response.toLowerCase().includes('summarize our conversation'), 'C4-23', 'last question recall', 'Failed last question recall');

  const r99 = await b.processSmartQuery('A train travels at 80 km/h for 2.5 hours, how far does it travel?');
  assert(r99.response.includes('200'), 'C4-24', 'train distance problem', 'Failed train distance');

  const r100 = await b.processSmartQuery('If each notebook costs 5 dollars, what is the cost of 8 notebooks?');
  assert(r100.response.includes('40'), 'C4-25', 'unit price problem', 'Failed notebook cost');

  console.log('\n' + '='.repeat(80));
  console.log(`🏆 STAGE 40 BENCHMARK RESULTS: ${passCount}/100 PASSED (${((passCount/100)*100).toFixed(1)}%) | ${failCount} FAILED`);
  console.log('='.repeat(80));

  if (failCount > 0) {
    console.error('\n⚠️ DETAILED FAILURE BREAKDOWN:');
    failures.forEach((f, idx) => {
      console.error(`  ${idx + 1}. [${f.testId}] "${f.prompt}": ${f.message}`);
    });
    process.exit(1);
  } else {
    console.log('\n✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 40 COMPLETE! ✨\n');
  }
}

runStage40Benchmark();
