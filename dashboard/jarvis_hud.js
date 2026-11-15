/**
 * J.A.R.V.I.S. Holographic Reactive HUD, WebAudio Synth & Multi-Model Fusion Matrix (Stage 19)
 * 100% Self-Contained • Zero External CDN Dependencies
 */
(function (global) {
  'use strict';

  class JarvisHolographicHUD {
    constructor(arcCanvasId, waveformContainerId) {
      this.arcCanvas = document.getElementById(arcCanvasId);
      this.waveformEl = document.getElementById(waveformContainerId);
      this.angle = 0;
      this.energy = 0.25;
      this.mode = 'IDLE';
      this.audioCtx = null;
      this.isPlayingMusic = false;
      this._musicTimer = null;

      if (this.waveformEl) {
        this.waveformEl.innerHTML = '';
        this.bars = [];
        for (let i = 0; i < 16; i++) {
          const b = document.createElement('div');
          b.className = 'wf-bar';
          b.style.height = '14%';
          this.waveformEl.appendChild(b);
          this.bars.push(b);
        }
      }

      this._loop = this._loop.bind(this);
      requestAnimationFrame(this._loop);
    }

    setActivity(mode, energyLevel, barHeights) {
      this.mode = (mode || 'IDLE').toUpperCase();
      this.energy = Math.max(0.15, Math.min(1.0, Number(energyLevel) || 0.25));
      if (Array.isArray(barHeights) && this.bars) {
        for (let i = 0; i < Math.min(this.bars.length, barHeights.length); i++) {
          this.bars[i].style.height = Math.max(8, Math.min(100, barHeights[i])) + '%';
        }
      }
    }

    playSciFiChime(type) {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        if (!this.audioCtx) this.audioCtx = new AudioContext();
        const ctx = this.audioCtx;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(type === 'wake' ? 520 : 660, now);
        osc.frequency.exponentialRampToValueAtTime(type === 'wake' ? 880 : 990, now + 0.16);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.19);
      } catch (_) {}
    }

    duckSynthMusic(isDucked = true) {
      if (!this.audioCtx || !this.musicMasterGain) return;
      const ctx = this.audioCtx;
      const now = ctx.currentTime;
      try {
        this.musicMasterGain.gain.cancelScheduledValues(now);
        if (isDucked) {
          this.musicMasterGain.gain.linearRampToValueAtTime(0.15, now + 0.12);
        } else {
          this.musicMasterGain.gain.linearRampToValueAtTime(1.0, now + 1.2);
        }
      } catch (_) {}
    }

    toggleSynthMusic(forcePlay) {
      if (forcePlay === false || (this.isPlayingMusic && forcePlay !== true)) {
        this.isPlayingMusic = false;
        if (this._musicTimer) clearInterval(this._musicTimer);
        this._musicTimer = null;
        this.setActivity('IDLE', 0.22);
        return false;
      }
      this.isPlayingMusic = true;
      this.setActivity('MUSIC', 0.85);
      const notes = [220, 261.63, 329.63, 392.0, 440.0, 523.25, 392.0, 329.63];
      let idx = 0;
      if (this._musicTimer) clearInterval(this._musicTimer);
      this._musicTimer = setInterval(() => {
        if (!this.isPlayingMusic) return;
        try {
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          if (!AudioContext) return;
          if (!this.audioCtx) this.audioCtx = new AudioContext();
          const ctx = this.audioCtx;
          const now = ctx.currentTime;
          if (!this.musicMasterGain) {
            this.musicMasterGain = ctx.createGain();
            this.musicMasterGain.gain.setValueAtTime(1.0, now);
            this.musicMasterGain.connect(ctx.destination);
          }
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(notes[idx % notes.length], now);
          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
          osc.connect(gain);
          gain.connect(this.musicMasterGain);
          osc.start(now);
          osc.stop(now + 0.30);
          idx++;
        } catch (_) {}
      }, 320);
      return true;
    }

    _loop(now) {
      this.angle += 0.025 * (0.6 + this.energy);
      this._drawArcReactor();
      if (this.bars) {
        for (let i = 0; i < this.bars.length; i++) {
          const wave = Math.abs(Math.sin(now * 0.006 + i * 0.45)) * 75 * this.energy + 10;
          this.bars[i].style.height = Math.min(100, Math.round(wave)) + '%';
        }
      }
      requestAnimationFrame(this._loop);
    }

    _drawArcReactor() {
      if (!this.arcCanvas) return;
      const ctx = this.arcCanvas.getContext('2d');
      const w = this.arcCanvas.width;
      const h = this.arcCanvas.height;
      const cx = w / 2;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      // Outer segmented ring (Warm Violet)
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(this.angle);
      ctx.strokeStyle = 'rgba(168, 85, 247, 0.88)';
      ctx.lineWidth = 2.4;
      for (let i = 0; i < 6; i++) {
        ctx.beginPath();
        ctx.arc(0, 0, 26, (i * Math.PI) / 3, (i * Math.PI) / 3 + 0.38);
        ctx.stroke();
      }
      ctx.restore();

      // Counter-rotating inner ring (Rose / Amber)
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(-this.angle * 1.4);
      ctx.strokeStyle = 'rgba(244, 114, 182, 0.82)';
      ctx.lineWidth = 2;
      for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        ctx.arc(0, 0, 18, (i * Math.PI) / 2, (i * Math.PI) / 2 + 0.55);
        ctx.stroke();
      }
      ctx.restore();

      // Glowing core pulse (White -> Violet -> Rose)
      const coreRadius = 8.5 + Math.sin(this.angle * 3) * 2.5 * this.energy;
      const grad = ctx.createRadialGradient(cx, cy, 1, cx, cy, coreRadius * 1.9);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.45, '#c084fc');
      grad.addColorStop(0.8, 'rgba(236, 72, 153, 0.45)');
      grad.addColorStop(1, 'rgba(168, 85, 247, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx, cy, coreRadius * 1.9, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  /**
   * Stage 47: Cosmic Soundwave Portal & Luminescent Voice Orb Engine
   * Inspired by Reference Design 1 (Loqo Soundwave Portal) & Design 4 (Executive Orb)
   * 100% Self-Contained Canvas Animation • Zero External Dependencies
   */
  class CosmicSoundwavePortal {
    constructor(canvasId) {
      this.canvas = typeof canvasId === 'string' ? document.getElementById(canvasId) : canvasId;
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext('2d');
      this.energy = 0.35;
      this.targetEnergy = 0.35;
      this.time = 0;
      this.stars = [];
      this.waveCount = 18;

      // Seed ambient background stars
      for (let i = 0; i < 45; i++) {
        this.stars.push({
          x: Math.random(),
          y: Math.random(),
          size: Math.random() * 1.6 + 0.4,
          speed: Math.random() * 0.0004 + 0.0001,
          phase: Math.random() * Math.PI * 2
        });
      }

      this._render = this._render.bind(this);
      requestAnimationFrame(this._render);
    }

    setEnergy(val) {
      this.targetEnergy = Math.max(0.2, Math.min(1.2, Number(val) || 0.35));
    }

    pulse() {
      this.energy = 1.0;
    }

    _render(now) {
      if (!this.canvas) return;
      this.energy += (this.targetEnergy - this.energy) * 0.08;
      this.time = now * 0.0018;

      const w = this.canvas.width;
      const h = this.canvas.height;
      if (w === 0 || h === 0) {
        requestAnimationFrame(this._render);
        return;
      }
      const ctx = this.ctx;
      const cx = w / 2;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      // 1. Draw subtle drifting cosmic stars
      for (let i = 0; i < this.stars.length; i++) {
        const s = this.stars[i];
        const sx = (s.x * w + Math.sin(this.time * 0.5 + s.phase) * 6) % w;
        const sy = (s.y * h + this.time * s.speed * 200) % h;
        const alpha = 0.25 + Math.sin(this.time * 1.5 + s.phase) * 0.25;
        ctx.fillStyle = `rgba(255, 255, 255, ${Math.max(0, alpha)})`;
        ctx.beginPath();
        ctx.arc(sx, sy, s.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // 2. Dynamic Concentric Harmonic Soundwave Ripples (Design 1)
      const baseRadius = Math.min(w, h) * 0.22;
      const maxRipple = Math.min(w, h) * 0.46;

      ctx.save();
      ctx.translate(cx, cy);

      for (let waveIdx = 0; waveIdx < this.waveCount; waveIdx++) {
        const progress = waveIdx / (this.waveCount - 1);
        const radius = baseRadius + progress * (maxRipple - baseRadius);
        const waveAmp = (4 + progress * 14) * (0.4 + this.energy * 0.9);
        const freq = 4 + (waveIdx % 3) * 2;
        const phaseShift = this.time * (1.2 + waveIdx * 0.15);

        ctx.beginPath();
        const steps = 120;
        for (let i = 0; i <= steps; i++) {
          const theta = (i / steps) * Math.PI * 2;
          const harmonic = Math.sin(theta * freq + phaseShift) * Math.cos(theta * 2 - phaseShift * 0.6);
          const r = radius + harmonic * waveAmp;
          const px = Math.cos(theta) * r;
          const py = Math.sin(theta) * r;

          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();

        // Dual-gradient: Cyan (#00f0ff) on left, Magenta (#ff007a) on right
        const strokeAlpha = (1 - progress * 0.75) * (0.2 + this.energy * 0.45);
        const grad = ctx.createLinearGradient(-radius, 0, radius, 0);
        grad.addColorStop(0, `rgba(0, 240, 255, ${strokeAlpha})`);
        grad.addColorStop(0.5, `rgba(168, 85, 247, ${strokeAlpha * 0.85})`);
        grad.addColorStop(1, `rgba(255, 0, 122, ${strokeAlpha})`);

        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.0 + (1 - progress) * 1.5;
        ctx.stroke();
      }

      // 3. Central Luminous Sphere / Celestial Orb
      const orbRadius = baseRadius * 0.92;
      const orbAura = ctx.createRadialGradient(0, 0, orbRadius * 0.4, 0, 0, orbRadius * 1.35);
      orbAura.addColorStop(0, 'rgba(0, 0, 0, 0)');
      orbAura.addColorStop(0.68, 'rgba(0, 240, 255, 0.08)');
      orbAura.addColorStop(0.85, 'rgba(168, 85, 247, 0.28)');
      orbAura.addColorStop(0.96, 'rgba(255, 0, 122, 0.45)');
      orbAura.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.fillStyle = orbAura;
      ctx.beginPath();
      ctx.arc(0, 0, orbRadius * 1.35, 0, Math.PI * 2);
      ctx.fill();

      // Deep obsidian void center with glowing perimeter
      const voidGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, orbRadius);
      voidGrad.addColorStop(0, '#090a10');
      voidGrad.addColorStop(0.78, '#0d0e17');
      voidGrad.addColorStop(0.95, '#151726');
      voidGrad.addColorStop(1, '#231e3d');

      ctx.fillStyle = voidGrad;
      ctx.beginPath();
      ctx.arc(0, 0, orbRadius, 0, Math.PI * 2);
      ctx.fill();

      // Inner Chromatic Rim
      ctx.lineWidth = 2.2;
      const rimGrad = ctx.createLinearGradient(-orbRadius, -orbRadius, orbRadius, orbRadius);
      rimGrad.addColorStop(0, 'rgba(0, 240, 255, 0.85)');
      rimGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.7)');
      rimGrad.addColorStop(1, 'rgba(255, 0, 122, 0.9)');
      ctx.strokeStyle = rimGrad;
      ctx.beginPath();
      ctx.arc(0, 0, orbRadius, 0, Math.PI * 2);
      ctx.stroke();

      // Core pulsating shimmer
      const corePulse = Math.sin(this.time * 2.8) * 4 * this.energy;
      const innerGlow = ctx.createRadialGradient(0, 0, 2, 0, 0, 32 + corePulse);
      innerGlow.addColorStop(0, 'rgba(255, 255, 255, 0.75)');
      innerGlow.addColorStop(0.35, 'rgba(168, 85, 247, 0.55)');
      innerGlow.addColorStop(0.7, 'rgba(0, 240, 255, 0.25)');
      innerGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = innerGlow;
      ctx.beginPath();
      ctx.arc(0, 0, 32 + corePulse, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
      requestAnimationFrame(this._render);
    }
  }

  global.JarvisHolographicHUD = JarvisHolographicHUD;
  global.CosmicSoundwavePortal = CosmicSoundwavePortal;
})(window);
