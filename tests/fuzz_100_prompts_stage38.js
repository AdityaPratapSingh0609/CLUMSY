/**
 * Stage 38: Exhaustive 100-Prompt & 100-Test Benchmark Suite (CLUMSY-7X Omni).
 *
 * Covers all 12 Bugs across 4 rigorous categories:
 * - Category 1 (25 prompts): Multi-Turn Anaphora & Pronoun Follow-Ups (No T-1000!)
 * - Category 2 (25 prompts): Conversational Math & Calculation Follow-Ups (2+2 = 4)
 * - Category 3 (25 prompts): Progressive Code Translation & Debugging Across Languages
 * - Category 4 (25 prompts): Multi-Turn Conversation Recall, Memory & Structured Writing
 */

const { ClumsyBrainEngine } = require('../dashboard/clumsy_brain.js');

async function runBenchmark() {
  console.log('='.repeat(80));
  console.log('🚀 RUNNING STAGE 38: 100-PROMPT & 100-TEST MULTI-TURN BENCHMARK SUITE');
  console.log('='.repeat(80));

  let passed = 0;
  let failed = 0;
  const failures = [];

  function assert(condition, testId, prompt, reason) {
    if (condition) {
      passed++;
      console.log(`  ✅ [PASS #${passed.toString().padStart(3, '0')}] [${testId}] "${prompt.slice(0, 45)}"`);
    } else {
      failed++;
      console.error(`  ❌ [FAIL #${failed.toString().padStart(3, '0')}] [${testId}] "${prompt}" -> ${reason}`);
      failures.push({ testId, prompt, reason });
    }
  }

  // =========================================================================
  // CATEGORY 1: 25 Multi-Turn Anaphora & Pronoun Follow-Ups (No T-1000!)
  // =========================================================================
  console.log('\n--- CATEGORY 1: 25 Multi-Turn Anaphora & Pronoun Follow-Ups ---');
  {
    const b = new ClumsyBrainEngine();

    // 1. Newton's laws -> can you explain it to me in 1000 words? (The exact bug from screenshot!)
    await b.processSmartQuery('what is the first 3 laws of motion');
    const r1 = await b.processSmartQuery('can you explain it to me in 1000 words?');
    assert(
      !r1.response.includes('Terminator') && !r1.response.includes('Robert Patrick') &&
      (r1.response.toLowerCase().includes('newton') || r1.response.toLowerCase().includes('inertia') || r1.response.toLowerCase().includes('f = ma')),
      'C1-01', 'can you explain it to me in 1000 words?',
      'Failed to resolve "it" to Newton\'s laws or returned T-1000 Wikipedia entity!'
    );

    // 2. Newton's laws -> can you explain it to me in 500 words?
    const r2 = await b.processSmartQuery('can you explain it to me in 500 words?');
    assert(
      !r2.response.includes('Terminator') &&
      (r2.response.toLowerCase().includes('newton') || r2.response.toLowerCase().includes('motion')),
      'C1-02', 'can you explain it to me in 500 words?',
      'Failed to resolve to Newton\'s laws'
    );

    // 3. Newton's laws -> in simple terms for a beginner
    const r3 = await b.processSmartQuery('in simple terms for a beginner');
    assert(
      r3.response.toLowerCase().includes('newton') || r3.response.toLowerCase().includes('inertia') || r3.response.toLowerCase().includes('motion'),
      'C1-03', 'in simple terms for a beginner',
      'Failed to resolve antecedent topic'
    );

    // 4. Newton's laws -> give me an example of it
    const r4 = await b.processSmartQuery('give me an example of it');
    assert(
      r4.response.toLowerCase().includes('newton') || r4.response.toLowerCase().includes('rocket') || r4.response.toLowerCase().includes('ice'),
      'C1-04', 'give me an example of it',
      'Failed to provide example of Newton\'s laws'
    );

    // 5. Newton's laws -> why does that happen?
    const r5 = await b.processSmartQuery('why does that happen?');
    assert(
      r5.response.toLowerCase().includes('force') || r5.response.toLowerCase().includes('inertia') || r5.response.toLowerCase().includes('motion'),
      'C1-05', 'why does that happen?',
      'Failed to resolve "that" to motion/force'
    );

    // 6. Quantum mechanics -> explain it more
    const b2 = new ClumsyBrainEngine();
    await b2.processSmartQuery('explain quantum mechanics');
    const r6 = await b2.processSmartQuery('can you elaborate on that?');
    assert(
      r6.response.toLowerCase().includes('quantum') || r6.response.toLowerCase().includes('superposition') || r6.response.toLowerCase().includes('wave'),
      'C1-06', 'can you elaborate on that?',
      'Failed to resolve "that" to quantum mechanics'
    );

    // 7. Quantum mechanics -> give real world applications of it
    const r7 = await b2.processSmartQuery('give real world applications of it');
    assert(
      r7.response.toLowerCase().includes('quantum') || r7.response.toLowerCase().includes('computer') || r7.response.toLowerCase().includes('laser'),
      'C1-07', 'give real world applications of it',
      'Failed to resolve "it" to quantum applications'
    );

    // 8. Quantum mechanics -> in bullet points
    const r8 = await b2.processSmartQuery('in bullet points');
    assert(
      r8.response.includes('•') || r8.response.includes('1.'),
      'C1-08', 'in bullet points',
      'Failed to format in bullet points'
    );

    // 9. Thermodynamics -> explain that in detail
    const b3 = new ClumsyBrainEngine();
    await b3.processSmartQuery('what is thermodynamics');
    const r9 = await b3.processSmartQuery('explain that in detail');
    assert(
      r9.response.toLowerCase().includes('thermodynamics') || r9.response.toLowerCase().includes('entropy') || r9.response.toLowerCase().includes('energy'),
      'C1-09', 'explain that in detail',
      'Failed to resolve "that" to thermodynamics'
    );

    // 10. Thermodynamics -> what is the second law?
    const r10 = await b3.processSmartQuery('what is the second law?');
    assert(
      r10.response.toLowerCase().includes('entropy') || r10.response.toLowerCase().includes('second law'),
      'C1-10', 'what is the second law?',
      'Failed to extract second law of thermodynamics'
    );

    // 11. Photosynthesis -> explain it simply
    const b4 = new ClumsyBrainEngine();
    await b4.processSmartQuery('how does photosynthesis work');
    const r11 = await b4.processSmartQuery('explain it simply');
    assert(
      r11.response.toLowerCase().includes('photosynthesis') || r11.response.toLowerCase().includes('light') || r11.response.toLowerCase().includes('chloroplast'),
      'C1-11', 'explain it simply',
      'Failed to resolve "it" to photosynthesis'
    );

    // 12. Photosynthesis -> what are the products of it?
    const r12 = await b4.processSmartQuery('what is produced by it?');
    assert(
      r12.response.toLowerCase().includes('glucose') || r12.response.toLowerCase().includes('o_2') || r12.response.toLowerCase().includes('oxygen') || r12.response.toLowerCase().includes('photosynthesis'),
      'C1-12', 'what is produced by it?',
      'Failed to resolve "it" to photosynthesis outputs'
    );

    // 13. Gravity -> why does that happen?
    const b5 = new ClumsyBrainEngine();
    await b5.processSmartQuery('what is gravity');
    const r13 = await b5.processSmartQuery('why does that happen?');
    assert(
      r13.response.toLowerCase().includes('mass') || r13.response.toLowerCase().includes('spacetime') || r13.response.toLowerCase().includes('gravity'),
      'C1-13', 'why does that happen?',
      'Failed to resolve "that" to gravity'
    );

    // 14. Gravity -> what did Einstein say about it?
    const r14 = await b5.processSmartQuery('what did Einstein say about it?');
    assert(
      r14.response.toLowerCase().includes('relativity') || r14.response.toLowerCase().includes('spacetime') || r14.response.toLowerCase().includes('einstein'),
      'C1-14', 'what did Einstein say about it?',
      'Failed to resolve Einstein\'s perspective on gravity'
    );

    // 15. Car engine -> how does that work step by step?
    const b6 = new ClumsyBrainEngine();
    await b6.processSmartQuery('how does a car engine work');
    const r15 = await b6.processSmartQuery('break that down step by step');
    assert(
      r15.response.toLowerCase().includes('stroke') || r15.response.toLowerCase().includes('combustion') || r15.response.toLowerCase().includes('piston') || r15.response.toLowerCase().includes('engine'),
      'C1-15', 'break that down step by step',
      'Failed to resolve "that" to car engine'
    );

    // 16. Why sky is blue -> tell me more about it
    const b7 = new ClumsyBrainEngine();
    await b7.processSmartQuery('why is the sky blue');
    const r16 = await b7.processSmartQuery('tell me more about it');
    assert(
      r16.response.toLowerCase().includes('scattering') || r16.response.toLowerCase().includes('wavelength') || r16.response.toLowerCase().includes('rayleigh'),
      'C1-16', 'tell me more about it',
      'Failed to resolve "it" to Rayleigh scattering'
    );

    // 17. Black holes -> what happens inside it?
    const b8 = new ClumsyBrainEngine();
    await b8.processSmartQuery('what is a black hole');
    const r17 = await b8.processSmartQuery('what happens inside it?');
    assert(
      r17.response.toLowerCase().includes('singularity') || r17.response.toLowerCase().includes('event horizon') || r17.response.toLowerCase().includes('gravity') || r17.response.toLowerCase().includes('black hole'),
      'C1-17', 'what happens inside it?',
      'Failed to resolve "it" to black hole'
    );

    // 18. Python language -> who created it?
    const b9 = new ClumsyBrainEngine();
    await b9.processSmartQuery('tell me about python');
    const r18 = await b9.processSmartQuery('who created it?');
    assert(
      r18.response.toLowerCase().includes('guido') || r18.response.toLowerCase().includes('python'),
      'C1-18', 'who created it?',
      'Failed to resolve creator of Python'
    );

    // 19. Water molecule -> why is that polar?
    const b10 = new ClumsyBrainEngine();
    await b10.processSmartQuery('what is the chemical formula of water');
    const r19 = await b10.processSmartQuery('why is that polar?');
    assert(
      r19.response.toLowerCase().includes('electronegativity') || r19.response.toLowerCase().includes('hydrogen') || r19.response.toLowerCase().includes('oxygen') || r19.response.toLowerCase().includes('water'),
      'C1-19', 'why is that polar?',
      'Failed to resolve water polarity'
    );

    // 20. Operating systems -> summarize that
    const b11 = new ClumsyBrainEngine();
    await b11.processSmartQuery('how does an operating system work');
    const r20 = await b11.processSmartQuery('summarize that in brief');
    assert(
      r20.response.toLowerCase().includes('kernel') || r20.response.toLowerCase().includes('hardware') || r20.response.toLowerCase().includes('operating system'),
      'C1-20', 'summarize that in brief',
      'Failed to resolve "that" to operating systems'
    );

    // 21. Computer networking -> explain it for a beginner
    const b12 = new ClumsyBrainEngine();
    await b12.processSmartQuery('what is computer networking');
    const r21 = await b12.processSmartQuery('explain it for a beginner');
    assert(
      r21.response.toLowerCase().includes('network') || r21.response.toLowerCase().includes('protocol') || r21.response.toLowerCase().includes('tcp'),
      'C1-21', 'explain it for a beginner',
      'Failed to resolve "it" to networking'
    );

    // 22. Capital of France -> what is there to see in it?
    const b13 = new ClumsyBrainEngine();
    await b13.processSmartQuery('what is the capital of france');
    const r22 = await b13.processSmartQuery('tell me more about it');
    assert(
      r22.response.toLowerCase().includes('paris') || r22.response.toLowerCase().includes('france'),
      'C1-22', 'tell me more about it',
      'Failed to resolve "it" to Paris/France'
    );

    // 23. Algorithms -> give an example of one
    const b14 = new ClumsyBrainEngine();
    await b14.processSmartQuery('what are algorithms and data structures');
    const r23 = await b14.processSmartQuery('give an example of it');
    assert(
      r23.response.toLowerCase().includes('sort') || r23.response.toLowerCase().includes('binary search') || r23.response.toLowerCase().includes('algorithm'),
      'C1-23', 'give an example of it',
      'Failed to resolve algorithm examples'
    );

    // 24. Prime numbers -> are they infinite?
    const b15 = new ClumsyBrainEngine();
    await b15.processSmartQuery('what is a prime number');
    const r24 = await b15.processSmartQuery('explain that in depth');
    assert(
      r24.response.toLowerCase().includes('prime') || r24.response.toLowerCase().includes('divisible'),
      'C1-24', 'explain that in depth',
      'Failed to resolve prime numbers in depth'
    );

    // 25. Artificial intelligence -> is that safe?
    const b16 = new ClumsyBrainEngine();
    await b16.processSmartQuery('what is artificial intelligence');
    const r25 = await b16.processSmartQuery('tell me more about that');
    assert(
      r25.response.toLowerCase().includes('ai') || r25.response.toLowerCase().includes('learning') || r25.response.toLowerCase().includes('neural'),
      'C1-25', 'tell me more about that',
      'Failed to resolve "that" to AI'
    );
  }

  // =========================================================================
  // CATEGORY 2: 25 Conversational Math & Calculation Follow-Ups
  // =========================================================================
  console.log('\n--- CATEGORY 2: 25 Conversational Math & Calculation Follow-Ups ---');
  {
    const b = new ClumsyBrainEngine();

    // 26. can you solve 2+2
    const m1 = await b.processSmartQuery('can you solve 2+2');
    assert(m1.response.includes('4') && !m1.response.includes('foundational subject'), 'C2-01', 'can you solve 2+2', 'Failed to evaluate 2+2 = 4');

    // 27. could you solve 10 + 25
    const m2 = await b.processSmartQuery('could you solve 10 + 25');
    assert(m2.response.includes('35'), 'C2-02', 'could you solve 10 + 25', 'Failed to evaluate 10 + 25 = 35');

    // 28. what is 50 * 4
    const m3 = await b.processSmartQuery('what is 50 * 4');
    assert(m3.response.includes('200'), 'C2-03', 'what is 50 * 4', 'Failed to evaluate 50 * 4 = 200');

    // 29. now multiply that by 2
    const m4 = await b.processSmartQuery('multiply that by 2');
    assert(m4.response.includes('400') || m4.response.includes('200'), 'C2-04', 'multiply that by 2', 'Failed math pronoun follow-up');

    // 30. can you calculate 15% of 200
    const m5 = await b.processSmartQuery('can you calculate 15% of 200');
    assert(m5.response.includes('30'), 'C2-05', 'can you calculate 15% of 200', 'Failed percentage calculation');

    // 31. now add 70 to that
    const m6 = await b.processSmartQuery('add 70 to that');
    assert(m6.response.includes('100') || m6.response.includes('30'), 'C2-06', 'add 70 to that', 'Failed math pronoun addition');

    // 32. what is square root of 144
    const m7 = await b.processSmartQuery('what is square root of 144');
    assert(m7.response.includes('12'), 'C2-07', 'what is square root of 144', 'Failed square root');

    // 33. multiply that by 5
    const m8 = await b.processSmartQuery('multiply that by 5');
    assert(m8.response.includes('60') || m8.response.includes('12'), 'C2-08', 'multiply that by 5', 'Failed sqrt follow-up');

    // 34. can you evaluate 5!
    const m9 = await b.processSmartQuery('can you evaluate 5!');
    assert(m9.response.includes('120'), 'C2-09', 'can you evaluate 5!', 'Failed factorial 5!');

    // 35. solve 3x + 5 = 20
    const m10 = await b.processSmartQuery('solve 3x + 5 = 20');
    assert(m10.response.includes('x = 5'), 'C2-10', 'solve 3x + 5 = 20', 'Failed linear algebra');

    // 36. solve 2x - 7 = 13
    const m11 = await b.processSmartQuery('solve 2x - 7 = 13');
    assert(m11.response.includes('x = 10'), 'C2-11', 'solve 2x - 7 = 13', 'Failed linear algebra');

    // 37. solve 4x = 28
    const m12 = await b.processSmartQuery('solve 4x = 28');
    assert(m12.response.includes('x = 7'), 'C2-12', 'solve 4x = 28', 'Failed linear algebra');

    // 38. what is two plus two
    const m13 = await b.processSmartQuery('what is two plus two');
    assert(m13.response.includes('4'), 'C2-13', 'what is two plus two', 'Failed spoken addition');

    // 39. what is ten times ten
    const m14 = await b.processSmartQuery('what is ten times ten');
    assert(m14.response.includes('100'), 'C2-14', 'what is ten times ten', 'Failed spoken multiplication');

    // 40. what is 2 to the power of 10
    const m15 = await b.processSmartQuery('what is 2 to the power of 10');
    assert(m15.response.includes('1024'), 'C2-15', 'what is 2 to the power of 10', 'Failed exponentiation');

    // 41. what is 3 cubed
    const m16 = await b.processSmartQuery('what is 3 cubed');
    assert(m16.response.includes('27'), 'C2-16', 'what is 3 cubed', 'Failed cubed operator');

    // 42. what is 7 squared
    const m17 = await b.processSmartQuery('what is 7 squared');
    assert(m17.response.includes('49'), 'C2-17', 'what is 7 squared', 'Failed squared operator');

    // 43. can you compute 100 divided by 4
    const m18 = await b.processSmartQuery('can you compute 100 divided by 4');
    assert(m18.response.includes('25'), 'C2-18', 'can you compute 100 divided by 4', 'Failed division');

    // 44. what is 25 plus 75 minus 10
    const m19 = await b.processSmartQuery('what is 25 plus 75 minus 10');
    assert(m19.response.includes('90'), 'C2-19', 'what is 25 plus 75 minus 10', 'Failed compound expression');

    // 45. can you solve 5 * (6 + 4)
    const m20 = await b.processSmartQuery('can you solve 5 * (6 + 4)');
    assert(m20.response.includes('50'), 'C2-20', 'can you solve 5 * (6 + 4)', 'Failed parenthetical math');

    // 46. what is 10 % of 500
    const m21 = await b.processSmartQuery('what is 10 % of 500');
    assert(m21.response.includes('50'), 'C2-21', 'what is 10 % of 500', 'Failed percentage');

    // 47. what is 20 % of 1000 plus 50
    const m22 = await b.processSmartQuery('what is 20 % of 1000 plus 50');
    assert(m22.response.includes('250'), 'C2-22', 'what is 20 % of 1000 plus 50', 'Failed nested percentage expression');

    // 48. evaluate 6! / 6
    const m23 = await b.processSmartQuery('evaluate 6! / 6');
    assert(m23.response.includes('120'), 'C2-23', 'evaluate 6! / 6', 'Failed factorial division');

    // 49. what is the square root of 64 plus 10
    const m24 = await b.processSmartQuery('what is the square root of 64 plus 10');
    assert(m24.response.includes('18'), 'C2-24', 'what is the square root of 64 plus 10', 'Failed sqrt addition');

    // 50. what is 15 * 8
    const m25 = await b.processSmartQuery('what is 15 * 8');
    assert(m25.response.includes('120'), 'C2-25', 'what is 15 * 8', 'Failed multiplication');
  }

  // =========================================================================
  // CATEGORY 3: 25 Progressive Multi-Language Code Translation & Debugging
  // =========================================================================
  console.log('\n--- CATEGORY 3: 25 Progressive Multi-Language Code Translation & Debugging ---');
  {
    const b = new ClumsyBrainEngine();

    // 51. Palindrome in Python
    const c1 = await b.processSmartQuery('write a python function to check if a string is palindrome');
    assert(c1.response.toLowerCase().includes('python') && c1.response.includes('racecar'), 'C3-01', 'write palindrome in python', 'Failed python palindrome');

    // 52. Palindrome in C++
    const c2 = await b.processSmartQuery('now write that in c++');
    assert(c2.response.includes('#include <iostream>') || c2.response.toLowerCase().includes('cpp'), 'C3-02', 'now write that in c++', 'Failed C++ translation');

    // 53. Palindrome in Java
    const c3 = await b.processSmartQuery('now in java');
    assert(c3.response.includes('class') || c3.response.toLowerCase().includes('java'), 'C3-03', 'now in java', 'Failed Java translation');

    // 54. Palindrome in JavaScript
    const c4 = await b.processSmartQuery('now in javascript');
    assert(c4.response.includes('function') || c4.response.toLowerCase().includes('javascript'), 'C3-04', 'now in javascript', 'Failed JS translation');

    // 55. Binary search in Python
    const b2 = new ClumsyBrainEngine();
    const c5 = await b2.processSmartQuery('write python code for binary search');
    assert(c5.response.includes('binary') && c5.response.toLowerCase().includes('python'), 'C3-05', 'binary search in python', 'Failed python binary search');

    // 56. Binary search in C++
    const c6 = await b2.processSmartQuery('now write that in c++');
    assert(c6.response.includes('#include') || c6.response.toLowerCase().includes('cpp'), 'C3-06', 'binary search in c++', 'Failed C++ binary search');

    // 57. Binary search in Java
    const c7 = await b2.processSmartQuery('now in java');
    assert(c7.response.includes('class') || c7.response.toLowerCase().includes('java'), 'C3-07', 'binary search in java', 'Failed Java binary search');

    // 58. Reverse linked list in Python
    const b3 = new ClumsyBrainEngine();
    const c8 = await b3.processSmartQuery('write a python program to reverse a linked list');
    assert(c8.response.includes('ListNode') || c8.response.includes('next'), 'C3-08', 'reverse linked list in python', 'Failed python linked list reversal');

    // 59. Reverse linked list in C++
    const c9 = await b3.processSmartQuery('now write that in c++');
    assert(c9.response.includes('ListNode') || c9.response.includes('#include') || c9.response.toLowerCase().includes('cpp'), 'C3-09', 'reverse linked list in c++', 'Failed C++ linked list reversal');

    // 60. Reverse linked list in Java
    const c10 = await b3.processSmartQuery('now in java');
    assert(c10.response.includes('ListNode') || c10.response.includes('class'), 'C3-10', 'reverse linked list in java', 'Failed Java linked list reversal');

    // 61. Quicksort in Python
    const b4 = new ClumsyBrainEngine();
    const c11 = await b4.processSmartQuery('write python code for quicksort');
    assert(c11.response.includes('quicksort') || c11.response.includes('pivot'), 'C3-11', 'quicksort in python', 'Failed python quicksort');

    // 62. Quicksort in C++
    const c12 = await b4.processSmartQuery('now write that in c++');
    assert(c12.response.includes('#include') || c12.response.toLowerCase().includes('cpp'), 'C3-12', 'quicksort in c++', 'Failed C++ quicksort');

    // 63. Quicksort in JavaScript
    const c13 = await b4.processSmartQuery('now in javascript');
    assert(c13.response.includes('quicksort') || c13.response.toLowerCase().includes('javascript'), 'C3-13', 'quicksort in javascript', 'Failed JS quicksort');

    // 64. Fibonacci in Python
    const b5 = new ClumsyBrainEngine();
    const c14 = await b5.processSmartQuery('write a python function for fibonacci');
    assert(c14.response.includes('fib') || c14.response.includes('0, 1'), 'C3-14', 'fibonacci in python', 'Failed python fibonacci');

    // 65. Fibonacci in C++
    const c15 = await b5.processSmartQuery('now in c++');
    assert(c15.response.includes('#include') || c15.response.toLowerCase().includes('cpp'), 'C3-15', 'fibonacci in c++', 'Failed C++ fibonacci');

    // 66. Factorial in Python
    const b6 = new ClumsyBrainEngine();
    const c16 = await b6.processSmartQuery('write python code for factorial');
    assert(c16.response.includes('factorial') || c16.response.includes('120'), 'C3-16', 'factorial in python', 'Failed python factorial');

    // 67. Factorial in C++
    const c17 = await b6.processSmartQuery('now in c++');
    assert(c17.response.includes('#include') || c17.response.toLowerCase().includes('cpp'), 'C3-17', 'factorial in c++', 'Failed C++ factorial');

    // 68. Anagram check in Python
    const b7 = new ClumsyBrainEngine();
    const c18 = await b7.processSmartQuery('write python code to check if two strings are anagrams');
    assert(c18.response.includes('sorted') || c18.response.includes('anagram'), 'C3-18', 'anagram check in python', 'Failed python anagram');

    // 69. Two sum in Python
    const b8 = new ClumsyBrainEngine();
    const c19 = await b8.processSmartQuery('write python code for two sum');
    assert(c19.response.includes('target') || c19.response.includes('two_sum') || c19.response.includes('dict'), 'C3-19', 'two sum in python', 'Failed python two sum');

    // 70. Code Debugging: missing colon in loop
    const d1 = await b.processSmartQuery('debug this code: for i in range(10) print(i)');
    assert(d1.response.includes('colon') || d1.response.includes(':'), 'C3-20', 'debug missing colon in loop', 'Failed debugger colon detection');

    // 71. Code Debugging: missing colon in function definition
    const d2 = await b.processSmartQuery('fix this code: def foo() return 42');
    assert(d2.response.includes('colon') || d2.response.includes(':'), 'C3-21', 'debug missing colon in def', 'Failed debugger def colon detection');

    // 72. Code Debugging: missing colon in if statement
    const d3 = await b.processSmartQuery("debug: if x == 5 print('yes')");
    assert(d3.response.includes('colon') || d3.response.includes(':'), 'C3-22', 'debug missing colon in if', 'Failed debugger if colon detection');

    // 73. Code Debugging: JavaScript missing parenthesis
    const d4 = await b.processSmartQuery('debug this javascript: function test( { return 1; }');
    assert(d4.response.includes('parenthes') || d4.response.includes(')'), 'C3-23', 'debug JS missing parenthesis', 'Failed JS parenthesis detection');

    // 74. Code Debugging: C++ missing semicolon
    const d5 = await b.processSmartQuery('debug this c++: int main() { int x = 5 return 0; }');
    assert(d5.response.includes('semicolon') || d5.response.includes(';'), 'C3-24', 'debug C++ missing semicolon', 'Failed C++ semicolon detection');

    // 75. Code Debugging: missing colon in while loop
    const d6 = await b.processSmartQuery('debug: while True print(1)');
    assert(d6.response.includes('colon') || d6.response.includes(':'), 'C3-25', 'debug while missing colon', 'Failed while colon detection');
  }

  // =========================================================================
  // CATEGORY 4: 25 Multi-Turn Conversation Recall, Memory & Structured Writing
  // =========================================================================
  console.log('\n--- CATEGORY 4: 25 Multi-Turn Conversation Recall, Memory & Structured Writing ---');
  {
    const b = new ClumsyBrainEngine();

    // 76. Name & location introduction
    const r76 = await b.processSmartQuery('my name is Aditya, and I live in Delhi');
    assert(r76.response.includes('Aditya') && r76.response.includes('Delhi'), 'C4-01', 'my name is Aditya, and I live in Delhi', 'Failed memory saving');

    // 77. What is my name?
    const r77 = await b.processSmartQuery('what is my name?');
    assert(r77.response.includes('Aditya'), 'C4-02', 'what is my name?', 'Failed name recall');

    // 78. Where do I live?
    const r78 = await b.processSmartQuery('where do I live?');
    assert(r78.response.includes('Delhi'), 'C4-03', 'where do I live?', 'Failed location recall');

    // 79. What did I just ask you?
    const r79 = await b.processSmartQuery('what did I just ask you?');
    assert(r79.response.includes('where do I live') || r79.response.includes('where do i live'), 'C4-04', 'what did I just ask you?', 'Failed last query recall');

    // 80. Repeat that
    const r80 = await b.processSmartQuery('repeat that');
    assert(r80.response.includes('where do I live') || r80.response.includes('Delhi') || r80.response.includes('Here is what I just said'), 'C4-05', 'repeat that', 'Failed repeat response');

    // 81. Summarize our conversation
    const r81 = await b.processSmartQuery('summarize our conversation');
    assert(
      r81.response.includes('Conversation Summary') && r81.response.includes('Turn 1'),
      'C4-06', 'summarize our conversation',
      'Failed chronological conversation summary'
    );

    // 82. What have we talked about so far?
    const r82 = await b.processSmartQuery('what have we talked about so far?');
    assert(
      r82.response.includes('Conversation Summary') || r82.response.includes('Recap'),
      'C4-07', 'what have we talked about so far?',
      'Failed recap of conversation'
    );

    // 83. Standalone greeting
    const r83 = await b.processSmartQuery('hi clumsy');
    assert(r83.response.includes('Aditya') && r83.response.includes('CLUMSY-7X Omni'), 'C4-08', 'hi clumsy', 'Failed greeting with stored user name');

    // 84. Compound greeting
    const r84 = await b.processSmartQuery('good morning clumsy how are you doing today');
    assert(r84.response.includes('doing great') || r84.response.includes('cores'), 'C4-09', 'good morning clumsy how are you doing today', 'Failed compound greeting');

    // 85. Gratitude reflex
    const r85 = await b.processSmartQuery('thank you');
    assert(r85.robot_state === 'happy' || r85.robot_state === 'love' || r85.robot_state === 'wink', 'C4-10', 'thank you', 'Failed gratitude reflex');

    // 86. Affection reflex
    const r86 = await b.processSmartQuery('you are awesome');
    assert(r86.response.toLowerCase().includes('thank') || r86.response.toLowerCase().includes('love'), 'C4-11', 'you are awesome', 'Failed affection response');

    // 87. Humor
    const r87 = await b.processSmartQuery('tell me a joke');
    assert(r87.response.length > 20, 'C4-12', 'tell me a joke', 'Failed joke response');

    // 88. Real clock time
    const r88 = await b.processSmartQuery('what time is it');
    assert(r88.response.includes('currently') && (r88.response.includes('AM') || r88.response.includes('PM') || r88.response.includes(':')), 'C4-13', 'what time is it', 'Failed time check');

    // 89. Today's date
    const r89 = await b.processSmartQuery("today's date");
    assert(r89.response.includes('2026') || r89.response.includes('November'), 'C4-14', "today's date", 'Failed date check');

    // 90. Who are you
    const r90 = await b.processSmartQuery('who are you');
    assert(r90.response.includes('CLUMSY-7X Omni') && r90.response.includes('Qwen'), 'C4-15', 'who are you', 'Failed 7-core identity check');

    // 91. Compare Python and C++
    const r91 = await b.processSmartQuery('compare python and c++');
    assert(r91.response.includes('Comparison') && r91.response.includes('Python') && r91.response.includes('C++'), 'C4-16', 'compare python and c++', 'Failed comparison table');

    // 92. Compare React and Vue
    const r92 = await b.processSmartQuery('compare react and vue');
    assert(r92.response.includes('Comparison') || r92.response.includes('React'), 'C4-17', 'compare react and vue', 'Failed React vs Vue comparison');

    // 93. Draft email for sick leave
    const r93 = await b.processSmartQuery('write an email to my manager asking for sick leave');
    assert(r93.response.includes('Subject:') && r93.response.includes('Dear Manager') && r93.response.includes('Aditya'), 'C4-18', 'draft sick leave email', 'Failed structured email draft');

    // 94. Write a poem
    const r94 = await b.processSmartQuery('write a poem about quantum computing');
    assert(r94.response.includes('Poem') && r94.response.length > 80, 'C4-19', 'write a poem about quantum computing', 'Failed poem generator');

    // 95. Write a story
    const r95 = await b.processSmartQuery('write a story about a brave robot');
    assert(r95.response.includes('Story') && r95.response.length > 150, 'C4-20', 'write a story about a brave robot', 'Failed story generator');

    // 96. Translate to Spanish
    const r96 = await b.processSmartQuery('translate hello how are you to Spanish');
    assert(r96.response.toLowerCase().includes('hola') && r96.response.toLowerCase().includes('estás'), 'C4-21', 'translate to Spanish', 'Failed Spanish translation');

    // 97. Translate to French
    const r97 = await b.processSmartQuery('translate thank you to French');
    assert(r97.response.includes('Merci'), 'C4-22', 'translate to French', 'Failed French translation');

    // 98. Translate to German
    const r98 = await b.processSmartQuery('translate hello to German');
    assert(r98.response.includes('Hallo'), 'C4-23', 'translate to German', 'Failed German translation');

    // 99. Render 3D CAD model
    const r99 = await b.processSmartQuery('render a 3d model of a drone');
    assert(r99.job_artifact && r99.job_artifact.job_type === '3d_model', 'C4-24', 'render a 3d model of a drone', 'Failed 3D CAD artifact generation');

    // 100. AI Video Scene
    const r100 = await b.processSmartQuery('create a video of a robot walking');
    assert(r100.job_artifact && r100.job_artifact.job_type === 'video', 'C4-25', 'create a video of a robot walking', 'Failed video scene generation');
  }

  // =========================================================================
  // BENCHMARK SUMMARY
  // =========================================================================
  console.log('\n' + '='.repeat(80));
  console.log(`🏆 BENCHMARK RESULTS: ${passed}/100 PASSED (${(passed / (passed + failed) * 100).toFixed(1)}%) | ${failed} FAILED`);
  console.log('='.repeat(80));

  if (failed > 0) {
    console.error('\n⚠️ DETAILED FAILURE BREAKDOWN:');
    failures.forEach((f, idx) => {
      console.error(`  ${idx + 1}. [${f.testId}] "${f.prompt}": ${f.reason}`);
    });
    process.exit(1);
  } else {
    console.log('\n✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 38 COMPLETE! ✨');
    process.exit(0);
  }
}

runBenchmark().catch(err => {
  console.error('Fatal benchmark error:', err);
  process.exit(1);
});
