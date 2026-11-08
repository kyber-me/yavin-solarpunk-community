import { useEffect, useRef, useState } from 'react';

// Original, generated ambience. Playback follows browser autoplay permissions.
function createArrivalSound(onPlayback: (playing: boolean) => void) {
  const context = new AudioContext();
  const master = context.createGain();
  master.gain.value = 0;
  master.connect(context.destination);
  const delay = context.createDelay(2);
  const feedback = context.createGain();
  feedback.gain.value = 0.3;
  delay.delayTime.value = 0.72;
  delay.connect(feedback).connect(delay);
  delay.connect(master);

  function note(frequency: number, at: number, duration: number, volume: number, type: OscillatorType = 'sine') {
    const oscillator = context.createOscillator();
    const envelope = context.createGain();
    oscillator.type = type;
    oscillator.frequency.value = frequency;
    envelope.gain.setValueAtTime(0, at);
    envelope.gain.linearRampToValueAtTime(volume, at + Math.min(1.5, duration / 4));
    envelope.gain.exponentialRampToValueAtTime(0.0001, at + duration);
    oscillator.connect(envelope);
    envelope.connect(master);
    envelope.connect(delay);
    oscillator.start(at);
    oscillator.stop(at + duration + 0.1);
    oscillator.onended = () => { oscillator.disconnect(); envelope.disconnect(); };
  }

  const chords = [[130.81, 196, 246.94, 293.66], [110, 164.81, 220, 329.63], [174.61, 220, 261.63, 329.63], [98, 196, 293.66, 440]];
  let phrase = 0;
  function schedule() {
    const at = context.currentTime + 0.1;
    const chord = chords[phrase++ % chords.length];
    chord.forEach((frequency, index) => {
      note(frequency, at + index * 0.15, 14, 0.035, 'sine');
      note(frequency * 2, at + 1 + index * 2.1, 4, 0.045);
    });
  }
  let interval: number | undefined;
  let started = false;
  let stopped = false;
  function updatePlayback() {
    const playing = context.state === 'running';
    if (playing && !started && !stopped) {
      started = true;
      master.gain.linearRampToValueAtTime(0.65, context.currentTime + 2);
      schedule();
      interval = window.setInterval(() => { if (context.state === 'running') schedule(); }, 12000);
    }
    onPlayback(playing && !stopped);
  }
  context.onstatechange = updatePlayback;
  return {
    async start() {
      if (stopped) return;
      if (context.state !== 'running') await context.resume();
      updatePlayback();
    },
    async pause() { if (!stopped && context.state === 'running') await context.suspend(); },
    async stop() {
      stopped = true;
      window.clearInterval(interval);
      context.onstatechange = null;
      if (context.state === 'closed') return;
      await context.close();
    },
  };
}

export function useArrivalSound(active: boolean) {
  const [enabled, setEnabled] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState('');
  const audio = useRef<ReturnType<typeof createArrivalSound> | null>(null);

  useEffect(() => {
    if (!active || !enabled) { setPlaying(false); return; }
    let disposed = false;
    setError('');
    try {
      audio.current = createArrivalSound(value => { if (!disposed) setPlaying(value); });
    } catch {
      setError('Não foi possível ativar o som neste navegador.');
      return;
    }
    const current = audio.current;
    function start() {
      if (!document.hidden) void current.start().catch(() => {
        if (!disposed) setError('Não foi possível ativar o som neste navegador.');
      });
    }
    function interaction(event: Event) {
      // Muting must not briefly unlock audio during the same gesture.
      if (event.target instanceof Element && event.target.closest('.arrival-sound')) return;
      start();
    }
    function visibility() {
      if (document.hidden) void current.pause().catch(() => {});
      else start();
    }
    start();
    window.addEventListener('pointerdown', interaction);
    window.addEventListener('keydown', interaction);
    document.addEventListener('visibilitychange', visibility);
    return () => {
      disposed = true;
      window.removeEventListener('pointerdown', interaction);
      window.removeEventListener('keydown', interaction);
      document.removeEventListener('visibilitychange', visibility);
      audio.current = null;
      void current.stop();
    };
  }, [active, enabled]);

  return { enabled, playing, error, toggle: () => setEnabled(value => !value) };
}

export type ArrivalSound = ReturnType<typeof useArrivalSound>;
