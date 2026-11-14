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
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(notes[idx % notes.length], now);
          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
          osc.connect(gain);
          gain.connect(ctx.destination);
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

  global.JarvisHolographicHUD = JarvisHolographicHUD;
})(window);
