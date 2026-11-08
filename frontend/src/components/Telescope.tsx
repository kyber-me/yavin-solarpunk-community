import { useRef, useState } from 'react';
import { TelescopeObject } from './TelescopeObject';
import './telescope.css';

export type Aim = { x: number; y: number };
export function boundAim(aim: Aim): Aim {
  return { x: Math.max(.04, Math.min(.96, aim.x)), y: Math.max(.06, Math.min(.94, aim.y)) };
}

export function Telescope({ aim, onAim, entering }: { aim: Aim; onAim: (aim: Aim) => void; entering: boolean }) {
  const [zoom, setZoom] = useState(3);
  const [dragging, setDragging] = useState(false);
  const drag = useRef<{ pointer: number; x: number; y: number; aim: Aim } | null>(null);
  const imageWidth = zoom * 370;
  const imageHeight = imageWidth * 1152 / 2048;

  return <div className={`telescope${dragging ? ' is-aiming' : ''}`}>
    <div className="telescope-aim" tabIndex={0} role="region" aria-label="Direcionar luneta" aria-describedby="telescope-help"
      onPointerDown={event => {
        if (entering || event.button !== 0 || !event.isPrimary) return;
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.focus({ preventScroll: true });
        event.currentTarget.setPointerCapture(event.pointerId);
        drag.current = { pointer: event.pointerId, x: event.clientX, y: event.clientY, aim };
        setDragging(true);
      }}
      onPointerMove={event => {
        event.stopPropagation();
        if (!drag.current || event.pointerId !== drag.current.pointer) return;
        onAim(boundAim({ x: drag.current.aim.x + (event.clientX - drag.current.x) / 650, y: drag.current.aim.y + (event.clientY - drag.current.y) / 500 }));
      }}
      onPointerUp={event => {
        drag.current = null;
        setDragging(false);
        if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
      }} onPointerCancel={() => { drag.current = null; setDragging(false); }} onLostPointerCapture={() => { drag.current = null; setDragging(false); }}
      onKeyDown={event => {
        if (entering) return;
        const step = event.shiftKey ? .1 : .025;
        const offsets: Record<string, Aim> = { ArrowLeft: { x: -step, y: 0 }, ArrowRight: { x: step, y: 0 }, ArrowUp: { x: 0, y: -step }, ArrowDown: { x: 0, y: step } };
        if (event.key === 'Home') { event.preventDefault(); onAim({ x: .66, y: .47 }); }
        else if (offsets[event.key]) { event.preventDefault(); onAim(boundAim({ x: aim.x + offsets[event.key].x, y: aim.y + offsets[event.key].y })); }
      }}>
      <TelescopeObject aim={aim} zoom={zoom} />
      <div className="telescope-observation" aria-hidden="true">
        <img src="/images/yavin-chegada-v1.png" alt="" draggable={false} style={{ width: imageWidth, height: imageHeight, transform: `translate(${-aim.x * 100}%, ${-aim.y * 100}%)` }} />
        <span />
      </div>
    </div>
    <div className="telescope-actions">
      <div className="telescope-zoom" role="group" aria-label="Ampliação da luneta">
        <button type="button" aria-label="Diminuir ampliação" disabled={zoom <= 2 || entering} onClick={() => setZoom(value => Math.max(2, value - .5))}>−</button>
        <output aria-live="polite">{zoom}×</output>
        <button type="button" aria-label="Aumentar ampliação" disabled={zoom >= 6 || entering} onClick={() => setZoom(value => Math.min(6, value + .5))}>+</button>
      </div>
    </div>
    <p className="sr-only" id="telescope-help">Arraste a luneta ou use as setas para apontar. Home retorna à estação. Você também pode tocar em uma parte da paisagem para observá-la. Os botões mais e menos ajustam a ampliação.</p>
  </div>;
}
