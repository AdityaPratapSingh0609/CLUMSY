/**
 * Stage 45 100-Prompt & 100-Test Impressive Benchmark Suite
 * Covers Bugs #133–#144:
 *   - Category 1: Spoken Voice Volume & Speech Rate Commands (25 prompts)
 *   - Category 2: Chain-of-Thought (CoT) & Classic Logic Riddles (25 prompts)
 *   - Category 3: Financial Math & Amortization Calculations (25 prompts)
 *   - Category 4: Code Refactoring, Socratic Clarification & Cognitive Intactness (25 prompts)
 */

const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');

let passed = 0;
let failed = 0;
const failureDetails = [];

function assert(condition, testId, prompt, failMsg) {
  if (condition) {
    passed++;
    console.log(`  ✅ [PASS #${String(passed).padStart(3, '0')}] [${testId}] "${prompt}"`);
  } else {
    failed++;
    console.error(`  ❌ [FAIL #${String(failed).padStart(3, '0')}] [${testId}] "${prompt}" -> ${failMsg}`);
    failureDetails.push({ testId, prompt, failMsg });
  }
}

async function runStage45Benchmark() {
  console.log('='.repeat(80));
  console.log('🚀 RUNNING STAGE 45: 100-PROMPT BENCHMARK (VOICE, COT, SOCRATIC & FINANCIAL MATH)');
  console.log('='.repeat(80));
  console.log('');

  const brain = new ClumsyBrainEngine();

  // =========================================================================
  // CATEGORY 1: Spoken Voice Volume & Speech Rate Commands (25 prompts)
  // =========================================================================
  console.log('--- CATEGORY 1: Spoken Voice Volume & Speech Rate Commands ---');

  // 1. Speak slower
  let r = await brain.processSmartQuery('speak slower');
  assert(r.response.toLowerCase().includes('speech rate') || r.response.toLowerCase().includes('slower') || brain.ttsRate < 1.0, 'C1-01', 'speak slower', 'Failed speak slower');

  // 2. Talk slower
  r = await brain.processSmartQuery('talk slower');
  assert(r.response.toLowerCase().includes('speech rate') || r.response.toLowerCase().includes('slower'), 'C1-02', 'talk slower', 'Failed talk slower');

  // 3. Slow down your voice
  r = await brain.processSmartQuery('slow down your voice');
  assert(r.response.toLowerCase().includes('speech rate') || r.response.toLowerCase().includes('slower'), 'C1-03', 'slow down your voice', 'Failed slow down voice');

  // 4. Decrease speed
  r = await brain.processSmartQuery('decrease speed');
  assert(r.response.toLowerCase().includes('speech rate') || r.response.toLowerCase().includes('slower'), 'C1-04', 'decrease speed', 'Failed decrease speed');

  // 5. Normal speed
  r = await brain.processSmartQuery('normal speed');
  assert(brain.ttsRate === 1.0 && (r.response.toLowerCase().includes('normal') || r.response.toLowerCase().includes('1.0x')), 'C1-05', 'normal speed', 'Failed normal speed');

  // 6. Speak faster
  r = await brain.processSmartQuery('speak faster');
  assert(r.response.toLowerCase().includes('faster') || brain.ttsRate > 1.0, 'C1-06', 'speak faster', 'Failed speak faster');

  // 7. Talk faster
  r = await brain.processSmartQuery('talk faster');
  assert(r.response.toLowerCase().includes('faster'), 'C1-07', 'talk faster', 'Failed talk faster');

  // 8. Speed up your voice
  r = await brain.processSmartQuery('speed up your voice');
  assert(r.response.toLowerCase().includes('faster'), 'C1-08', 'speed up your voice', 'Failed speed up voice');

  // 9. Increase speed
  r = await brain.processSmartQuery('increase speed');
  assert(r.response.toLowerCase().includes('faster'), 'C1-09', 'increase speed', 'Failed increase speed');

  // 10. Reset speech rate
  r = await brain.processSmartQuery('reset speech rate');
  assert(brain.ttsRate === 1.0, 'C1-10', 'reset speech rate', 'Failed reset speech rate');

  // 11. Set volume to 80%
  r = await brain.processSmartQuery('set volume to 80%');
  assert(brain.ttsVolume === 0.8 && r.response.includes('80%'), 'C1-11', 'set volume to 80%', 'Failed volume 80%');

  // 12. Volume 50%
  r = await brain.processSmartQuery('volume 50%');
  assert(brain.ttsVolume === 0.5 && r.response.includes('50%'), 'C1-12', 'volume 50%', 'Failed volume 50%');

  // 13. Set the volume to 100%
  r = await brain.processSmartQuery('set the volume to 100%');
  assert(brain.ttsVolume === 1.0 && r.response.includes('100%'), 'C1-13', 'set the volume to 100%', 'Failed volume 100%');

  // 14. Volume 20%
  r = await brain.processSmartQuery('volume 20%');
  assert(brain.ttsVolume === 0.2 && r.response.includes('20%'), 'C1-14', 'volume 20%', 'Failed volume 20%');

  // 15. Set voice volume to 10%
  r = await brain.processSmartQuery('set voice volume to 10%');
  assert(brain.ttsVolume === 0.1 && r.response.includes('10%'), 'C1-15', 'set voice volume to 10%', 'Failed voice volume 10%');

  // 16. Turn up the volume
  r = await brain.processSmartQuery('turn up the volume');
  assert(brain.ttsVolume >= 0.3 && (r.response.toLowerCase().includes('increased') || r.response.toLowerCase().includes('volume')), 'C1-16', 'turn up the volume', 'Failed turn up volume');

  // 17. Turn volume up
  r = await brain.processSmartQuery('turn volume up');
  assert(r.response.toLowerCase().includes('increased'), 'C1-17', 'turn volume up', 'Failed turn volume up');

  // 18. Louder
  r = await brain.processSmartQuery('louder');
  assert(r.response.toLowerCase().includes('increased') || r.response.toLowerCase().includes('volume'), 'C1-18', 'louder', 'Failed louder');

  // 19. Increase volume
  r = await brain.processSmartQuery('increase volume');
  assert(r.response.toLowerCase().includes('increased'), 'C1-19', 'increase volume', 'Failed increase volume');

  // 20. Turn down the volume
  r = await brain.processSmartQuery('turn down the volume');
  assert(r.response.toLowerCase().includes('decreased'), 'C1-20', 'turn down the volume', 'Failed turn down volume');

  // 21. Turn volume down
  r = await brain.processSmartQuery('turn volume down');
  assert(r.response.toLowerCase().includes('decreased'), 'C1-21', 'turn volume down', 'Failed turn volume down');

  // 22. Quieter
  r = await brain.processSmartQuery('quieter');
  assert(r.response.toLowerCase().includes('decreased') || r.response.toLowerCase().includes('volume'), 'C1-22', 'quieter', 'Failed quieter');

  // 23. Mute voice
  r = await brain.processSmartQuery('mute voice');
  assert(brain.ttsMuted === true && r.response.toLowerCase().includes('muted'), 'C1-23', 'mute voice', 'Failed mute voice');

  // 24. Unmute voice
  r = await brain.processSmartQuery('unmute voice');
  assert(brain.ttsMuted === false && r.response.toLowerCase().includes('unmuted'), 'C1-24', 'unmute voice', 'Failed unmute voice');

  // 25. Silence voice
  r = await brain.processSmartQuery('silence voice');
  assert(brain.ttsMuted === true && r.response.toLowerCase().includes('muted'), 'C1-25', 'silence voice', 'Failed silence voice');

  brain.ttsMuted = false;

  // =========================================================================
  // CATEGORY 2: Chain-of-Thought (CoT) & Classic Logic Riddles (25 prompts)
  // =========================================================================
  console.log('');
  console.log('--- CATEGORY 2: Chain-of-Thought (CoT) & Classic Logic Riddles ---');

  // 26. River crossing (wolf, goat, cabbage)
  r = await brain.processSmartQuery('how to get the wolf, goat, and cabbage across the river');
  assert(r.response.includes('Goat') && r.response.includes('7 steps'), 'C2-01', 'river crossing riddle', 'Failed river crossing');

  // 27. River crossing variant (fox, goose, grain)
  r = await brain.processSmartQuery('cross river with fox, goose, and grain in a boat');
  assert(r.response.includes('Goat') || r.response.includes('7 steps') || r.response.includes('River Crossing'), 'C2-02', 'cross river fox goose grain', 'Failed river crossing variant');

  // 28. River crossing question
  r = await brain.processSmartQuery('can the farmer cross the river with wolf, goat, and cabbage safely');
  assert(r.response.includes('7 steps') || r.response.includes('Goat'), 'C2-03', 'farmer river crossing', 'Failed farmer river crossing');

  // 29. Monty Hall problem
  r = await brain.processSmartQuery('should i switch doors in the monty hall problem');
  assert(r.response.toLowerCase().includes('switch') && (r.response.includes('2/3') || r.response.includes('66.7%')), 'C2-04', 'monty hall problem', 'Failed monty hall');

  // 30. Three doors one car
  r = await brain.processSmartQuery('three doors one car and two goats should i switch');
  assert(r.response.toLowerCase().includes('switch'), 'C2-05', 'three doors one car', 'Failed three doors one car');

  // 31. Switch doors or stay
  r = await brain.processSmartQuery('in monty hall should you switch or stay');
  assert(r.response.toLowerCase().includes('switch'), 'C2-06', 'switch or stay', 'Failed switch or stay');

  // 32. Bridge and torch
  r = await brain.processSmartQuery('bridge and torch problem with four people');
  assert(r.response.includes('17 minutes') || r.response.includes('17 Minutes'), 'C2-07', 'bridge and torch problem', 'Failed bridge and torch');

  // 33. Four people crossing bridge
  r = await brain.processSmartQuery('four people crossing a bridge at night with one flashlight');
  assert(r.response.includes('17 min') || r.response.includes('17 Minutes'), 'C2-08', 'four people bridge', 'Failed four people bridge');

  // 34. Flashlight bridge riddle
  r = await brain.processSmartQuery('flashlight bridge riddle schedule');
  assert(r.response.includes('17 min') || r.response.includes('17 Minutes'), 'C2-09', 'flashlight bridge riddle', 'Failed flashlight bridge riddle');

  // 35. Three mislabelled boxes
  r = await brain.processSmartQuery('three mislabelled boxes of apples and oranges');
  assert(r.response.includes('Mixed') && (r.response.includes('1 fruit') || r.response.includes('Apples')), 'C2-10', 'three mislabelled boxes', 'Failed three mislabelled boxes');

  // 36. Apples and oranges boxes
  r = await brain.processSmartQuery('all three boxes are incorrectly labeled with apples and oranges');
  assert(r.response.includes('Mixed'), 'C2-11', 'all boxes incorrectly labeled', 'Failed boxes incorrectly labeled');

  // 37. Explicit CoT: think step by step
  r = await brain.processSmartQuery('think step by step: how to design a distributed cache');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-12', 'think step by step distributed cache', 'Failed CoT distributed cache');

  // 38. Show your reasoning: rocket stages
  r = await brain.processSmartQuery('show your reasoning: why multistage rockets are needed for orbit');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-13', 'show your reasoning rocket', 'Failed CoT rocket');

  // 39. Explain your thought process
  r = await brain.processSmartQuery('explain your thought process: selecting between rust and go for microservices');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-14', 'explain thought process rust go', 'Failed CoT rust go');

  // 40. Step by step reasoning: why hash map is O(1)
  r = await brain.processSmartQuery('step by step reasoning: why hash map average lookup is constant time');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-15', 'step by step hash map', 'Failed CoT hash map');

  // 41. Think step by step: sorting algorithms
  r = await brain.processSmartQuery('think step by step: quicksort vs mergesort memory consumption');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-16', 'think step by step sorting', 'Failed CoT sorting');

  // 42. Show your reasoning: p vs np
  r = await brain.processSmartQuery('show your reasoning: the difference between p and np completeness');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-17', 'show your reasoning p vs np', 'Failed CoT p vs np');

  // 43. River crossing: how to cross boat with wolf and goat
  r = await brain.processSmartQuery('how does the farmer take wolf goat and cabbage across');
  assert(r.response.includes('Goat') && r.response.includes('7 steps'), 'C2-18', 'farmer takes wolf goat cabbage', 'Failed river crossing');

  // 44. Monty hall why switch
  r = await brain.processSmartQuery('why is switching doors better in monty hall');
  assert(r.response.includes('2/3') || r.response.includes('66.7%'), 'C2-19', 'why switching doors better', 'Failed monty hall why switch');

  // 45. Bridge and torch optimal time
  r = await brain.processSmartQuery('what is the optimal time for the bridge and torch problem');
  assert(r.response.includes('17'), 'C2-20', 'optimal time bridge torch', 'Failed bridge torch time');

  // 46. Three boxes riddle
  r = await brain.processSmartQuery('which box should you pick from in the three mislabelled boxes');
  assert(r.response.includes('Mixed'), 'C2-21', 'which box pick three mislabelled', 'Failed pick box');

  // 47. Think step by step: tcp handshake
  r = await brain.processSmartQuery('think step by step: three way tcp handshake establishment');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-22', 'tcp handshake CoT', 'Failed CoT tcp');

  // 48. Show reasoning: raft consensus
  r = await brain.processSmartQuery('show your reasoning: raft consensus leader election');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-23', 'raft consensus CoT', 'Failed CoT raft');

  // 49. Step by step reasoning: database sharding
  r = await brain.processSmartQuery('step by step reasoning: consistent hashing in distributed databases');
  assert(r.response.includes('Chain of Thought') || r.response.includes('Step-by-Step'), 'C2-24', 'consistent hashing CoT', 'Failed CoT consistent hashing');

  // 50. River crossing cabbage riddle
  r = await brain.processSmartQuery('wolf goat and cabbage river crossing riddle');
  assert(r.response.includes('7 steps'), 'C2-25', 'wolf goat cabbage river riddle', 'Failed river crossing riddle');

  // =========================================================================
  // CATEGORY 3: Financial Math & Amortization Calculations (25 prompts)
  // =========================================================================
  console.log('');
  console.log('--- CATEGORY 3: Financial Math & Amortization Calculations ---');

  // 51. Compound interest 1000 at 5% for 3 years -> 1157.63
  r = await brain.processSmartQuery('compound interest on 1000 at 5% for 3 years');
  assert(r.response.includes('1,157.63') || r.response.includes('1157.63'), 'C3-01', 'compound interest 1000 at 5% for 3 years', 'Failed comp interest 1000 5% 3y');

  // 52. Compound interest $5000 at 7% for 5 years -> 7012.76
  r = await brain.processSmartQuery('compound interest on $5,000 at 7% for 5 years');
  assert(r.response.includes('7,012.76') || r.response.includes('7012.76'), 'C3-02', 'compound interest 5000 at 7% for 5 years', 'Failed comp interest 5000 7% 5y');

  // 53. Compound interest 10000 at 8% for 4 years -> 13604.89
  r = await brain.processSmartQuery('compound interest on 10000 at 8% for 4 years');
  assert(r.response.includes('13,604.89') || r.response.includes('13604.89'), 'C3-03', 'compound interest 10000 at 8% for 4 years', 'Failed comp interest 10000 8% 4y');

  // 54. Compound interest on 2500 at 4% for 2 years -> 2704.00
  r = await brain.processSmartQuery('compound interest on 2500 at 4% for 2 years');
  assert(r.response.includes('2,704') || r.response.includes('2704'), 'C3-04', 'compound interest 2500 at 4% for 2 years', 'Failed comp interest 2500 4% 2y');

  // 55. Compound interest on $20,000 at 6% for 3 years -> 23820.32
  r = await brain.processSmartQuery('compound interest on $20,000 at 6% for 3 years');
  assert(r.response.includes('23,820.32') || r.response.includes('23820.32'), 'C3-05', 'compound interest 20000 at 6% for 3 years', 'Failed comp interest 20000 6% 3y');

  // 56. Compound interest on 500 at 10% for 2 years -> 605.00
  r = await brain.processSmartQuery('compound interest on 500 at 10% for 2 years');
  assert(r.response.includes('605'), 'C3-06', 'compound interest 500 at 10% for 2 years', 'Failed comp interest 500 10% 2y');

  // 57. Compound interest on 12000 at 5% for 1 year -> 12600.00
  r = await brain.processSmartQuery('compound interest on 12000 at 5% for 1 year');
  assert(r.response.includes('12,600') || r.response.includes('12600'), 'C3-07', 'compound interest 12000 at 5% for 1 year', 'Failed comp interest 12000 5% 1y');

  // 58. Compound interest on 100000 at 7% for 10 years -> 196715.14
  r = await brain.processSmartQuery('compound interest on 100000 at 7% for 10 years');
  assert(r.response.includes('196,715.14') || r.response.includes('196715.14'), 'C3-08', 'compound interest 100000 at 7% for 10 years', 'Failed comp interest 100000 7% 10y');

  // 59. Simple interest on 5000 at 4% for 2 years -> 400.00
  r = await brain.processSmartQuery('simple interest on 5000 at 4% for 2 years');
  assert(r.response.includes('400.00') && (r.response.includes('5,400.00') || r.response.includes('5400.00')), 'C3-09', 'simple interest 5000 at 4% for 2 years', 'Failed simple interest 5000 4% 2y');

  // 60. Simple interest on 1000 at 5% for 3 years -> 150.00
  r = await brain.processSmartQuery('simple interest on 1000 at 5% for 3 years');
  assert(r.response.includes('150.00') && (r.response.includes('1,150.00') || r.response.includes('1150.00')), 'C3-10', 'simple interest 1000 at 5% for 3 years', 'Failed simple interest 1000 5% 3y');

  // 61. Simple interest on 2000 at 6% for 5 years -> 600.00
  r = await brain.processSmartQuery('simple interest on 2000 at 6% for 5 years');
  assert(r.response.includes('600.00') && (r.response.includes('2,600.00') || r.response.includes('2600.00')), 'C3-11', 'simple interest 2000 at 6% for 5 years', 'Failed simple interest 2000 6% 5y');

  // 62. Simple interest on 10000 at 7% for 3 years -> 2100.00
  r = await brain.processSmartQuery('simple interest on 10000 at 7% for 3 years');
  assert(r.response.includes('2,100.00') || r.response.includes('2100.00'), 'C3-12', 'simple interest 10000 at 7% for 3 years', 'Failed simple interest 10000 7% 3y');

  // 63. Simple interest on $50,000 at 3% for 1 year -> 1500.00
  r = await brain.processSmartQuery('simple interest on $50,000 at 3% for 1 year');
  assert(r.response.includes('1,500.00') || r.response.includes('1500.00'), 'C3-13', 'simple interest 50000 at 3% for 1 year', 'Failed simple interest 50000 3% 1y');

  // 64. Simple interest on 3000 at 8% for 2 years -> 480.00
  r = await brain.processSmartQuery('simple interest on 3000 at 8% for 2 years');
  assert(r.response.includes('480.00'), 'C3-14', 'simple interest 3000 at 8% for 2 years', 'Failed simple interest 3000 8% 2y');

  // 65. Simple interest on 8000 at 5% for 4 years -> 1600.00
  r = await brain.processSmartQuery('simple interest on 8000 at 5% for 4 years');
  assert(r.response.includes('1,600.00') || r.response.includes('1600.00'), 'C3-15', 'simple interest 8000 at 5% for 4 years', 'Failed simple interest 8000 5% 4y');

  // 66. Simple interest on 15000 at 4% for 3 years -> 1800.00
  r = await brain.processSmartQuery('simple interest on 15000 at 4% for 3 years');
  assert(r.response.includes('1,800.00') || r.response.includes('1800.00'), 'C3-16', 'simple interest 15000 at 4% for 3 years', 'Failed simple interest 15000 4% 3y');

  // 67. Monthly payment for 200000 at 6% for 30 years -> 1199.10
  r = await brain.processSmartQuery('monthly payment for 200000 at 6% for 30 years');
  assert(r.response.includes('1,199.10') || r.response.includes('1199.10'), 'C3-17', 'monthly payment 200000 at 6% for 30 years', 'Failed monthly payment 200000 6% 30y');

  // 68. Mortgage payment for 300000 at 7% for 15 years -> 2696.48
  r = await brain.processSmartQuery('mortgage payment for 300000 at 7% for 15 years');
  assert(r.response.includes('2,696.48') || r.response.includes('2696.48'), 'C3-18', 'mortgage payment 300000 at 7% for 15 years', 'Failed mortgage payment 300000 7% 15y');

  // 69. Loan payment for 25000 at 5% for 5 years -> 471.78
  r = await brain.processSmartQuery('loan payment for 25000 at 5% for 5 years');
  assert(r.response.includes('471.78'), 'C3-19', 'loan payment 25000 at 5% for 5 years', 'Failed loan payment 25000 5% 5y');

  // 70. Monthly payment for $400,000 at 6.5% for 30 years -> 2528.27
  r = await brain.processSmartQuery('monthly payment for $400,000 at 6.5% for 30 years');
  assert(r.response.includes('2,528.27') || r.response.includes('2528.27'), 'C3-20', 'monthly payment 400000 at 6.5% for 30 years', 'Failed monthly payment 400000 6.5% 30y');

  // 71. Loan payment for 50000 at 4.5% for 10 years -> 518.19
  r = await brain.processSmartQuery('loan payment for 50000 at 4.5% for 10 years');
  assert(r.response.includes('518.19'), 'C3-21', 'loan payment 50000 at 4.5% for 10 years', 'Failed loan payment 50000 4.5% 10y');

  // 72. Mortgage payment for 250000 at 5.5% for 30 years -> 1419.47
  r = await brain.processSmartQuery('mortgage payment for 250000 at 5.5% for 30 years');
  assert(r.response.includes('1,419.47') || r.response.includes('1419.47'), 'C3-22', 'mortgage payment 250000 at 5.5% for 30 years', 'Failed mortgage payment 250000 5.5% 30y');

  // 73. Monthly payment for 100000 at 8% for 20 years -> 836.44
  r = await brain.processSmartQuery('monthly payment for 100000 at 8% for 20 years');
  assert(r.response.includes('836.44'), 'C3-23', 'monthly payment 100000 at 8% for 20 years', 'Failed monthly payment 100000 8% 20y');

  // 74. Loan payment for 10000 at 6% for 3 years -> 304.22
  r = await brain.processSmartQuery('loan payment for 10000 at 6% for 3 years');
  assert(r.response.includes('304.22'), 'C3-24', 'loan payment 10000 at 6% for 3 years', 'Failed loan payment 10000 6% 3y');

  // 75. Mortgage payment for 500000 at 7% for 30 years -> 3326.51
  r = await brain.processSmartQuery('mortgage payment for 500000 at 7% for 30 years');
  assert(r.response.includes('3,326.51') || r.response.includes('3326.51'), 'C3-25', 'mortgage payment 500000 at 7% for 30 years', 'Failed mortgage payment 500000 7% 30y');

  // =========================================================================
  // CATEGORY 4: Code Refactoring, Socratic Clarification & Cognitive Intactness (25 prompts)
  // =========================================================================
  console.log('');
  console.log('--- CATEGORY 4: Code Refactoring, Socratic Clarification & Cognitive Intactness ---');

  // 76. Refactor nested loop to hash map
  r = await brain.processSmartQuery('refactor nested loop to hash map');
  assert(r.response.includes('O(n)') && (r.response.includes('Hash Map') || r.response.includes('Set')), 'C4-01', 'refactor nested loop to hash map', 'Failed refactor nested loop');

  // 77. Optimize duplicate detection
  r = await brain.processSmartQuery('optimize nested loops for duplicate detection');
  assert(r.response.includes('O(n)') || r.response.includes('hash'), 'C4-02', 'optimize duplicate detection', 'Failed optimize duplicate detection');

  // 78. Refactor bubble sort to quicksort
  r = await brain.processSmartQuery('refactor bubble sort to quicksort');
  assert(r.response.includes('Quicksort') && (r.response.includes('O(n \\log n)') || r.response.includes('O(n log n)')), 'C4-03', 'refactor bubble sort to quicksort', 'Failed refactor bubble sort');

  // 79. Optimize sorting from O(n^2) to O(n log n)
  r = await brain.processSmartQuery('optimize sorting algorithm from O(n^2) to O(n log n)');
  assert(r.response.includes('Quicksort') || r.response.includes('O(n log n)'), 'C4-04', 'optimize sorting algorithm', 'Failed optimize sorting');

  // 80. Refactor string concatenation to string builder
  r = await brain.processSmartQuery('refactor string concatenation loop to string builder');
  assert(r.response.includes('StringBuilder') || r.response.includes('join'), 'C4-05', 'refactor string builder', 'Failed refactor string builder');

  // 81. Socratic clarification: how much does it cost?
  const socraticBrain1 = new ClumsyBrainEngine();
  r = await socraticBrain1.processSmartQuery('how much does it cost?');
  assert(r.response.includes('Which product') || r.response.includes('item') || r.response.includes('cost'), 'C4-06', 'how much does it cost?', 'Failed socratic cost');

  // 82. Socratic clarification: who won the match?
  const socraticBrain2 = new ClumsyBrainEngine();
  r = await socraticBrain2.processSmartQuery('who won the match?');
  assert(r.response.includes('Which sports match') || r.response.includes('match') || r.response.includes('tournament'), 'C4-07', 'who won the match?', 'Failed socratic match');

  // 83. Socratic clarification: what is the formula?
  const socraticBrain3 = new ClumsyBrainEngine();
  r = await socraticBrain3.processSmartQuery('what is the formula?');
  assert(r.response.includes('formula') && (r.response.includes('scientific') || r.response.includes('mathematical')), 'C4-08', 'what is the formula?', 'Failed socratic formula');

  // 84. Socratic clarification: how do i get there?
  const socraticBrain4 = new ClumsyBrainEngine();
  r = await socraticBrain4.processSmartQuery('how do i get there?');
  assert(r.response.includes('location') || r.response.includes('destination') || r.response.includes('origin'), 'C4-09', 'how do i get there?', 'Failed socratic get there');

  // 85. Socratic clarification: how much is it?
  const socraticBrain5 = new ClumsyBrainEngine();
  r = await socraticBrain5.processSmartQuery('how much is it?');
  assert(r.response.includes('Which product') || r.response.includes('item') || r.response.includes('cost'), 'C4-10', 'how much is it?', 'Failed socratic how much is it');

  // 86. Socratic clarification: who won the game?
  const socraticBrain6 = new ClumsyBrainEngine();
  r = await socraticBrain6.processSmartQuery('who won the game?');
  assert(r.response.includes('sports match') || r.response.includes('game') || r.response.includes('tournament'), 'C4-11', 'who won the game?', 'Failed socratic who won the game');

  // 87. Socratic clarification: what formula should i use?
  const socraticBrain7 = new ClumsyBrainEngine();
  r = await socraticBrain7.processSmartQuery('what formula should i use?');
  assert(r.response.includes('formula'), 'C4-12', 'what formula should i use?', 'Failed socratic formula should i use');

  // 88. Socratic clarification: how do i reach there?
  const socraticBrain8 = new ClumsyBrainEngine();
  r = await socraticBrain8.processSmartQuery('how do i reach there?');
  assert(r.response.includes('location') || r.response.includes('destination'), 'C4-13', 'how do i reach there?', 'Failed socratic reach there');

  // 89. Refactor linear search to binary search
  r = await brain.processSmartQuery('refactor linear search to binary search');
  assert(r.response.includes('Binary Search') || r.response.includes('O(log n)'), 'C4-14', 'refactor linear to binary search', 'Failed refactor linear search');

  // 90. Refactor recursive fibonacci with memoization
  r = await brain.processSmartQuery('refactor recursive fibonacci with memoization');
  assert(r.response.includes('memo') || r.response.includes('cache') || r.response.includes('O(n)'), 'C4-15', 'refactor fibonacci memoization', 'Failed refactor fibonacci');

  // 91. Linear equation solver intact
  r = await brain.processSmartQuery('solve 4x + 10 = 50');
  assert(r.response.includes('10') && r.response.includes('x = 10'), 'C4-16', 'solve 4x + 10 = 50', 'Failed linear equation');

  // 92. Linear algebra 2x - 5 = 15
  r = await brain.processSmartQuery('solve 2x - 5 = 15');
  assert(r.response.includes('10'), 'C4-17', 'solve 2x - 5 = 15', 'Failed linear equation 2');

  // 93. Arithmetic 100 * 25
  r = await brain.processSmartQuery('what is 100 * 25');
  assert(r.response.includes('2500'), 'C4-18', 'what is 100 * 25', 'Failed arithmetic 100*25');

  // 94. Square root calculation
  r = await brain.processSmartQuery('square root of 144');
  assert(r.response.includes('12'), 'C4-19', 'square root of 144', 'Failed square root');

  // 95. Fact storage
  r = await brain.processSmartQuery('my favorite language is Python');
  assert(r.response.includes('Python'), 'C4-20', 'my favorite language is Python', 'Failed fact storage');

  // 96. Fact recall
  r = await brain.processSmartQuery('what is my favorite language');
  assert(r.response.includes('Python'), 'C4-21', 'what is my favorite language', 'Failed fact recall');

  // 97. Emotional empathy
  r = await brain.processSmartQuery("i'm feeling stressed today");
  assert(r.response.toLowerCase().includes('breathe') || r.response.toLowerCase().includes('stress') || r.response.toLowerCase().includes('here for you'), 'C4-22', 'i am feeling stressed today', 'Failed emotional empathy');

  // 98. Physics formula: kinetic energy
  r = await brain.processSmartQuery('what is the kinetic energy of 10kg at 5m/s');
  assert(r.response.includes('125'), 'C4-23', 'kinetic energy 10kg at 5m/s', 'Failed kinetic energy');

  // 99. Project scaffolder: fastAPI
  r = await brain.processSmartQuery('scaffold a python fastapi project');
  assert(r.response.includes('FastAPI') || r.response.includes('requirements.txt'), 'C4-24', 'scaffold fastapi', 'Failed scaffold fastapi');

  // 100. Conversation summary
  r = await brain.processSmartQuery('summarize our conversation');
  assert(r.response.includes('Summary') || r.response.includes('Recap'), 'C4-25', 'summarize our conversation', 'Failed conversation summary');

  console.log('');
  console.log('='.repeat(80));
  console.log(`🏆 STAGE 45 BENCHMARK RESULTS: ${passed}/100 PASSED (${((passed/100)*100).toFixed(1)}%) | ${failed} FAILED`);
  console.log('='.repeat(80));

  if (failed > 0) {
    console.error('');
    console.error('⚠️ DETAILED FAILURE BREAKDOWN:');
    failureDetails.forEach((f, i) => {
      console.error(`  ${i+1}. [${f.testId}] "${f.prompt}": ${f.failMsg}`);
    });
    process.exit(1);
  } else {
    console.log('');
    console.log('✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 45 COMPLETE! ✨');
    console.log('');
  }
}

runStage45Benchmark().catch(err => {
  console.error('Benchmark crashed with unhandled error:', err);
  process.exit(1);
});
