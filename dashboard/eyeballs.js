/**
 * DESKBOT // J.A.R.V.I.S. 60-FPS Anatomical Living Eyeball Engine (Stage 16 — Bug Fix #4)
 *
 * Renders ultra-dynamic, expressive living eyeballs on HTML5 <canvas> for both:
 *   1. The Laptop Hub OLED face (`#eyeballCanvas` inside `#oledScreen`)
 *   2. The Full-Screen Phone "Deskbot Eyes" Stream-Flow App (`/mobile`)
 *
 * Features:
 *   - 3D-shaded Sclera (eyeball sphere) + glowing cybernetic orbital socket
 *   - Textured Glowing Iris with radial iris fibers + limbal ring
 *   - Voice & Emotion-Dilating Pupil that pulses with live mic audio / speech
 *   - Dual Specular Catchlights (plus heart highlights in 'love' & sparkles in 'excited')
 *   - Articulated Upper & Lower Eyelids (warm curved lower-lid smile in 'happy' while keeping
 *     the iris, pupil, and catchlights 100% visible!)
 *   - Expressive Floating Eyebrows above each eyeball
 *   - Autonomous Micro-Saccades, Spontaneous Blinking, and Pointer Gaze Tracking
 *   - 14 Dynamic Reactions: idle, happy, excited, love, listening, thinking, speaking,
 *     coding, wink, surprised, focused, confused, sleepy, blink
 */

(function () {
  const REACTION_PRESETS = {
    idle: {
      irisColor: "#38bdf8",
      irisCore: "#0284c7",
      glowColor: "rgba(56, 189, 248, 0.58)",
      scleraRim: "rgba(56, 189, 248, 0.35)",
      browColor: "#38bdf8",
      pupilScale: 1.0,
      upperLidL: 0.08,
      upperLidR: 0.08,
      lowerLidL: 0.05,
      lowerLidR: 0.05,
      lowerSmile: 0.15,
      browAngleL: -2,
      browAngleR: 2,
      browOffsetY: 0,
      gazeBiasX: 0,
      gazeBiasY: 0,
    },
    happy: {
      irisColor: "#4ade80",
      irisCore: "#10b981",
      glowColor: "rgba(52, 211, 153, 0.90)",
      scleraRim: "rgba(250, 204, 21, 0.55)",
      browColor: "#fde047",
      pupilScale: 1.22,
      upperLidL: 0.04,
      upperLidR: 0.04,
      lowerLidL: 0.36,
      lowerLidR: 0.36,
      lowerSmile: 0.85,
      browAngleL: -10,
      browAngleR: 10,
      browOffsetY: -6,
      gazeBiasX: 0,
      gazeBiasY: -2,
    },
    excited: {
      irisColor: "#f472b6",
      irisCore: "#d946ef",
      glowColor: "rgba(236, 72, 153, 0.95)",
      scleraRim: "rgba(250, 204, 21, 0.72)",
      browColor: "#fef08a",
      pupilScale: 1.36,
      upperLidL: 0.0,
      upperLidR: 0.0,
      lowerLidL: 0.24,
      lowerLidR: 0.24,
      lowerSmile: 0.78,
      browAngleL: -15,
      browAngleR: 15,
      browOffsetY: -9,
      gazeBiasX: 0,
      gazeBiasY: -3,
      sparkle: true,
    },
    love: {
      irisColor: "#fb7185",
      irisCore: "#e11d48",
      glowColor: "rgba(244, 63, 94, 0.92)",
      scleraRim: "rgba(251, 113, 133, 0.65)",
      browColor: "#fda4af",
      pupilScale: 1.38,
      upperLidL: 0.08,
      upperLidR: 0.08,
      lowerLidL: 0.32,
      lowerLidR: 0.32,
      lowerSmile: 0.8,
      browAngleL: -12,
      browAngleR: 12,
      browOffsetY: -5,
      gazeBiasX: 0,
      gazeBiasY: -2,
      hearts: true,
    },
    listening: {
      irisColor: "#2dd4bf",
      irisCore: "#059669",
      glowColor: "rgba(16, 185, 129, 0.92)",
      scleraRim: "rgba(45, 212, 191, 0.65)",
      browColor: "#6ee7b7",
      pupilScale: 1.26,
      upperLidL: 0.0,
      upperLidR: 0.0,
      lowerLidL: 0.0,
      lowerLidR: 0.0,
      lowerSmile: 0.2,
      browAngleL: -8,
      browAngleR: 8,
      browOffsetY: -6,
      gazeBiasX: 0,
      gazeBiasY: -3,
      audioRing: true,
    },
    thinking: {
      irisColor: "#fbbf24",
      irisCore: "#7c3aed",
      glowColor: "rgba(245, 158, 11, 0.88)",
      scleraRim: "rgba(167, 139, 250, 0.65)",
      browColor: "#fcd34d",
      pupilScale: 0.84,
      upperLidL: 0.22,
      upperLidR: 0.1,
      lowerLidL: 0.18,
      lowerLidR: 0.12,
      lowerSmile: 0.0,
      browAngleL: 12,
      browAngleR: -14,
      browOffsetY: -3,
      gazeBiasX: 10,
      gazeBiasY: -8,
      scanRing: true,
    },
    speaking: {
      irisColor: "#38bdf8",
      irisCore: "#6366f1",
      glowColor: "rgba(99, 102, 241, 0.92)",
      scleraRim: "rgba(56, 189, 248, 0.65)",
      browColor: "#7dd3fc",
      pupilScale: 1.18,
      upperLidL: 0.05,
      upperLidR: 0.05,
      lowerLidL: 0.15,
      lowerLidR: 0.15,
      lowerSmile: 0.45,
      browAngleL: -6,
      browAngleR: 6,
      browOffsetY: -4,
      gazeBiasX: 0,
      gazeBiasY: 0,
      audioRing: true,
    },
    coding: {
      irisColor: "#22c55e",
      irisCore: "#15803d",
      glowColor: "rgba(34, 197, 94, 0.90)",
      scleraRim: "rgba(74, 222, 128, 0.65)",
      browColor: "#86efac",
      pupilScale: 0.8,
      upperLidL: 0.2,
      upperLidR: 0.2,
      lowerLidL: 0.18,
      lowerLidR: 0.18,
      lowerSmile: 0.1,
      browAngleL: 10,
      browAngleR: -10,
      browOffsetY: 2,
      gazeBiasX: 0,
      gazeBiasY: 2,
      codeScan: true,
    },
    wink: {
      irisColor: "#f59e0b",
      irisCore: "#ec4899",
      glowColor: "rgba(245, 158, 11, 0.88)",
      scleraRim: "rgba(244, 114, 182, 0.6)",
      browColor: "#fde047",
      pupilScale: 1.18,
      upperLidL: 0.04,
      upperLidR: 0.94,
      lowerLidL: 0.25,
      lowerLidR: 0.94,
      lowerSmile: 0.75,
      browAngleL: -12,
      browAngleR: 8,
      browOffsetY: -4,
      gazeBiasX: -3,
      gazeBiasY: -2,
    },
    surprised: {
      irisColor: "#c084fc",
      irisCore: "#7e22ce",
      glowColor: "rgba(192, 132, 252, 0.95)",
      scleraRim: "rgba(232, 121, 249, 0.7)",
      browColor: "#f0abfc",
      pupilScale: 1.44,
      upperLidL: 0.0,
      upperLidR: 0.0,
      lowerLidL: 0.0,
      lowerLidR: 0.0,
      lowerSmile: 0.0,
      browAngleL: -18,
      browAngleR: 18,
      browOffsetY: -12,
      gazeBiasX: 0,
      gazeBiasY: 0,
    },
    focused: {
      irisColor: "#f43f5e",
      irisCore: "#9f1239",
      glowColor: "rgba(244, 63, 94, 0.88)",
      scleraRim: "rgba(251, 113, 133, 0.65)",
      browColor: "#fda4af",
      pupilScale: 0.74,
      upperLidL: 0.3,
      upperLidR: 0.3,
      lowerLidL: 0.28,
      lowerLidR: 0.28,
      lowerSmile: 0.0,
      browAngleL: 16,
      browAngleR: -16,
      browOffsetY: 4,
      gazeBiasX: 0,
      gazeBiasY: 0,
    },
    confused: {
      irisColor: "#fb923c",
      irisCore: "#9333ea",
      glowColor: "rgba(251, 146, 60, 0.88)",
      scleraRim: "rgba(192, 132, 252, 0.6)",
      browColor: "#fdba74",
      pupilScale: 0.94,
      upperLidL: 0.34,
      upperLidR: 0.02,
      lowerLidL: 0.22,
      lowerLidR: 0.02,
      lowerSmile: -0.1,
      browAngleL: 18,
      browAngleR: 14,
      browOffsetY: -2,
      gazeBiasX: -7,
      gazeBiasY: -4,
    },
    sleepy: {
      irisColor: "#818cf8",
      irisCore: "#312e81",
      glowColor: "rgba(129, 140, 248, 0.48)",
      scleraRim: "rgba(129, 140, 248, 0.35)",
      browColor: "#a5b4fc",
      pupilScale: 0.88,
      upperLidL: 0.64,
      upperLidR: 0.64,
      lowerLidL: 0.12,
      lowerLidR: 0.12,
      lowerSmile: 0.0,
      browAngleL: 6,
      browAngleR: -6,
      browOffsetY: 5,
      gazeBiasX: 0,
      gazeBiasY: 6,
    },
    blink: {
      irisColor: "#38bdf8",
      irisCore: "#0284c7",
      glowColor: "rgba(56, 189, 248, 0.4)",
      scleraRim: "rgba(56, 189, 248, 0.3)",
      browColor: "#38bdf8",
      pupilScale: 1.0,
      upperLidL: 0.97,
      upperLidR: 0.97,
      lowerLidL: 0.97,
      lowerLidR: 0.97,
      lowerSmile: 0.2,
      browAngleL: 0,
      browAngleR: 0,
      browOffsetY: 2,
      gazeBiasX: 0,
      gazeBiasY: 0,
    },
  };

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  class DeskbotEyeballEngine {
    constructor(canvas, options = {}) {
      this.canvas = canvas;
      this.ctx = canvas ? canvas.getContext("2d") : null;
      this.fullScreenMode = Boolean(options.fullScreen);
      this.reaction = "idle";
      this.panDeg = 90;
      this.tiltDeg = 90;
      this.audioLevel = 0.0; // 0.0 .. 1.0

      // Spring-interpolated state
      this.gazeX = 0;
      this.gazeY = 0;
      this.targetGazeX = 0;
      this.targetGazeY = 0;
      this.pointerX = 0;
      this.pointerY = 0;
      this.pointerActive = false;

      // Saccades & spontaneous blink
      this.saccadeX = 0;
      this.saccadeY = 0;
      this.nextSaccadeAt = performance.now() + 1200;
      this.nextBlinkAt = performance.now() + 3200;
      this.blinkProgress = 0;
      this.isBlinking = false;

      // Interpolated eyelid & pupil parameters
      this.curUpperL = 0.08;
      this.curUpperR = 0.08;
      this.curLowerL = 0.05;
      this.curLowerR = 0.05;
      this.curSmile = 0.15;
      this.curPupilScale = 1.0;
      this.curBrowAngleL = -2;
      this.curBrowAngleR = 2;
      this.curBrowY = 0;

      this._bindPointerTracking();
      this._resize();
      window.addEventListener("resize", () => this._resize());
      this._animate = this._animate.bind(this);
      requestAnimationFrame(this._animate);
    }

    _bindPointerTracking() {
      window.addEventListener("mousemove", (e) => {
        if (!this.canvas) return;
        const rect = this.canvas.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return;
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const nx = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth * 0.45)));
        const ny = Math.max(-1, Math.min(1, (e.clientY - cy) / (window.innerHeight * 0.45)));
        this.pointerX = nx * 10;
        this.pointerY = ny * 7;
        this.pointerActive = true;
      });
    }

    _resize() {
      if (!this.canvas) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = this.canvas.getBoundingClientRect();
      const w = Math.max(220, rect.width || 240);
      const h = Math.max(110, rect.height || 120);
      this.canvas.width = Math.round(w * dpr);
      this.canvas.height = Math.round(h * dpr);
      this.width = w;
      this.height = h;
      this.dpr = dpr;
    }

    setReaction(reactionName, panDeg, tiltDeg) {
      const key = String(reactionName || "idle").toLowerCase().trim();
      if (key === "blink") {
        this.triggerBlink();
        return;
      }
      this.reaction = REACTION_PRESETS[key] ? key : "idle";
      if (typeof panDeg === "number") this.panDeg = panDeg;
      if (typeof tiltDeg === "number") this.tiltDeg = tiltDeg;
    }

    setServoAngles(panDeg, tiltDeg) {
      if (typeof panDeg === "number") this.panDeg = panDeg;
      if (typeof tiltDeg === "number") this.tiltDeg = tiltDeg;
    }

    setAudioLevel(normalizedLevel) {
      this.audioLevel = Math.max(0, Math.min(1, Number(normalizedLevel) || 0));
    }

    triggerBlink() {
      this.isBlinking = true;
      this.blinkStart = performance.now();
    }

    _updatePhysics(now) {
      const preset = REACTION_PRESETS[this.reaction] || REACTION_PRESETS.idle;

      // Autonomous micro-saccades
      if (now >= this.nextSaccadeAt) {
        if (preset.codeScan) {
          // Rapid horizontal scanning like reading lines of code
          this.saccadeX = ((Math.floor(now / 260) % 5) - 2) * 5.5;
          this.saccadeY = Math.sin(now * 0.004) * 2.5;
          this.nextSaccadeAt = now + 260;
        } else {
          this.saccadeX = (Math.random() - 0.5) * 9.0;
          this.saccadeY = (Math.random() - 0.5) * 6.0;
          this.nextSaccadeAt = now + 900 + Math.random() * 1700;
        }
      }

      // Spontaneous natural blinking
      if (!this.isBlinking && now >= this.nextBlinkAt) {
        this.triggerBlink();
        // Occasional double blink
        const doubleBlink = Math.random() < 0.22;
        this.nextBlinkAt = now + (doubleBlink ? 320 : 2800 + Math.random() * 2700);
      }

      if (this.isBlinking) {
        const elapsed = now - this.blinkStart;
        const duration = 150;
        if (elapsed >= duration) {
          this.isBlinking = false;
          this.blinkProgress = 0;
        } else {
          const phase = elapsed / duration;
          this.blinkProgress = Math.sin(phase * Math.PI);
        }
      }

      // Compute combined gaze target from servo angles + preset bias + pointer + saccades
      const servoDx = ((this.panDeg - 90) / 75) * 12;
      const servoDy = ((90 - this.tiltDeg) / 75) * 9;
      const ptrX = this.pointerActive ? this.pointerX * 0.45 : 0;
      const ptrY = this.pointerActive ? this.pointerY * 0.45 : 0;

      this.targetGazeX = servoDx + preset.gazeBiasX + this.saccadeX + ptrX;
      this.targetGazeY = servoDy + preset.gazeBiasY + this.saccadeY + ptrY;

      this.gazeX = lerp(this.gazeX, this.targetGazeX, 0.22);
      this.gazeY = lerp(this.gazeY, this.targetGazeY, 0.22);

      // Eyelids & pupil interpolation
      const blinkClosure = this.blinkProgress * 0.96;
      const targetUL = Math.max(preset.upperLidL, blinkClosure);
      const targetUR = Math.max(preset.upperLidR, blinkClosure);
      const targetLL = Math.max(preset.lowerLidL, this.blinkProgress * 0.45);
      const targetLR = Math.max(preset.lowerLidR, this.blinkProgress * 0.45);

      this.curUpperL = lerp(this.curUpperL, targetUL, 0.28);
      this.curUpperR = lerp(this.curUpperR, targetUR, 0.28);
      this.curLowerL = lerp(this.curLowerL, targetLL, 0.28);
      this.curLowerR = lerp(this.curLowerR, targetLR, 0.28);
      this.curSmile = lerp(this.curSmile, preset.lowerSmile || 0, 0.2);

      const audioPulse = this.audioLevel * 0.28;
      const breathPulse = Math.sin(now * 0.0035) * 0.04;
      this.curPupilScale = lerp(
        this.curPupilScale,
        preset.pupilScale + audioPulse + breathPulse,
        0.25
      );

      this.curBrowAngleL = lerp(this.curBrowAngleL, preset.browAngleL, 0.2);
      this.curBrowAngleR = lerp(this.curBrowAngleR, preset.browAngleR, 0.2);
      this.curBrowY = lerp(this.curBrowY, preset.browOffsetY || 0, 0.2);
    }

    _drawSingleEyeball(ctx, cx, cy, radius, isRight, now, preset) {
      const upperClosure = isRight ? this.curUpperR : this.curUpperL;
      const lowerClosure = isRight ? this.curLowerR : this.curLowerL;
      const browAngle = isRight ? this.curBrowAngleR : this.curBrowAngleL;

      ctx.save();

      // 1. Outer ambient orbital glow
      const outerGlow = ctx.createRadialGradient(cx, cy, radius * 0.3, cx, cy, radius * 1.45);
      outerGlow.addColorStop(0, preset.glowColor);
      outerGlow.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.45, 0, Math.PI * 2);
      ctx.fill();

      // 2. Clip to eyeball socket sphere
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();

      // 3. 3D Shaded Sclera (dark cyber-sclera with bright inner rim so iris pops)
      const scleraGrad = ctx.createRadialGradient(
        cx - radius * 0.2,
        cy - radius * 0.2,
        radius * 0.1,
        cx,
        cy,
        radius
      );
      scleraGrad.addColorStop(0, "#172b4d");
      scleraGrad.addColorStop(0.72, "#0b1528");
      scleraGrad.addColorStop(1, "#050914");
      ctx.fillStyle = scleraGrad;
      ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);

      // Subtle sclera grid/circuit ring tinted by emotion
      ctx.strokeStyle = preset.scleraRim || "rgba(56, 189, 248, 0.28)";
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 0.86, 0, Math.PI * 2);
      ctx.stroke();

      // 4. Moving Iris (clamped within eyeball sphere)
      const maxOffset = radius * 0.38;
      const gx = Math.max(-maxOffset, Math.min(maxOffset, this.gazeX * (radius / 32)));
      const gy = Math.max(-maxOffset, Math.min(maxOffset, this.gazeY * (radius / 32)));
      const ix = cx + gx;
      const iy = cy + gy;
      const irisRadius = radius * 0.62;

      const irisGrad = ctx.createRadialGradient(ix, iy, irisRadius * 0.15, ix, iy, irisRadius);
      irisGrad.addColorStop(0, "#e0f2fe");
      irisGrad.addColorStop(0.35, preset.irisColor);
      irisGrad.addColorStop(0.82, preset.irisCore);
      irisGrad.addColorStop(1, "#082f49");

      ctx.fillStyle = irisGrad;
      ctx.beginPath();
      ctx.arc(ix, iy, irisRadius, 0, Math.PI * 2);
      ctx.fill();

      // Radial iris texture fibers
      ctx.save();
      ctx.translate(ix, iy);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.22)";
      ctx.lineWidth = 1;
      const fiberCount = 16;
      for (let i = 0; i < fiberCount; i++) {
        const ang = (i / fiberCount) * Math.PI * 2 + now * 0.0004;
        ctx.beginPath();
        ctx.moveTo(Math.cos(ang) * (irisRadius * 0.38), Math.sin(ang) * (irisRadius * 0.38));
        ctx.lineTo(Math.cos(ang) * (irisRadius * 0.92), Math.sin(ang) * (irisRadius * 0.92));
        ctx.stroke();
      }
      ctx.restore();

      // Glowing limbal ring around iris
      ctx.strokeStyle = preset.irisColor;
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      ctx.arc(ix, iy, irisRadius, 0, Math.PI * 2);
      ctx.stroke();

      // Optional audio/thinking ring inside iris
      if (preset.audioRing || this.audioLevel > 0.08) {
        const ringR = irisRadius * (0.72 + Math.sin(now * 0.012) * 0.12);
        ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(ix, iy, ringR, 0, Math.PI * 2);
        ctx.stroke();
      }

      // 5. Dilating Pupil
      const pupilRadius = Math.max(
        irisRadius * 0.26,
        Math.min(irisRadius * 0.72, irisRadius * 0.44 * this.curPupilScale)
      );
      ctx.fillStyle = "#020617";
      ctx.beginPath();
      ctx.arc(ix, iy, pupilRadius, 0, Math.PI * 2);
      ctx.fill();

      // Subtle inner pupil ring
      ctx.strokeStyle = "rgba(56, 189, 248, 0.45)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(ix, iy, pupilRadius * 0.85, 0, Math.PI * 2);
      ctx.stroke();

      // 6. Dual Specular Catchlights (or Heart highlight in Love mode)
      const hlX = ix - irisRadius * 0.32 + gx * 0.12;
      const hlY = iy - irisRadius * 0.32 + gy * 0.12;
      if (preset.hearts) {
        this._drawHeartCatchlight(ctx, hlX, hlY, irisRadius * 0.28);
      } else {
        ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
        ctx.beginPath();
        ctx.arc(hlX, hlY, irisRadius * 0.21, 0, Math.PI * 2);
        ctx.fill();
      }

      // Secondary bottom-right catchlight
      ctx.fillStyle = "rgba(255, 255, 255, 0.65)";
      ctx.beginPath();
      ctx.arc(
        ix + irisRadius * 0.34,
        iy + irisRadius * 0.32,
        irisRadius * 0.10,
        0,
        Math.PI * 2
      );
      ctx.fill();

      // Extra sparkle in excited mode
      if (preset.sparkle) {
        const spScale = 0.8 + 0.3 * Math.sin(now * 0.015);
        ctx.fillStyle = "#fef08a";
        ctx.beginPath();
        ctx.arc(ix + irisRadius * 0.38, iy - irisRadius * 0.28, irisRadius * 0.1 * spScale, 0, Math.PI * 2);
        ctx.fill();
      }

      // 7. Articulated Upper & Lower Eyelids (drawn inside socket clip)
      ctx.fillStyle = "#030712";

      // Upper Eyelid
      if (upperClosure > 0.01) {
        const lidY = cy - radius + upperClosure * (radius * 2.05);
        ctx.beginPath();
        ctx.moveTo(cx - radius * 1.2, cy - radius * 1.2);
        ctx.lineTo(cx + radius * 1.2, cy - radius * 1.2);
        ctx.lineTo(cx + radius * 1.2, lidY);
        ctx.quadraticCurveTo(cx, lidY + radius * 0.16, cx - radius * 1.2, lidY);
        ctx.closePath();
        ctx.fill();

        // Glowing upper lash line
        ctx.strokeStyle = preset.irisColor;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(cx - radius, lidY);
        ctx.quadraticCurveTo(cx, lidY + radius * 0.16, cx + radius, lidY);
        ctx.stroke();
      }

      // Lower Eyelid (supports Happy upward smile curve while keeping iris/pupil visible!)
      if (lowerClosure > 0.01) {
        const lidY = cy + radius - lowerClosure * (radius * 1.65);
        const curveArch = this.curSmile * (radius * 0.38);
        ctx.fillStyle = "#030712";
        ctx.beginPath();
        ctx.moveTo(cx - radius * 1.2, cy + radius * 1.2);
        ctx.lineTo(cx + radius * 1.2, cy + radius * 1.2);
        ctx.lineTo(cx + radius * 1.2, lidY + curveArch * 0.3);
        ctx.quadraticCurveTo(cx, lidY - curveArch, cx - radius * 1.2, lidY + curveArch * 0.3);
        ctx.closePath();
        ctx.fill();

        // Glowing lower cheek-smile line
        ctx.strokeStyle = preset.irisColor;
        ctx.lineWidth = 2.0;
        ctx.beginPath();
        ctx.moveTo(cx - radius * 0.92, lidY + curveArch * 0.25);
        ctx.quadraticCurveTo(cx, lidY - curveArch, cx + radius * 0.92, lidY + curveArch * 0.25);
        ctx.stroke();
      }

      ctx.restore(); // End eyeball sphere clip

      // 8. Outer eyeball socket rim tinted by emotion
      ctx.strokeStyle = preset.scleraRim || "rgba(56, 189, 248, 0.35)";
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // 9. Expressive Floating Eyebrow tinted by emotion
      ctx.save();
      const browY = cy - radius * 1.18 + this.curBrowY * (radius / 32);
      ctx.translate(cx, browY);
      ctx.rotate((browAngle * Math.PI) / 180);
      ctx.strokeStyle = preset.browColor || preset.irisColor;
      ctx.shadowColor = preset.browColor || preset.irisColor;
      ctx.shadowBlur = 10;
      ctx.lineWidth = Math.max(3.0, radius * 0.11);
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(-radius * 0.68, 2);
      ctx.quadraticCurveTo(0, -radius * 0.18, radius * 0.68, 2);
      ctx.stroke();
      ctx.restore();

      ctx.restore();
    }

    _drawHeartCatchlight(ctx, x, y, size) {
      ctx.save();
      ctx.translate(x, y);
      ctx.fillStyle = "#fff1f2";
      ctx.beginPath();
      ctx.moveTo(0, size * 0.35);
      ctx.bezierCurveTo(-size, -size * 0.3, -size * 0.5, -size, 0, -size * 0.35);
      ctx.bezierCurveTo(size * 0.5, -size, size, -size * 0.3, 0, size * 0.35);
      ctx.fill();
      ctx.restore();
    }

    _animate(now) {
      if (this.ctx && this.canvas) {
        this._updatePhysics(now);
        const ctx = this.ctx;
        ctx.save();
        ctx.scale(this.dpr, this.dpr);
        ctx.clearRect(0, 0, this.width, this.height);

        const preset = REACTION_PRESETS[this.reaction] || REACTION_PRESETS.idle;
        const cy = this.height * 0.54;
        const radius = Math.min(this.width * 0.19, this.height * 0.34);
        const spacing = Math.max(radius * 2.55, this.width * 0.44);
        const leftCx = this.width / 2 - spacing / 2;
        const rightCx = this.width / 2 + spacing / 2;

        this._drawSingleEyeball(ctx, leftCx, cy, radius, false, now, preset);
        this._drawSingleEyeball(ctx, rightCx, cy, radius, true, now, preset);

        ctx.restore();
      }
      requestAnimationFrame(this._animate);
    }
  }

  window.DeskbotEyeballEngine = DeskbotEyeballEngine;
  window.DESKBOT_REACTION_PRESETS = REACTION_PRESETS;
})();
