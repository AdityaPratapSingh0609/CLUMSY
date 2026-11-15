/**
 * STAGE 44: 100-PROMPT BENCHMARK SUITE — PERSISTENT MEMORY MESH,
 * CONVERSATIONAL MATH CHAINING, LENGTH CONSTRAINTS & EMPIRICAL SCIENCE ENGINE
 *
 * 100 Total Tests across 4 Deep Verification Categories:
 *   - Category 1: Multi-Turn Accumulator & Conversational Math Chaining [25 Tests]
 *   - Category 2: Length Constraints, Conciseness & Verbosity Budgeting [25 Tests]
 *   - Category 3: User Fact Extraction, Memory & Profile Recall [25 Tests]
 *   - Category 4: Offline Science Formulas, Emotional Empathy & Task Breakdown [25 Tests]
 */

const path = require('path');
const p = path.resolve(__dirname, '../dashboard/clumsy_brain.js');
const { clumsyBrain } = require(p);

const TEST_PROMPTS = [
  // =========================================================================
  // CATEGORY 1: Multi-Turn Accumulator & Conversational Math Chaining (25 Prompts)
  // =========================================================================
  {
    id: "C1-01",
    prompt: "what is 25 * 4",
    expectedCategory: "Math Init",
    validator: (r) => r && r.response && r.response.includes("100")
  },
  {
    id: "C1-02",
    prompt: "now add 50 to that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("150")
  },
  {
    id: "C1-03",
    prompt: "divide that by 2",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("75")
  },
  {
    id: "C1-04",
    prompt: "subtract 10 from it",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("65")
  },
  {
    id: "C1-05",
    prompt: "multiply that by 3",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("195")
  },
  {
    id: "C1-06",
    prompt: "add 5 to the result",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("200")
  },
  {
    id: "C1-07",
    prompt: "divide that by 4",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("50")
  },
  {
    id: "C1-08",
    prompt: "square that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("2500")
  },
  {
    id: "C1-09",
    prompt: "what is the square root of that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("50")
  },
  {
    id: "C1-10",
    prompt: "plus 50",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("100")
  },
  {
    id: "C1-11",
    prompt: "minus 20",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("80")
  },
  {
    id: "C1-12",
    prompt: "times 2",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("160")
  },
  {
    id: "C1-13",
    prompt: "divided by 4",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("40")
  },
  {
    id: "C1-14",
    prompt: "what is 12 * 12",
    expectedCategory: "Math Init",
    validator: (r) => r && r.response && r.response.includes("144")
  },
  {
    id: "C1-15",
    prompt: "now add 56 to that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("200")
  },
  {
    id: "C1-16",
    prompt: "divide the result by 10",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("20")
  },
  {
    id: "C1-17",
    prompt: "multiply the answer by 5",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("100")
  },
  {
    id: "C1-18",
    prompt: "subtract 25 from that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("75")
  },
  {
    id: "C1-19",
    prompt: "add 25 to it",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("100")
  },
  {
    id: "C1-20",
    prompt: "divide that by 5",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("20")
  },
  {
    id: "C1-21",
    prompt: "square it",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("400")
  },
  {
    id: "C1-22",
    prompt: "square root of it",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("20")
  },
  {
    id: "C1-23",
    prompt: "multiply by 3",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("60")
  },
  {
    id: "C1-24",
    prompt: "subtract 10 from the result",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("50")
  },
  {
    id: "C1-25",
    prompt: "add 50 to that",
    expectedCategory: "Math Chaining",
    validator: (r) => r && r.response && r.response.includes("100")
  },

  // =========================================================================
  // CATEGORY 2: Length Constraints, Conciseness & Verbosity Budgeting (25 Prompts)
  // =========================================================================
  {
    id: "C2-01",
    prompt: "explain quantum computing in 1 sentence",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && r.response.length > 15 && (r.response.match(/[.!?]/g) || []).length <= 2
  },
  {
    id: "C2-02",
    prompt: "explain photosynthesis in 1 sentence",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("photosynthesis") && (r.response.match(/[.!?]/g) || []).length <= 2
  },
  {
    id: "C2-03",
    prompt: "what is machine learning in 1 sentence",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("learning") && (r.response.match(/[.!?]/g) || []).length <= 2
  },
  {
    id: "C2-04",
    prompt: "explain gravity in 1 sentence",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("gravity") && (r.response.match(/[.!?]/g) || []).length <= 2
  },
  {
    id: "C2-05",
    prompt: "explain relativity in 1 sentence",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 2
  },
  {
    id: "C2-06",
    prompt: "explain newton's laws in 2 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 4
  },
  {
    id: "C2-07",
    prompt: "what is dna in 2 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 4
  },
  {
    id: "C2-08",
    prompt: "explain thermodynamics in 2 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 4
  },
  {
    id: "C2-09",
    prompt: "what is artificial intelligence in 2 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 4
  },
  {
    id: "C2-10",
    prompt: "explain black holes in 2 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 4
  },
  {
    id: "C2-11",
    prompt: "what is blockchain in 3 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 6
  },
  {
    id: "C2-12",
    prompt: "explain cell biology in 3 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 6
  },
  {
    id: "C2-13",
    prompt: "what is plate tectonics in 3 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 6
  },
  {
    id: "C2-14",
    prompt: "explain electromagnetism in 3 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 6
  },
  {
    id: "C2-15",
    prompt: "what is general relativity in 3 sentences",
    expectedCategory: "Sentence Budget",
    validator: (r) => r && r.response && (r.response.match(/[.!?]/g) || []).length <= 6
  },
  {
    id: "C2-16",
    prompt: "summarize gravity in 1 paragraph",
    expectedCategory: "Paragraph Budget",
    validator: (r) => r && r.response && !r.response.includes("\n\n\n")
  },
  {
    id: "C2-17",
    prompt: "summarize photosynthesis in 1 paragraph",
    expectedCategory: "Paragraph Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("photosynthesis")
  },
  {
    id: "C2-18",
    prompt: "summarize machine learning in 1 paragraph",
    expectedCategory: "Paragraph Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("learning")
  },
  {
    id: "C2-19",
    prompt: "summarize quantum physics in 1 paragraph",
    expectedCategory: "Paragraph Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("quantum")
  },
  {
    id: "C2-20",
    prompt: "summarize black holes in 1 paragraph",
    expectedCategory: "Paragraph Budget",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("black hole")
  },
  {
    id: "C2-21",
    prompt: "briefly explain gravity",
    expectedCategory: "Concise Summary",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("gravity") && r.response.split(/\s+/).length <= 100
  },
  {
    id: "C2-22",
    prompt: "briefly explain photosynthesis",
    expectedCategory: "Concise Summary",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("photosynthesis") && r.response.split(/\s+/).length <= 100
  },
  {
    id: "C2-23",
    prompt: "briefly describe quantum computing",
    expectedCategory: "Concise Summary",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("quantum") && r.response.split(/\s+/).length <= 100
  },
  {
    id: "C2-24",
    prompt: "give a concise summary of newton's laws",
    expectedCategory: "Concise Summary",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("newton") && r.response.split(/\s+/).length <= 100
  },
  {
    id: "C2-25",
    prompt: "concise explanation of relativity",
    expectedCategory: "Concise Summary",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("relativity") && r.response.split(/\s+/).length <= 100
  },

  // =========================================================================
  // CATEGORY 3: User Fact Extraction, Memory & Profile Recall (25 Prompts)
  // =========================================================================
  {
    id: "C3-01",
    prompt: "my favorite language is Rust",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Rust")
  },
  {
    id: "C3-02",
    prompt: "what is my favorite language",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Rust")
  },
  {
    id: "C3-03",
    prompt: "my favorite color is Cyan",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Cyan")
  },
  {
    id: "C3-04",
    prompt: "what is my favorite color",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Cyan")
  },
  {
    id: "C3-05",
    prompt: "my favorite food is Sushi",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Sushi")
  },
  {
    id: "C3-06",
    prompt: "what is my favorite food",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Sushi")
  },
  {
    id: "C3-07",
    prompt: "my favorite movie is Interstellar",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Interstellar")
  },
  {
    id: "C3-08",
    prompt: "what is my favorite movie",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Interstellar")
  },
  {
    id: "C3-09",
    prompt: "i work as a DevOps Engineer",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("DevOps Engineer")
  },
  {
    id: "C3-10",
    prompt: "what is my job",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("DevOps Engineer")
  },
  {
    id: "C3-11",
    prompt: "what do i do for work",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("DevOps Engineer")
  },
  {
    id: "C3-12",
    prompt: "my name is Aditya Pratap Singh",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Aditya Pratap Singh")
  },
  {
    id: "C3-13",
    prompt: "what is my name",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Aditya")
  },
  {
    id: "C3-14",
    prompt: "i live in Bangalore",
    expectedCategory: "Profile Store",
    validator: (r) => r && r.response && r.response.includes("Bangalore")
  },
  {
    id: "C3-15",
    prompt: "where do i live",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Bangalore")
  },
  {
    id: "C3-16",
    prompt: "what is my city",
    expectedCategory: "Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Bangalore")
  },
  {
    id: "C3-17",
    prompt: "remember that I am preparing for the AWS certification",
    expectedCategory: "Profile Note",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("remember")
  },
  {
    id: "C3-18",
    prompt: "what do you know about me",
    expectedCategory: "Full Profile Recall",
    validator: (r) => r && r.response && r.response.includes("Aditya") && r.response.includes("Bangalore")
  },
  {
    id: "C3-19",
    prompt: "what do you remember about me",
    expectedCategory: "Full Profile Recall",
    validator: (r) => r && r.response && r.response.includes("DevOps Engineer")
  },
  {
    id: "C3-20",
    prompt: "repeat that",
    expectedCategory: "Recall Last Turn",
    validator: (r) => r && r.response && r.response.length > 10
  },
  {
    id: "C3-21",
    prompt: "what did i just ask you",
    expectedCategory: "Recall Last Question",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("repeat")
  },
  {
    id: "C3-22",
    prompt: "summarize our conversation",
    expectedCategory: "Summary",
    validator: (r) => r && r.response && r.response.includes("Summary")
  },
  {
    id: "C3-23",
    prompt: "export history",
    expectedCategory: "Export History",
    validator: (r) => r && r.response && r.response.includes("Exported Conversation History")
  },
  {
    id: "C3-24",
    prompt: "clear history",
    expectedCategory: "Clear History",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("cleared")
  },
  {
    id: "C3-25",
    prompt: "what did i just ask you",
    expectedCategory: "Fresh History Check",
    validator: (r) => r && r.response && r.response.toLowerCase().includes("started")
  },

  // =========================================================================
  // CATEGORY 4: Offline Science Formulas, Emotional Empathy & Scaffolding (25 Prompts)
  // =========================================================================
  {
    id: "C4-01",
    prompt: "what is the kinetic energy of 10kg at 5m/s",
    expectedCategory: "Formula: KE",
    validator: (r) => r && r.response && r.response.includes("125") && r.response.includes("Joules")
  },
  {
    id: "C4-02",
    prompt: "kinetic energy of 2kg at 10m/s",
    expectedCategory: "Formula: KE",
    validator: (r) => r && r.response && r.response.includes("100") && r.response.includes("Joules")
  },
  {
    id: "C4-03",
    prompt: "kinetic energy of 4kg at 3m/s",
    expectedCategory: "Formula: KE",
    validator: (r) => r && r.response && r.response.includes("18") && r.response.includes("Joules")
  },
  {
    id: "C4-04",
    prompt: "what is the force of 5kg accelerating at 2m/s^2",
    expectedCategory: "Formula: F=ma",
    validator: (r) => r && r.response && r.response.includes("10") && r.response.includes("Newtons")
  },
  {
    id: "C4-05",
    prompt: "force of 10kg accelerating at 9.8m/s^2",
    expectedCategory: "Formula: F=ma",
    validator: (r) => r && r.response && r.response.includes("98") && r.response.includes("Newtons")
  },
  {
    id: "C4-06",
    prompt: "what is the energy of 2kg mass",
    expectedCategory: "Formula: E=mc^2",
    validator: (r) => r && r.response && r.response.includes("Joules") && r.response.includes("E = mc^2")
  },
  {
    id: "C4-07",
    prompt: "what is the speed of light",
    expectedCategory: "Constant: c",
    validator: (r) => r && r.response && r.response.includes("299,792,458")
  },
  {
    id: "C4-08",
    prompt: "what is planck's constant",
    expectedCategory: "Constant: h",
    validator: (r) => r && r.response && r.response.includes("6.62607015")
  },
  {
    id: "C4-09",
    prompt: "what is the gravitational constant",
    expectedCategory: "Constant: G",
    validator: (r) => r && r.response && r.response.includes("6.67430")
  },
  {
    id: "C4-10",
    prompt: "what is avogadro's number",
    expectedCategory: "Constant: Na",
    validator: (r) => r && r.response && r.response.includes("6.02214076")
  },
  {
    id: "C4-11",
    prompt: "what is boltzmann constant",
    expectedCategory: "Constant: kb",
    validator: (r) => r && r.response && r.response.includes("1.380649")
  },
  {
    id: "C4-12",
    prompt: "i'm feeling stressed today",
    expectedCategory: "Empathy Stress",
    validator: (r) => r && r.response && r.response.includes("Right Here With You")
  },
  {
    id: "C4-13",
    prompt: "i have anxiety",
    expectedCategory: "Empathy Anxiety",
    validator: (r) => r && r.response && r.response.includes("Right Here With You")
  },
  {
    id: "C4-14",
    prompt: "i failed my exam",
    expectedCategory: "Empathy Failure",
    validator: (r) => r && r.response && r.response.includes("Right Here With You")
  },
  {
    id: "C4-15",
    prompt: "i just got promoted!",
    expectedCategory: "Empathy Celebration",
    validator: (r) => r && r.response && r.response.includes("Congratulations")
  },
  {
    id: "C4-16",
    prompt: "i passed my exam",
    expectedCategory: "Empathy Celebration",
    validator: (r) => r && r.response && r.response.includes("Congratulations")
  },
  {
    id: "C4-17",
    prompt: "i'm so happy today",
    expectedCategory: "Empathy Celebration",
    validator: (r) => r && r.response && r.response.includes("Congratulations")
  },
  {
    id: "C4-18",
    prompt: "i am so tired",
    expectedCategory: "Empathy Fatigue",
    validator: (r) => r && r.response && r.response.includes("Take Time to Rest")
  },
  {
    id: "C4-19",
    prompt: "i am exhausted",
    expectedCategory: "Empathy Fatigue",
    validator: (r) => r && r.response && r.response.includes("Take Time to Rest")
  },
  {
    id: "C4-20",
    prompt: "plan a 3-day workout routine",
    expectedCategory: "Task Scaffolder",
    validator: (r) => r && r.response && r.response.includes("Day 1: Push") && r.response.includes("Day 2: Pull") && r.response.includes("Day 3: Legs")
  },
  {
    id: "C4-21",
    prompt: "steps to prepare for technical interview",
    expectedCategory: "Task Scaffolder",
    validator: (r) => r && r.response && r.response.includes("Phase 1") && r.response.includes("Phase 2")
  },
  {
    id: "C4-22",
    prompt: "create a gitignore for python",
    expectedCategory: "Project Scaffolder",
    validator: (r) => r && r.response && r.response.includes("__pycache__") && r.response.includes(".venv")
  },
  {
    id: "C4-23",
    prompt: "create a gitignore for node",
    expectedCategory: "Project Scaffolder",
    validator: (r) => r && r.response && r.response.includes("node_modules") && r.response.includes(".env")
  },
  {
    id: "C4-24",
    prompt: "scaffold a python fastapi project",
    expectedCategory: "Project Scaffolder",
    validator: (r) => r && r.response && r.response.includes("fastapi") && r.response.includes("main.py")
  },
  {
    id: "C4-25",
    prompt: "scaffold a node express app",
    expectedCategory: "Project Scaffolder",
    validator: (r) => r && r.response && r.response.includes("express") && r.response.includes("server.ts")
  }
];

async function runBenchmark() {
  console.log("================================================================================");
  console.log("🚀 RUNNING STAGE 44: 100-PROMPT BENCHMARK (MEMORY, MATH, CONSTRAINTS & SCIENCE)");
  console.log("================================================================================\n");

  let passedCount = 0;
  let failedCount = 0;
  const failures = [];

  let currentCategory = "";

  for (let i = 0; i < TEST_PROMPTS.length; i++) {
    const item = TEST_PROMPTS[i];
    const categoryNumber = Math.floor(i / 25) + 1;
    const catTitles = [
      "Multi-Turn Accumulator & Conversational Math Chaining",
      "Length Constraints, Conciseness & Verbosity Budgeting",
      "User Fact Extraction, Memory & Profile Recall",
      "Offline Science Formulas, Emotional Empathy & Task Breakdown"
    ];

    if (currentCategory !== catTitles[categoryNumber - 1]) {
      currentCategory = catTitles[categoryNumber - 1];
      console.log(`\n--- CATEGORY ${categoryNumber}: ${currentCategory} ---`);
    }

    try {
      const result = await clumsyBrain.processSmartQuery(item.prompt);
      const isOk = item.validator(result);

      if (isOk) {
        passedCount++;
        console.log(`  ✅ [PASS #${String(i + 1).padStart(3, '0')}] [${item.id}] "${item.prompt}"`);
      } else {
        failedCount++;
        console.log(`  ❌ [FAIL #${String(i + 1).padStart(3, '0')}] [${item.id}] "${item.prompt}"`);
        failures.push({
          id: item.id,
          prompt: item.prompt,
          category: item.expectedCategory,
          got: result ? (result.response || result) : 'null/undefined'
        });
      }
    } catch (err) {
      failedCount++;
      console.log(`  💥 [ERROR #${String(i + 1).padStart(3, '0')}] [${item.id}] "${item.prompt}": ${err.message}`);
      failures.push({
        id: item.id,
        prompt: item.prompt,
        category: item.expectedCategory,
        got: `EXCEPTION: ${err.message}`
      });
    }
  }

  console.log("\n================================================================================");
  const passRate = ((passedCount / TEST_PROMPTS.length) * 100).toFixed(1);
  console.log(`🏆 STAGE 44 BENCHMARK RESULTS: ${passedCount}/${TEST_PROMPTS.length} PASSED (${passRate}%) | ${failedCount} FAILED`);
  console.log("================================================================================\n");

  if (failures.length > 0) {
    console.log("⚠️ SUMMARY OF FAILED PROMPTS:");
    failures.forEach((f) => {
      console.log(`\n[${f.id}] Prompt: "${f.prompt}" (${f.category})`);
      console.log(`  Received: ${String(f.got).slice(0, 160)}...`);
    });
    process.exit(1);
  } else {
    console.log("✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 44 COMPLETE! ✨\n");
    process.exit(0);
  }
}

runBenchmark();
