/**
 * STAGE 43: 100-PROMPT BENCHMARK SUITE — AUTONOMOUS HARDWARE MESH,
 * LIVING EYEBALLS, SERVO JITTER GUARD & MULTIMODAL COMPANION REFLEX
 *
 * 100 Total Tests across 4 Deep Verification Categories:
 *   - Category 1: Hardware Movement & Servo Angles (Pan/Tilt 15°-165°, look directions, centering) [25 Tests]
 *   - Category 2: Living Eyeball Expressions & Micro-Expressions (blink, wink, happy, love, sleep, wake) [25 Tests]
 *   - Category 3: Audio Deck Ducking, Hardware Mic Health & Mesh Telemetry [25 Tests]
 *   - Category 4: Anti-Regression Elaboration & Deep Science Stress Test (verifying "explain in 1000 words" never triggers T-1000) [25 Tests]
 */

const path = require('path');
const p = path.resolve(__dirname, '../dashboard/clumsy_brain.js');
const { clumsyBrain } = require(p);

const TEST_PROMPTS = [
  // =========================================================================
  // CATEGORY 1: Hardware Movement & Servo Angles (Pan/Tilt 15°-165°) (25 Prompts)
  // =========================================================================
  {
    id: "C1-01",
    prompt: "look left",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 45 && r.servos.tilt === 90 && r.response.toLowerCase().includes("left")
  },
  {
    id: "C1-02",
    prompt: "turn left",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 45 && r.servos.tilt === 90
  },
  {
    id: "C1-03",
    prompt: "pan left",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 45
  },
  {
    id: "C1-04",
    prompt: "look to the left",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 45
  },
  {
    id: "C1-05",
    prompt: "look right",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 135 && r.servos.tilt === 90 && r.response.toLowerCase().includes("right")
  },
  {
    id: "C1-06",
    prompt: "turn right",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 135 && r.servos.tilt === 90
  },
  {
    id: "C1-07",
    prompt: "pan right",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 135
  },
  {
    id: "C1-08",
    prompt: "look to the right",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 135
  },
  {
    id: "C1-09",
    prompt: "look up",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 135 && r.response.toLowerCase().includes("up")
  },
  {
    id: "C1-10",
    prompt: "tilt up",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 135
  },
  {
    id: "C1-11",
    prompt: "look above",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 135
  },
  {
    id: "C1-12",
    prompt: "look down",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 45 && r.response.toLowerCase().includes("down")
  },
  {
    id: "C1-13",
    prompt: "tilt down",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 45
  },
  {
    id: "C1-14",
    prompt: "look below",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 45
  },
  {
    id: "C1-15",
    prompt: "center eyes",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90 && r.response.toLowerCase().includes("centered")
  },
  {
    id: "C1-16",
    prompt: "look center",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },
  {
    id: "C1-17",
    prompt: "look forward",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },
  {
    id: "C1-18",
    prompt: "reset eyes",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },
  {
    id: "C1-19",
    prompt: "reset servos",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },
  {
    id: "C1-20",
    prompt: "reset position",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },
  {
    id: "C1-21",
    prompt: "pan left clumsy",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 45
  },
  {
    id: "C1-22",
    prompt: "turn right clumsy",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 135
  },
  {
    id: "C1-23",
    prompt: "look up please",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 135
  },
  {
    id: "C1-24",
    prompt: "look down please",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.tilt === 45
  },
  {
    id: "C1-25",
    prompt: "center your eyes",
    expectedCategory: "Hardware",
    validator: (r) => r && r.servos && r.servos.pan === 90 && r.servos.tilt === 90
  },

  // =========================================================================
  // CATEGORY 2: Living Eyeball Expressions & Micro-Expressions (25 Prompts)
  // =========================================================================
  {
    id: "C2-01",
    prompt: "blink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "blink" && r.response.toLowerCase().includes("blink")
  },
  {
    id: "C2-02",
    prompt: "blink eyes",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "blink"
  },
  {
    id: "C2-03",
    prompt: "blink for me",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "blink"
  },
  {
    id: "C2-04",
    prompt: "can you blink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "blink"
  },
  {
    id: "C2-05",
    prompt: "be happy",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "happy" && r.response.toLowerCase().includes("happy")
  },
  {
    id: "C2-06",
    prompt: "smile",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "happy"
  },
  {
    id: "C2-07",
    prompt: "look happy",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "happy"
  },
  {
    id: "C2-08",
    prompt: "wink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "wink" && r.response.toLowerCase().includes("wink")
  },
  {
    id: "C2-09",
    prompt: "give me a wink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "wink"
  },
  {
    id: "C2-10",
    prompt: "wink at me",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "wink"
  },
  {
    id: "C2-11",
    prompt: "can you wink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "wink"
  },
  {
    id: "C2-12",
    prompt: "go to sleep",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "sleep" && r.response.toLowerCase().includes("sleep")
  },
  {
    id: "C2-13",
    prompt: "sleep mode",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "sleep"
  },
  {
    id: "C2-14",
    prompt: "power down eyes",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "sleep"
  },
  {
    id: "C2-15",
    prompt: "shut eyes",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "sleep"
  },
  {
    id: "C2-16",
    prompt: "wake up",
    expectedCategory: "Expressions",
    validator: (r) => r && (r.robot_state === "happy" || r.robot_state === "excited") && r.response.toLowerCase().includes("awake")
  },
  {
    id: "C2-17",
    prompt: "rise and shine",
    expectedCategory: "Expressions",
    validator: (r) => r && (r.robot_state === "happy" || r.robot_state === "excited")
  },
  {
    id: "C2-18",
    prompt: "activate robot",
    expectedCategory: "Expressions",
    validator: (r) => r && (r.robot_state === "happy" || r.robot_state === "excited")
  },
  {
    id: "C2-19",
    prompt: "wake up clumsy",
    expectedCategory: "Expressions",
    validator: (r) => r && (r.robot_state === "happy" || r.robot_state === "excited")
  },
  {
    id: "C2-20",
    prompt: "be happy clumsy",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "happy"
  },
  {
    id: "C2-21",
    prompt: "smile for me",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "happy"
  },
  {
    id: "C2-22",
    prompt: "give a wink",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "wink"
  },
  {
    id: "C2-23",
    prompt: "time to sleep",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "sleep"
  },
  {
    id: "C2-24",
    prompt: "wake up now",
    expectedCategory: "Expressions",
    validator: (r) => r && (r.robot_state === "happy" || r.robot_state === "excited")
  },
  {
    id: "C2-25",
    prompt: "blink now",
    expectedCategory: "Expressions",
    validator: (r) => r && r.robot_state === "blink"
  },

  // =========================================================================
  // CATEGORY 3: Audio Deck Ducking, Hardware Mic Health & Mesh Telemetry (25 Prompts)
  // =========================================================================
  {
    id: "C3-01",
    prompt: "ping nodes",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("Dual-Transport Device Mesh") && r.response.includes("desktop_host") && r.response.includes("0.2 ms")
  },
  {
    id: "C3-02",
    prompt: "mesh status",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("Device Mesh") && r.response.includes("robot_avatar")
  },
  {
    id: "C3-03",
    prompt: "mesh latency",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("laptop_node") && r.response.includes("Latency")
  },
  {
    id: "C3-04",
    prompt: "node latency",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("phone_node") && r.response.includes("ms")
  },
  {
    id: "C3-05",
    prompt: "network health",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("100% Operational")
  },
  {
    id: "C3-06",
    prompt: "ping mesh nodes",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("Device Mesh")
  },
  {
    id: "C3-07",
    prompt: "check mesh status",
    expectedCategory: "Telemetry",
    validator: (r) => r && r.response.includes("Device Mesh")
  },
  {
    id: "C3-08",
    prompt: "system health",
    expectedCategory: "Telemetry",
    validator: (r) => r && (r.response.includes("System Diagnostics") || r.response.includes("Health") || r.response.includes("Healthy"))
  },
  {
    id: "C3-09",
    prompt: "diagnostics",
    expectedCategory: "Telemetry",
    validator: (r) => r && (r.response.includes("Diagnostics") || r.response.includes("Health"))
  },
  {
    id: "C3-10",
    prompt: "cpu usage",
    expectedCategory: "Telemetry",
    validator: (r) => r && (r.response.includes("CPU") || r.response.includes("Neural Engines") || r.response.includes("Diagnostics"))
  },
  {
    id: "C3-11",
    prompt: "battery of phone",
    expectedCategory: "Telemetry",
    validator: (r) => r && (r.response.includes("Battery") || r.response.includes("87%"))
  },
  {
    id: "C3-12",
    prompt: "device status",
    expectedCategory: "Telemetry",
    validator: (r) => r && (r.response.includes("Diagnostics") || r.response.includes("Device Mesh") || r.response.includes("100% Operational"))
  },
  {
    id: "C3-13",
    prompt: "is my mic working",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("microphone is active") || r.response.includes("hear you"))
  },
  {
    id: "C3-14",
    prompt: "can you hear me",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && r.response.includes("hear you")
  },
  {
    id: "C3-15",
    prompt: "are you listening",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && r.response.includes("listening")
  },
  {
    id: "C3-16",
    prompt: "are you there",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("right here") || r.response.includes("awake"))
  },
  {
    id: "C3-17",
    prompt: "stop talking",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("Stopping speech") || r.response.includes("silenced") || r.response.includes("silence"))
  },
  {
    id: "C3-18",
    prompt: "be quiet",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("silenced") || r.response.includes("silent") || r.response.includes("quiet") || r.response.includes("Stopping speech"))
  },
  {
    id: "C3-19",
    prompt: "shut up",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("silenced") || r.response.includes("silent") || r.response.includes("quiet") || r.response.includes("Stopping speech"))
  },
  {
    id: "C3-20",
    prompt: "silence",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("silenced") || r.response.includes("silence") || r.response.includes("Stopping speech") || r.response.includes("quiet"))
  },
  {
    id: "C3-21",
    prompt: "pause speech",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("silenced") || r.response.includes("Stopping speech") || r.response.includes("paused"))
  },
  {
    id: "C3-22",
    prompt: "play music",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("music") || r.response.includes("audio") || r.response.includes("playback") || r.job_artifact)
  },
  {
    id: "C3-23",
    prompt: "pause music",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("pause") || r.response.includes("Paused") || r.response.includes("playback"))
  },
  {
    id: "C3-24",
    prompt: "next track",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("next") || r.response.includes("Skipped") || r.response.includes("track") || r.response.includes("playlist"))
  },
  {
    id: "C3-25",
    prompt: "check my microphone",
    expectedCategory: "Voice/Audio",
    validator: (r) => r && (r.response.includes("microphone") || r.response.includes("hear you") || r.response.includes("listening"))
  },

  // =========================================================================
  // CATEGORY 4: Anti-Regression Elaboration & Deep Science Stress Test (25 Prompts)
  // =========================================================================
  {
    id: "C4-01",
    prompt: "can you explain it to me in 1000 words?",
    isOrphaned: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && r.response.includes("What topic would you like me to explain") && !r.response.includes("T-1000") && !r.response.includes("Terminator")
  },
  {
    id: "C4-02",
    prompt: "explain it in 1000 words",
    isOrphaned: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && !r.response.includes("T-1000") && !r.response.includes("Terminator")
  },
  {
    id: "C4-03",
    prompt: "explain this in 500 words",
    isOrphaned: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && !r.response.includes("T-1000")
  },
  {
    id: "C4-04",
    prompt: "can you explain that in 1000 words",
    isOrphaned: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && !r.response.includes("T-1000")
  },
  {
    id: "C4-05",
    prompt: "explain in 1000 words",
    isOrphaned: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && !r.response.includes("T-1000")
  },
  {
    id: "C4-06",
    prompt: "what is the first 3 laws of motion",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("Newton") || r.response.includes("Inertia"))
  },
  {
    id: "C4-07",
    prompt: "can you explain it to me in 1000 words?",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("Newton") || r.response.includes("Inertia") || r.response.includes("momentum")) && !r.response.includes("T-1000") && !r.response.includes("Terminator")
  },
  {
    id: "C4-08",
    prompt: "what is photosynthesis",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("photosynthesis") || r.response.includes("chlorophyll") || r.response.includes("glucose"))
  },
  {
    id: "C4-09",
    prompt: "explain it in detail",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("photosynthesis") || r.response.includes("chlorophyll") || r.response.includes("Calvin") || r.response.includes("light"))
  },
  {
    id: "C4-10",
    prompt: "what is quantum superposition",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("superposition") || r.response.includes("quantum") || r.response.includes("wavefunction"))
  },
  {
    id: "C4-11",
    prompt: "explain it in simple terms",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("superposition") || r.response.includes("states") || r.response.includes("coin"))
  },
  {
    id: "C4-12",
    prompt: "what is general relativity",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("Einstein") || r.response.includes("spacetime") || r.response.includes("curvature"))
  },
  {
    id: "C4-13",
    prompt: "give an example",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("spacetime") || r.response.includes("light") || r.response.includes("gravity") || r.response.includes("Sun"))
  },
  {
    id: "C4-14",
    prompt: "what is dna replication",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("DNA") || r.response.includes("polymerase") || r.response.includes("replication"))
  },
  {
    id: "C4-15",
    prompt: "in bullet points",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("DNA") || r.response.includes("•") || r.response.includes("-"))
  },
  {
    id: "C4-16",
    prompt: "what is machine learning",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.toLowerCase().includes("learning") || r.response.toLowerCase().includes("model") || r.response.toLowerCase().includes("algorithms"))
  },
  {
    id: "C4-17",
    prompt: "in 1000 words",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.toLowerCase().includes("learning") || r.response.toLowerCase().includes("neural") || r.response.toLowerCase().includes("artificial intelligence")) && !r.response.includes("T-1000")
  },
  {
    id: "C4-18",
    prompt: "explain black holes",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.toLowerCase().includes("black hole") || r.response.toLowerCase().includes("event horizon") || r.response.toLowerCase().includes("singularity"))
  },
  {
    id: "C4-19",
    prompt: "explain it to me in 1000 words",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.toLowerCase().includes("black hole") || r.response.toLowerCase().includes("singularity") || r.response.toLowerCase().includes("horizon")) && !r.response.includes("T-1000")
  },
  {
    id: "C4-20",
    prompt: "what is thermodynamics",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.toLowerCase().includes("thermodynamics") || r.response.toLowerCase().includes("entropy") || r.response.toLowerCase().includes("energy"))
  },
  {
    id: "C4-21",
    prompt: "tell me more",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.toLowerCase().includes("thermodynamics") || r.response.toLowerCase().includes("laws") || r.response.toLowerCase().includes("heat"))
  },
  {
    id: "C4-22",
    prompt: "what is plate tectonics",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.toLowerCase().includes("plate") || r.response.toLowerCase().includes("crust") || r.response.toLowerCase().includes("mantle") || r.response.toLowerCase().includes("lithosphere"))
  },
  {
    id: "C4-23",
    prompt: "explain that simply",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.toLowerCase().includes("plate") || r.response.toLowerCase().includes("earth") || r.response.toLowerCase().includes("continents") || r.response.toLowerCase().includes("lithosphere"))
  },
  {
    id: "C4-24",
    prompt: "what is special relativity",
    expectedCategory: "Science",
    validator: (r) => r && (r.response.includes("Einstein") || r.response.includes("speed of light") || r.response.includes("dilation"))
  },
  {
    id: "C4-25",
    prompt: "can you explain it in 1000 words?",
    dependsOnPrevious: true,
    expectedCategory: "Anti-Regression",
    validator: (r) => r && (r.response.includes("relativity") || r.response.includes("light") || r.response.includes("time")) && !r.response.includes("T-1000") && !r.response.includes("Terminator")
  }
];

async function runStage43Benchmark() {
  console.log('================================================================================');
  console.log('🚀 RUNNING STAGE 43: 100-PROMPT AUTONOMOUS HARDWARE, EYEBALLS & MESH BENCHMARK');
  console.log('================================================================================\n');

  let passed = 0;
  let failed = 0;
  const failureDetails = [];

  let currentCategory = "";

  for (let i = 0; i < TEST_PROMPTS.length; i++) {
    const t = TEST_PROMPTS[i];

    // Reset history if test is orphaned or standalone
    if (t.isOrphaned || (!t.dependsOnPrevious && i > 0)) {
      clumsyBrain.history = [];
    }

    // Determine category header
    let cat = "";
    if (i < 25) cat = "CATEGORY 1: Hardware Movement & Servo Angles (Pan/Tilt 15°-165°)";
    else if (i < 50) cat = "CATEGORY 2: Living Eyeball Expressions & Micro-Expressions";
    else if (i < 75) cat = "CATEGORY 3: Audio Deck Ducking, Hardware Mic Health & Mesh Telemetry";
    else cat = "CATEGORY 4: Anti-Regression Elaboration & Deep Science Stress Test";

    if (cat !== currentCategory) {
      currentCategory = cat;
      console.log(`\n--- ${currentCategory} ---`);
    }

    try {
      const result = await clumsyBrain.processSmartQuery(t.prompt);
      const isOk = t.validator(result);

      if (isOk) {
        passed++;
        console.log(`  ✅ [PASS #${String(i + 1).padStart(3, '0')}] [${t.id}] "${t.prompt}"`);
      } else {
        failed++;
        console.error(`  ❌ [FAIL #${String(i + 1).padStart(3, '0')}] [${t.id}] "${t.prompt}"`);
        failureDetails.push({
          testId: t.id,
          prompt: t.prompt,
          resultExcerpt: result ? String(result.response || result.spoken_tts || JSON.stringify(result)).substring(0, 150) : "null",
          message: "Validator returned false"
        });
      }
    } catch (err) {
      failed++;
      console.error(`  💥 [ERROR #${String(i + 1).padStart(3, '0')}] [${t.id}] "${t.prompt}": ${err.message}`);
      failureDetails.push({
        testId: t.id,
        prompt: t.prompt,
        message: err.message
      });
    }
  }

  console.log('\n================================================================================');
  console.log(`🏆 STAGE 43 BENCHMARK RESULTS: ${passed}/${TEST_PROMPTS.length} PASSED (${((passed / TEST_PROMPTS.length) * 100).toFixed(1)}%) | ${failed} FAILED`);
  console.log('================================================================================\n');

  if (failed > 0) {
    console.error('\n⚠️ DETAILED FAILURE BREAKDOWN:');
    failureDetails.forEach((f, idx) => {
      console.error(`  ${idx + 1}. [${f.testId}] "${f.prompt}": ${f.message}`);
      if (f.resultExcerpt) console.error(`     Response: ${f.resultExcerpt}`);
    });
    process.exit(1);
  } else {
    console.log('\n✨ ALL 100 TESTS & PROMPTS PASSED WITH ZERO MISTAKES! STAGE 43 COMPLETE! ✨\n');
    setTimeout(() => {
      process.exit(0);
    }, 50);
  }
}

runStage43Benchmark().catch(err => {
  console.error('Fatal benchmark error:', err);
  process.exit(1);
});
