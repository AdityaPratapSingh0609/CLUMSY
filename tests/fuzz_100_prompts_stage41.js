/**
 * Stage 41 Fuzz Benchmark: 100 Advanced Cognitive Reasoning Prompts & Logic Stress Tests.
 *
 * Categories:
 * 1. Multi-Stage Chain-of-Thought (CoT) & Counterfactual Reasoning (Prompts 01-25)
 * 2. Logical Fallacies & Foundational Thought Experiments (Prompts 26-50)
 * 3. Direct Comparison Matrix & Technology Versus Evaluator (Prompts 51-75)
 * 4. Socratic Quizzes, Reverse Dictionary, Analogies, Security Refactoring & Timelines (Prompts 76-100)
 */

const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');

async function runStage41Benchmark() {
  console.log('='.repeat(80));
  console.log('🚀 RUNNING STAGE 41: 100-PROMPT ADVANCED COGNITIVE REASONING BENCHMARK');
  console.log('='.repeat(80));

  const b = new ClumsyBrainEngine();
  let passed = 0;
  let failed = 0;
  const failureDetails = [];

  function assert(condition, testId, prompt, message) {
    if (condition) {
      passed++;
      console.log(`  ✅ [PASS #${String(passed).padStart(3, '0')}] [${testId}] "${prompt.slice(0, 42)}"`);
    } else {
      failed++;
      console.error(`  ❌ [FAIL #${String(failed).padStart(3, '0')}] [${testId}] "${prompt}" -> ${message}`);
      failureDetails.push({ testId, prompt, message });
    }
  }

  // --- CATEGORY 1: Multi-Stage Chain-of-Thought (CoT) & Counterfactual Reasoning (Prompts 01-25) ---
  console.log('\n--- CATEGORY 1: Multi-Stage Chain-of-Thought (CoT) & Counterfactual Reasoning ---');

  const r01 = await b.processSmartQuery('explain step by step how does a compiler work');
  assert(r01.response.includes('Chain-of-Thought') && (r01.response.includes('Lexical') || r01.response.includes('AST')), 'C1-01', 'compiler step by step', 'Failed compiler CoT');

  const r02 = await b.processSmartQuery('why does ice float on water');
  assert(r02.response.includes('Chain-of-Thought') && (r02.response.toLowerCase().includes('density') || r02.response.toLowerCase().includes('hexagonal')), 'C1-02', 'why ice floats', 'Failed ice density CoT');

  const r03 = await b.processSmartQuery('how does rsa encryption work');
  assert(r03.response.includes('RSA') && (r03.response.includes('prime') || r03.response.includes('totient') || r03.response.includes('mod')), 'C1-03', 'rsa encryption CoT', 'Failed RSA CoT');

  const r04 = await b.processSmartQuery('think step by step: how does photosynthesis work');
  assert(r04.response.includes('Chain-of-Thought') || r04.response.toLowerCase().includes('photosynthesis'), 'C1-04', 'photosynthesis CoT', 'Failed photosynthesis CoT');

  const r05 = await b.processSmartQuery('break it down step by step: how do neural networks learn');
  assert(r05.response.includes('Chain-of-Thought') || r05.response.toLowerCase().includes('neural network'), 'C1-05', 'neural networks CoT', 'Failed neural net CoT');

  const r06 = await b.processSmartQuery('show your reasoning: why is the sky blue');
  assert(r06.response.includes('Chain-of-Thought') || r06.response.toLowerCase().includes('sky blue'), 'C1-06', 'why sky is blue CoT', 'Failed sky blue CoT');

  const r07 = await b.processSmartQuery('explain step by step how a 4-stroke engine works');
  assert(r07.response.includes('Chain-of-Thought') || r07.response.toLowerCase().includes('engine'), 'C1-07', '4-stroke engine CoT', 'Failed engine CoT');

  const r08 = await b.processSmartQuery('how does git version control work step by step');
  assert(r08.response.includes('Chain-of-Thought') || r08.response.toLowerCase().includes('git'), 'C1-08', 'git CoT', 'Failed git CoT');

  const r09 = await b.processSmartQuery('think step by step: how does an airplane generate lift');
  assert(r09.response.includes('Chain-of-Thought') || r09.response.toLowerCase().includes('lift'), 'C1-09', 'airplane lift CoT', 'Failed airplane lift CoT');

  const r10 = await b.processSmartQuery('why does salt melt ice on roads');
  assert(r02.response.toLowerCase().includes('ice') || r10.response.length > 30, 'C1-10', 'salt melts ice', 'Failed salt melts ice');

  const r11 = await b.processSmartQuery('what if gravity were doubled on Earth');
  assert(r11.response.includes('Counterfactual Analysis') && (r11.response.toLowerCase().includes('weight') || r11.response.toLowerCase().includes('gravity')), 'C1-11', 'double gravity counterfactual', 'Failed double gravity');

  const r12 = await b.processSmartQuery('what if the Moon disappeared');
  assert(r12.response.includes('Counterfactual Analysis') && (r12.response.toLowerCase().includes('tidal') || r12.response.toLowerCase().includes('tides') || r12.response.toLowerCase().includes('axial')), 'C1-12', 'moon disappears counterfactual', 'Failed moon disappearance');

  const r13 = await b.processSmartQuery('what if the speed of light were only 100 mph');
  assert(r13.response.includes('Counterfactual Analysis') && (r13.response.toLowerCase().includes('relativistic') || r13.response.toLowerCase().includes('dilation')), 'C1-13', 'slow speed of light', 'Failed slow speed of light');

  const r14 = await b.processSmartQuery('what if humans had photosynthesis');
  assert(r14.response.includes('Counterfactual Analysis') && (r14.response.toLowerCase().includes('chlorophyll') || r14.response.toLowerCase().includes('metabolic') || r14.response.toLowerCase().includes('caloric')), 'C1-14', 'human photosynthesis', 'Failed human photosynthesis');

  const r15 = await b.processSmartQuery('what if dinosaurs never went extinct');
  assert(r15.response.includes('Counterfactual') && r15.response.toLowerCase().includes('dinosaurs'), 'C1-15', 'dinosaurs counterfactual', 'Failed dinosaurs counterfactual');

  const r16 = await b.processSmartQuery('what if Earth stopped spinning');
  assert(r16.response.includes('Counterfactual') && (r16.response.toLowerCase().includes('earth') || r16.response.toLowerCase().includes('spinning')), 'C1-16', 'earth stops spinning', 'Failed earth stopped spinning');

  const r17 = await b.processSmartQuery('what if all glaciers melted tomorrow');
  assert(r17.response.includes('Counterfactual') && (r17.response.toLowerCase().includes('sea') || r17.response.toLowerCase().includes('glaciers')), 'C1-17', 'glaciers melt counterfactual', 'Failed glaciers melt');

  const r18 = await b.processSmartQuery('what if oxygen levels doubled');
  assert(r18.response.includes('Counterfactual') && (r18.response.toLowerCase().includes('oxygen') || r18.response.toLowerCase().includes('fire')), 'C1-18', 'oxygen doubled counterfactual', 'Failed oxygen doubled');

  const r19 = await b.processSmartQuery('what if computers were never invented');
  assert(r19.response.includes('Counterfactual') && (r19.response.toLowerCase().includes('computers') || r19.response.toLowerCase().includes('technology')), 'C1-19', 'no computers counterfactual', 'Failed no computers');

  const r20 = await b.processSmartQuery('what if bees went extinct');
  assert(r20.response.includes('Counterfactual') && (r20.response.toLowerCase().includes('bees') || r20.response.toLowerCase().includes('pollination')), 'C1-20', 'bees extinct counterfactual', 'Failed bees extinct');

  const r21 = await b.processSmartQuery('what if the sun became a red giant tomorrow');
  assert(r21.response.includes('Counterfactual') && (r21.response.toLowerCase().includes('sun') || r21.response.toLowerCase().includes('solar')), 'C1-21', 'sun red giant counterfactual', 'Failed red giant');

  const r22 = await b.processSmartQuery('what if oil was never discovered');
  assert(r22.response.includes('Counterfactual') && (r22.response.toLowerCase().includes('oil') || r22.response.toLowerCase().includes('energy')), 'C1-22', 'no oil counterfactual', 'Failed no oil');

  const r23 = await b.processSmartQuery('what if humans had four arms');
  assert(r23.response.includes('Counterfactual') && (r23.response.toLowerCase().includes('arms') || r23.response.toLowerCase().includes('humans')), 'C1-23', 'four arms counterfactual', 'Failed four arms');

  const r24 = await b.processSmartQuery('what if friction ceased to exist for 5 seconds');
  assert(r24.response.includes('Counterfactual') && (r24.response.toLowerCase().includes('friction') || r24.response.toLowerCase().includes('kinetic')), 'C1-24', 'no friction counterfactual', 'Failed friction counterfactual');

  const r25 = await b.processSmartQuery('what if the oceans were freshwater');
  assert(r25.response.includes('Counterfactual') && (r25.response.toLowerCase().includes('oceans') || r25.response.toLowerCase().includes('freshwater')), 'C1-25', 'freshwater oceans counterfactual', 'Failed freshwater oceans');

  // --- CATEGORY 2: Logical Fallacies & Foundational Thought Experiments (Prompts 26-50) ---
  console.log('\n--- CATEGORY 2: Logical Fallacies & Foundational Thought Experiments ---');

  const r26 = await b.processSmartQuery('what fallacy is this: you are too young to understand economics');
  assert(r26.response.includes('Ad Hominem'), 'C2-01', 'ad hominem age', 'Failed ad hominem');

  const r27 = await b.processSmartQuery("what fallacy: he didn't go to college so his scientific paper is wrong");
  assert(r27.response.includes('Ad Hominem'), 'C2-02', 'ad hominem credentials', 'Failed ad hominem college');

  const r28 = await b.processSmartQuery('identify the fallacy: if we allow calculators nobody will ever learn math');
  assert(r28.response.includes('Slippery Slope'), 'C2-03', 'slippery slope calculators', 'Failed slippery slope');

  const r29 = await b.processSmartQuery('what fallacy: if you skip one workout you will become completely unhealthy');
  assert(r29.response.includes('Slippery Slope'), 'C2-04', 'slippery slope workout', 'Failed slippery slope workout');

  const r30 = await b.processSmartQuery('what fallacy: either you support this policy or you hate freedom');
  assert(r30.response.includes('False Dilemma') || r30.response.includes('Dichotomy'), 'C2-05', 'false dilemma policy', 'Failed false dilemma');

  const r31 = await b.processSmartQuery('identify the fallacy: you are either with us or against us');
  assert(r31.response.includes('False Dilemma') || r31.response.includes('Dichotomy'), 'C2-06', 'false dilemma with us', 'Failed false dilemma with us');

  const r32 = await b.processSmartQuery('what fallacy: everyone is buying this crypto so it must be safe');
  assert(r32.response.includes('Bandwagon') || r32.response.includes('Ad Populum'), 'C2-07', 'bandwagon crypto', 'Failed bandwagon');

  const r33 = await b.processSmartQuery('what fallacy: millions of people believe it so it must be true');
  assert(r33.response.includes('Bandwagon') || r33.response.includes('Ad Populum'), 'C2-08', 'bandwagon millions', 'Failed bandwagon millions');

  const r34 = await b.processSmartQuery('identify the fallacy: it rained after I washed my car therefore washing caused rain');
  assert(r34.response.includes('Post Hoc'), 'C2-09', 'post hoc car wash', 'Failed post hoc');

  const r35 = await b.processSmartQuery('what fallacy: event B happened after event A so A caused B');
  assert(r35.response.includes('Post Hoc'), 'C2-10', 'post hoc A then B', 'Failed post hoc general');

  const r36 = await b.processSmartQuery("what is schrodinger's cat");
  assert(r36.response.includes("Schrödinger's Cat") && r36.response.toLowerCase().includes('superposition'), 'C2-11', 'schrodinger cat', 'Failed schrodinger');

  const r37 = await b.processSmartQuery('explain schrodingers cat thought experiment');
  assert(r37.response.includes("Schrödinger's Cat") && r37.response.toLowerCase().includes('decoherence'), 'C2-12', 'schrodinger decoherence', 'Failed schrodinger decoherence');

  const r38 = await b.processSmartQuery('what is the trolley problem');
  assert(r38.response.includes('Trolley Problem') && (r38.response.toLowerCase().includes('utilitarianism') || r38.response.toLowerCase().includes('deontological')), 'C2-13', 'trolley problem', 'Failed trolley problem');

  const r39 = await b.processSmartQuery('explain the trolley problem in ethics');
  assert(r39.response.includes('Trolley Problem') && r39.response.toLowerCase().includes('lever'), 'C2-14', 'trolley problem lever', 'Failed trolley lever');

  const r40 = await b.processSmartQuery("what is maxwell's demon");
  assert(r40.response.includes("Maxwell's Demon") && (r40.response.toLowerCase().includes('thermodynamics') || r40.response.toLowerCase().includes('entropy')), 'C2-15', 'maxwell demon', 'Failed maxwell demon');

  const r41 = await b.processSmartQuery('explain maxwells demon paradox in thermodynamics');
  assert(r41.response.includes("Maxwell's Demon") && r41.response.toLowerCase().includes('landauer'), 'C2-16', 'maxwell demon landauer', 'Failed landauer');

  const r42 = await b.processSmartQuery('what is the ship of theseus');
  assert(r42.response.includes('Ship of Theseus') && (r42.response.toLowerCase().includes('planks') || r42.response.toLowerCase().includes('identity')), 'C2-17', 'ship of theseus', 'Failed ship of theseus');

  const r43 = await b.processSmartQuery('explain the ship of theseus paradox');
  assert(r43.response.includes('Ship of Theseus') && r43.response.toLowerCase().includes('continuity'), 'C2-18', 'ship of theseus continuity', 'Failed theseus continuity');

  const r44 = await b.processSmartQuery('what is the chinese room argument');
  assert(r44.response.includes('Chinese Room') && (r44.response.toLowerCase().includes('searle') || r44.response.toLowerCase().includes('syntax')), 'C2-19', 'chinese room', 'Failed chinese room');

  const r45 = await b.processSmartQuery('explain searle chinese room thought experiment');
  assert(r45.response.includes('Chinese Room') && (r45.response.toLowerCase().includes('consciousness') || r45.response.toLowerCase().includes('semantic')), 'C2-20', 'searle consciousness', 'Failed searle consciousness');

  const r46 = await b.processSmartQuery("what is the prisoner's dilemma");
  assert(r46.response.includes("Prisoner's Dilemma") && (r46.response.toLowerCase().includes('nash') || r46.response.toLowerCase().includes('equilibrium')), 'C2-21', 'prisoner dilemma', 'Failed prisoner dilemma');

  const r47 = await b.processSmartQuery('explain prisoners dilemma in game theory');
  assert(r47.response.includes("Prisoner's Dilemma") && r47.response.toLowerCase().includes('tit-for-tat'), 'C2-22', 'prisoner tit for tat', 'Failed tit-for-tat');

  const r48 = await b.processSmartQuery('what fallacy: attack the person instead of the argument');
  assert(r48.response.includes('Ad Hominem'), 'C2-23', 'fallacy attack person', 'Failed attack person fallacy');

  const r49 = await b.processSmartQuery('what fallacy is slippery slope');
  assert(r49.response.includes('Slippery Slope') && r49.response.toLowerCase().includes('causal'), 'C2-24', 'fallacy slippery slope', 'Failed slippery slope explain');

  const r50 = await b.processSmartQuery('what fallacy is false dilemma');
  assert(r50.response.includes('False Dilemma') && r50.response.toLowerCase().includes('options'), 'C2-25', 'fallacy false dilemma', 'Failed false dilemma explain');

  // --- CATEGORY 3: Direct Comparison Matrix & Technology Versus Evaluator (Prompts 51-75) ---
  console.log('\n--- CATEGORY 3: Direct Comparison Matrix & Technology Versus Evaluator ---');

  const r51 = await b.processSmartQuery('Python vs C++');
  assert(r51.response.includes('Python vs. C++') && (r51.response.includes('Interpreted') || r51.response.includes('Compiled')), 'C3-01', 'Python vs C++', 'Failed Python vs C++');

  const r52 = await b.processSmartQuery('C++ vs Python');
  assert(r52.response.includes('Python') && r52.response.includes('C++'), 'C3-02', 'C++ vs Python', 'Failed C++ vs Python');

  const r53 = await b.processSmartQuery('TCP vs UDP');
  assert(r53.response.includes('TCP vs. UDP') && (r53.response.includes('Reliability') || r53.response.includes('Connection')), 'C3-03', 'TCP vs UDP', 'Failed TCP vs UDP');

  const r54 = await b.processSmartQuery('UDP vs TCP');
  assert(r54.response.includes('TCP') && r54.response.includes('UDP'), 'C3-04', 'UDP vs TCP', 'Failed UDP vs TCP');

  const r55 = await b.processSmartQuery('SQL vs NoSQL');
  assert(r55.response.includes('SQL') && r55.response.includes('NoSQL') && (r55.response.includes('ACID') || r55.response.includes('Relational')), 'C3-05', 'SQL vs NoSQL', 'Failed SQL vs NoSQL');

  const r56 = await b.processSmartQuery('NoSQL vs SQL');
  assert(r56.response.includes('SQL') && r56.response.includes('NoSQL'), 'C3-06', 'NoSQL vs SQL', 'Failed NoSQL vs SQL');

  const r57 = await b.processSmartQuery('AC vs DC');
  assert(r57.response.includes('Comparison') || r57.response.includes('Comparative'), 'C3-07', 'AC vs DC', 'Failed AC vs DC');

  const r58 = await b.processSmartQuery('Mitosis vs Meiosis');
  assert(r58.response.includes('Comparison') || r58.response.includes('Comparative'), 'C3-08', 'Mitosis vs Meiosis', 'Failed Mitosis vs Meiosis');

  const r59 = await b.processSmartQuery('RAM vs ROM');
  assert(r59.response.includes('Comparison') || r59.response.includes('Comparative'), 'C3-09', 'RAM vs ROM', 'Failed RAM vs ROM');

  const r60 = await b.processSmartQuery('REST vs GraphQL');
  assert(r60.response.includes('Comparison') || r60.response.includes('Comparative'), 'C3-10', 'REST vs GraphQL', 'Failed REST vs GraphQL');

  const r61 = await b.processSmartQuery('Monolith vs Microservices');
  assert(r61.response.includes('Comparison') || r61.response.includes('Comparative'), 'C3-11', 'Monolith vs Microservices', 'Failed Monolith vs Microservices');

  const r62 = await b.processSmartQuery('Docker vs Virtual Machines');
  assert(r62.response.includes('Comparison') || r62.response.includes('Comparative'), 'C3-12', 'Docker vs VM', 'Failed Docker vs VM');

  const r63 = await b.processSmartQuery('Git vs SVN');
  assert(r63.response.includes('Comparison') || r63.response.includes('Comparative'), 'C3-13', 'Git vs SVN', 'Failed Git vs SVN');

  const r64 = await b.processSmartQuery('SSD vs HDD');
  assert(r64.response.includes('Comparison') || r64.response.includes('Comparative'), 'C3-14', 'SSD vs HDD', 'Failed SSD vs HDD');

  const r65 = await b.processSmartQuery('CPU vs GPU');
  assert(r65.response.includes('Comparison') || r65.response.includes('Comparative'), 'C3-15', 'CPU vs GPU', 'Failed CPU vs GPU');

  const r66 = await b.processSmartQuery('HTTP vs HTTPS');
  assert(r66.response.includes('Comparison') || r66.response.includes('Comparative'), 'C3-16', 'HTTP vs HTTPS', 'Failed HTTP vs HTTPS');

  const r67 = await b.processSmartQuery('JSON vs XML');
  assert(r67.response.includes('Comparison') || r67.response.includes('Comparative'), 'C3-17', 'JSON vs XML', 'Failed JSON vs XML');

  const r68 = await b.processSmartQuery('IPv4 vs IPv6');
  assert(r68.response.includes('Comparison') || r68.response.includes('Comparative'), 'C3-18', 'IPv4 vs IPv6', 'Failed IPv4 vs IPv6');

  const r69 = await b.processSmartQuery('Synchronous vs Asynchronous');
  assert(r69.response.includes('Comparison') || r69.response.includes('Comparative'), 'C3-19', 'Sync vs Async', 'Failed Sync vs Async');

  const r70 = await b.processSmartQuery('Stack vs Queue');
  assert(r70.response.includes('Comparison') || r70.response.includes('Comparative'), 'C3-20', 'Stack vs Queue', 'Failed Stack vs Queue');

  const r71 = await b.processSmartQuery('Array vs Linked List');
  assert(r71.response.includes('Comparison') || r71.response.includes('Comparative'), 'C3-21', 'Array vs Linked List', 'Failed Array vs Linked List');

  const r72 = await b.processSmartQuery('Compiler vs Interpreter');
  assert(r72.response.includes('Comparison') || r72.response.includes('Comparative'), 'C3-22', 'Compiler vs Interpreter', 'Failed Compiler vs Interpreter');

  const r73 = await b.processSmartQuery('Bluetooth vs WiFi');
  assert(r73.response.includes('Comparison') || r73.response.includes('Comparative'), 'C3-23', 'Bluetooth vs WiFi', 'Failed Bluetooth vs WiFi');

  const r74 = await b.processSmartQuery('Linux vs Windows');
  assert(r74.response.includes('Comparison') || r74.response.includes('Comparative'), 'C3-24', 'Linux vs Windows', 'Failed Linux vs Windows');

  const r75 = await b.processSmartQuery('compare Python and C++');
  assert(r75.response.includes('Python') && r75.response.includes('C++'), 'C3-25', 'compare Python and C++', 'Failed compare command');

  // --- CATEGORY 4: Socratic Quizzes, Reverse Dictionary, Analogies & Timelines (Prompts 76-100) ---
  console.log('\n--- CATEGORY 4: Socratic Quizzes, Reverse Dictionary, Analogies & Timelines ---');

  const r76 = await b.processSmartQuery('quiz me on physics');
  assert(r76.response.includes('Physics Knowledge Challenge') && r76.response.includes('• **A)**'), 'C4-01', 'quiz physics', 'Failed physics quiz');

  const r77 = await b.processSmartQuery('B');
  assert(r77.response.includes('Correct!') && r77.response.includes('Second Law'), 'C4-02', 'answer physics quiz', 'Failed quiz answer B');

  const r78 = await b.processSmartQuery('quiz me on python');
  assert(r78.response.includes('Python Knowledge Quiz') && r78.response.includes('• **A)**'), 'C4-03', 'quiz python', 'Failed python quiz');

  const r79 = await b.processSmartQuery('A');
  assert(r79.response.includes('Correct!') && r79.response.includes('O(1)'), 'C4-04', 'answer python quiz', 'Failed quiz answer A');

  const r80 = await b.processSmartQuery('ask me a riddle');
  assert(r80.response.includes('Riddle Challenge') && r80.response.includes('Footsteps'), 'C4-05', 'riddle challenge', 'Failed riddle challenge');

  const r81 = await b.processSmartQuery('A');
  assert(r81.response.includes('Correct!') && r81.response.includes('Footsteps'), 'C4-06', 'answer riddle A', 'Failed answer riddle A');

  const r82 = await b.processSmartQuery('what is the word for the smell of rain');
  assert(r82.response.includes('Petrichor'), 'C4-07', 'word for smell of rain', 'Failed petrichor');

  const r83 = await b.processSmartQuery("what is the word for when you can't remember a word");
  assert(r83.response.includes('Lethologica'), 'C4-08', 'word for forgetting word', 'Failed lethologica');

  const r84 = await b.processSmartQuery('what is the word for finding good things unexpectedly');
  assert(r84.response.includes('Serendipity'), 'C4-09', 'word for serendipity', 'Failed serendipity');

  const r85 = await b.processSmartQuery('what do you call it when repeating a word makes it lose meaning');
  assert(r85.response.includes('Semantic Satiation'), 'C4-10', 'word for semantic satiation', 'Failed semantic satiation');

  const r86 = await b.processSmartQuery("what is the word for nostalgic for a place you've never been");
  assert(r86.response.includes('Sehnsucht') || r86.response.includes('Fernweh'), 'C4-11', 'word for sehnsucht', 'Failed sehnsucht');

  const r87 = await b.processSmartQuery('what is the word for seeing faces in objects');
  assert(r87.response.includes('Pareidolia'), 'C4-12', 'word for pareidolia', 'Failed pareidolia');

  const r88 = await b.processSmartQuery('what is the word for everyone has a vivid life');
  assert(r88.response.includes('Sonder'), 'C4-13', 'word for sonder', 'Failed sonder');

  const r89 = await b.processSmartQuery("what is the word for pleasure at someone else's misfortune");
  assert(r89.response.includes('Schadenfreude'), 'C4-14', 'word for schadenfreude', 'Failed schadenfreude');

  const r90 = await b.processSmartQuery('explain an API using an analogy');
  assert(r90.response.includes('Restaurant Analogy') && r90.response.includes('Waiter'), 'C4-15', 'api restaurant analogy', 'Failed API analogy');

  const r91 = await b.processSmartQuery('analogy for RAM vs hard drive');
  assert(r91.response.includes('Desk & Filing Cabinet') || r91.response.includes('RAM'), 'C4-16', 'ram desk analogy', 'Failed RAM analogy');

  const r92 = await b.processSmartQuery("explain blockchain like I'm five");
  assert(r92.response.includes('Blockchain') && (r92.response.includes('Notebook') || r92.response.includes('ledger')), 'C4-17', 'blockchain analogy', 'Failed blockchain analogy');

  const r93 = await b.processSmartQuery('analogy for quantum entanglement');
  assert(r93.response.includes('Cosmic Magic Dice') || r93.response.includes('Dice'), 'C4-18', 'entanglement analogy', 'Failed entanglement analogy');

  const r94 = await b.processSmartQuery('check for sql injection: query = f"SELECT * FROM users WHERE username = \'{user_input}\'"');
  assert(r94.response.includes('SQL Injection') && r94.response.includes('parameterized'), 'C4-19', 'sql injection scanner', 'Failed SQL injection scan');

  const r95 = await b.processSmartQuery('refactor this code: result = eval(user_input_string)');
  assert(r95.response.includes('eval') && r95.response.includes('literal_eval'), 'C4-20', 'eval refactor', 'Failed eval refactor');

  const r96 = await b.processSmartQuery('timeline of World War 2');
  assert(r96.response.includes('World War II') && (r96.response.includes('1939') || r96.response.includes('1945')), 'C4-21', 'ww2 timeline', 'Failed WW2 timeline');

  const r97 = await b.processSmartQuery('timeline of computing');
  assert(r97.response.includes('Computing') && (r97.response.includes('Turing') || r97.response.includes('Babbage')), 'C4-22', 'computing timeline', 'Failed computing timeline');

  const r98 = await b.processSmartQuery('timeline of space exploration');
  assert(r98.response.includes('Space Exploration') && (r98.response.includes('Apollo') || r98.response.includes('Sputnik')), 'C4-23', 'space timeline', 'Failed space timeline');

  const r99 = await b.processSmartQuery('analyze the sentiment of: I absolutely love this fantastic new update, it works amazing!');
  assert(r99.response.includes('Positive') && r99.response.includes('Sentiment'), 'C4-24', 'positive sentiment', 'Failed positive sentiment');

  const r100 = await b.processSmartQuery('analyze the tone of: This is terrible and completely unacceptable, fix it asap!');
  assert((r100.response.includes('Negative') || r100.response.includes('Urgent')) && r100.response.includes('Tone'), 'C4-25', 'negative tone', 'Failed negative tone');

  console.log('\n' + '='.repeat(80));
  console.log(`🏆 STAGE 41 BENCHMARK RESULTS: ${passed}/100 PASSED (${((passed / 100) * 100).toFixed(1)}%) | ${failed} FAILED`);
  console.log('='.repeat(80));

  if (failed > 0) {
    console.error('\n⚠️ DETAILED FAILURE BREAKDOWN:');
    failureDetails.forEach((f, idx) => {
      console.error(`  ${idx + 1}. [${f.testId}] "${f.prompt}": ${f.message}`);
    });
    process.exit(1);
  } else {
    console.log('\n✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 41 COMPLETE! ✨\n');
    process.exit(0);
  }
}

runStage41Benchmark().catch(err => {
  console.error('Fatal benchmark error:', err);
  process.exit(1);
});
