import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { paintArrivalEffects } from '../arrivalEffects';
import type { ArrivalSound } from '../arrivalSound';
import { SoundControl } from './SoundControl';
import { Telescope, boundAim, type Aim } from './Telescope';
import '../arrival.css';

export function Arrival({ sound }: { sound: ArrivalSound }) {
  const [entering, setEntering] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);
  const [aim, setAim] = useState<Aim>({ x: .66, y: .47 });
  const scene = useRef<HTMLElement>(null);
  const effectsCanvas = useRef<HTMLCanvasElement>(null);
  const ambient = useMemo(() => ({ canvas: effectsCanvas, listeners: new Set<() => void>() }), []);
  const view = useRef({ x: 0, y: 0 });
  const touchOrigin = useRef<{ x: number; y: number; viewX: number; viewY: number } | null>(null);
  const transitionTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    return () => {
      window.clearTimeout(transitionTimer.current);
    };
  }, []);

  useEffect(() => {
    const canvas = effectsCanvas.current;
    if (!canvas) return;
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    let frame = 0;
    let lastPaint = -Infinity;
    const notify = () => ambient.listeners.forEach(listener => listener());
    function tick(time: number) {
      if (time - lastPaint >= 1000 / 30) {
        paintArrivalEffects(canvas!, time);
        notify();
        lastPaint = time;
      }
      frame = window.requestAnimationFrame(tick);
    }
    function applyPreference() {
      window.cancelAnimationFrame(frame);
      if (preference.matches) {
        const context = canvas!.getContext('2d');
        if (context) {
          context.save();
          context.setTransform(1, 0, 0, 1, 0, 0);
          context.clearRect(0, 0, canvas!.width, canvas!.height);
          context.restore();
        }
        notify();
      } else frame = window.requestAnimationFrame(tick);
    }
    applyPreference();
    preference.addEventListener('change', applyPreference);
    return () => { window.cancelAnimationFrame(frame); preference.removeEventListener('change', applyPreference); };
  }, [ambient, imageFailed]);

  function enter() {
    if (entering) return;
    const lens = scene.current?.querySelector('.telescope-aim')?.getBoundingClientRect();
    const bounds = scene.current?.getBoundingClientRect();
    if (lens && bounds) {
      scene.current?.style.setProperty('--entrance-x', `${lens.left + lens.width / 2 - bounds.left}px`);
      scene.current?.style.setProperty('--entrance-y', `${lens.top + lens.height / 2 - bounds.top}px`);
    }
    setEntering(true);
    const duration = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 1500;
    transitionTimer.current = window.setTimeout(() => { window.location.hash = '/visita'; }, duration);
  }

  function moveView(x: number, y: number) {
    if (entering) return;
    view.current = { x: Math.max(-34, Math.min(34, x)), y: Math.max(-22, Math.min(22, y)) };
    scene.current?.style.setProperty('--look-x', `${view.current.x}px`);
    scene.current?.style.setProperty('--look-y', `${view.current.y}px`);
  }

  return <main ref={scene} className={`arrival-scene${entering ? ' is-entering' : ''}`} aria-labelledby="arrival-title" onDragStart={event => event.preventDefault()}
    onPointerDown={event => {
      if ((event.target as Element).closest('button,a,.telescope') || entering) return;
      const image = scene.current?.querySelector<HTMLImageElement>('.arrival-landscape img');
      if (image?.naturalWidth) {
        const bounds = image.getBoundingClientRect();
        const scale = Math.max(bounds.width / image.naturalWidth, bounds.height / image.naturalHeight);
        const width = image.naturalWidth * scale;
        const height = image.naturalHeight * scale;
        const mobile = window.matchMedia('(max-width:800px)').matches;
        setAim(boundAim({ x: (event.clientX - bounds.left - (bounds.width - width) * (mobile ? .6 : .5)) / width, y: (event.clientY - bounds.top - (bounds.height - height) * (mobile ? .5 : .54)) / height }));
      }
      if (event.pointerType === 'touch') touchOrigin.current = { x: event.clientX, y: event.clientY, viewX: view.current.x, viewY: view.current.y };
    }}
    onPointerMove={event => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const bounds = event.currentTarget.getBoundingClientRect();
      if (event.pointerType === 'mouse') moveView(((event.clientX - bounds.left) / bounds.width - 0.5) * 68, ((event.clientY - bounds.top) / bounds.height - 0.5) * 44);
      else if (touchOrigin.current) moveView(touchOrigin.current.viewX + (event.clientX - touchOrigin.current.x) * 0.32, touchOrigin.current.viewY + (event.clientY - touchOrigin.current.y) * 0.24);
    }} onPointerUp={() => { touchOrigin.current = null; }} onPointerCancel={() => { touchOrigin.current = null; }}
    onPointerLeave={event => { touchOrigin.current = null; if (event.pointerType === 'mouse') moveView(0, 0); }}>
    <div className="arrival-landscape" aria-hidden="true">
      <img src="/images/yavin-chegada-v1.png" alt="" draggable={false} onLoad={() => setImageFailed(false)} onError={() => setImageFailed(true)} />
      {!imageFailed && <canvas ref={effectsCanvas} className="arrival-ambient-effects" width="1024" height="576" />}
    </div>
    <div className="arrival-atmosphere" aria-hidden="true" />
    <div className="arrival-grain" aria-hidden="true" />
    <header className="arrival-header">
      <a className="arrival-brand" href="#/" aria-label="Yavin, início"><Sun /> <span>yavin<span className="arrival-brand-dot">.</span></span></a>
      <nav className="arrival-navigation" aria-label="Menu superior"><a href="#/manifesto">Manifesto</a></nav>
      <SoundControl sound={sound} />
    </header>
    <div className="arrival-intro">
      <h1 id="arrival-title" tabIndex={-1}>O futuro<br />tem <em>lugar.</em></h1>
    </div>
    <div className="arrival-pollen" aria-hidden="true">{Array.from({ length: 12 }, (_, index) => <i key={index} style={{ '--seed': index } as CSSProperties} />)}</div>
    <div className="arrival-invitation">
      <Telescope aim={aim} onAim={setAim} entering={entering} ambient={ambient} />
    </div>
    <button className="arrival-enter" type="button" onClick={enter} disabled={entering} aria-label="Entrar em Yavin">{entering ? 'Entrando…' : 'Entrar'} <span aria-hidden="true">↗</span></button>
    <p className="sr-only" role="status">{entering ? 'Entrando no mapa de Yavin.' : sound.error}</p>
    {imageFailed && <p className="arrival-image-error" role="status">A paisagem não carregou. O acesso ao mapa continua disponível.</p>}
    <div className="arrival-transition" aria-hidden="true" />
  </main>;
}

function Sun() {
  return <svg viewBox="0 0 48 48" fill="none" aria-hidden="true"><circle cx="24" cy="24" r="8" stroke="currentColor" strokeWidth="1.5" /><path d="M24 2v9m0 26v9M2 24h9m26 0h9M8.5 8.5l6.4 6.4m18.2 18.2 6.4 6.4M8.5 39.5l6.4-6.4m18.2-18.2 6.4-6.4" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
