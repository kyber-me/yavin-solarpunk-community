import { useRef } from 'react';
import { MapView } from './MapView';
import { SoundControl } from './SoundControl';
import type { ArrivalSound } from '../arrivalSound';
import '../visitor.css';

// Visual preview only. Public world state and conversation publication need a backend contract.
export function VisitorMap({ sound }: { sound: ArrivalSound }) {
  const heading = useRef<HTMLHeadingElement>(null);
  const chatButton = useRef<HTMLButtonElement>(null);
  return <div className="visitor-shell map-expanded">
    <header className="visitor-header">
      <a href="#/" className="visitor-brand" aria-label="Yavin, voltar à entrada">yavin<span>.</span></a>
      <p>Todo futuro tem um começo.</p>
      <SoundControl sound={sound} />
      <nav className="visitor-links" aria-label="Menu superior"><a href="#/manifesto">Manifesto</a><a href="#/">Mirante <span aria-hidden="true">↗</span></a></nav>
    </header>
    <MapView hidden={false} headingRef={heading} expanded visitor onToggleExpanded={() => {}} chatOpen={false} onToggleChat={() => {}} chatButtonRef={chatButton} onOpenSilasChat={() => {}} />
    <p role="status" className="sr-only">{sound.error}</p>
  </div>;
}
