import { useEffect, useRef, useState, type RefObject } from 'react';
import silasMapArtwork from '../assets/silas-mapa.png';
import laboratoryArtwork from '../assets/laboratorio.png';
import { useMapPan } from '../useMapPan';
import { WorkshopReference } from './WorkshopReference';

export function MapView({ hidden, headingRef, expanded, onToggleExpanded, chatOpen, onToggleChat, chatButtonRef, onOpenSilasChat, visitor = false }: {
  visitor?: boolean;
  hidden: boolean;
  headingRef: RefObject<HTMLHeadingElement | null>;
  expanded: boolean;
  onToggleExpanded: () => void;
  chatOpen: boolean;
  onToggleChat: () => void;
  chatButtonRef: RefObject<HTMLButtonElement | null>;
  onOpenSilasChat: () => void;
}) {
  const [imageFailed, setImageFailed] = useState(false);
  const expandButton = useRef<HTMLButtonElement>(null);
  const previousExpanded = useRef(expanded);
  const { viewportRef, pan, dragging, pressed, grabPoint, zoom, minZoom, maxZoom, setZoom, zoomIn, zoomOut, reset, handlers } = useMapPan();

  useEffect(() => {
    if (previousExpanded.current === expanded) return;
    previousExpanded.current = expanded;
    setZoom(expanded ? minZoom : maxZoom);
    expandButton.current?.focus({ preventScroll: true });
    if (!expanded) expandButton.current?.scrollIntoView({ block: 'nearest' });
  }, [expanded, minZoom, maxZoom, setZoom]);

  const territoryId = visitor ? 'visitor-territory-title' : 'territory-title';
  const panHelpId = visitor ? 'visitor-map-pan-help' : 'map-pan-help';
  const gridId = visitor ? 'visitor-isometric-grid' : 'isometric-grid';

  return <main className="map-view" hidden={hidden} aria-labelledby={expanded ? territoryId : 'map-title'} onKeyDown={event => {
    if (expanded && event.key === 'Escape') {
      event.preventDefault();
      onToggleExpanded();
    }
  }}>
    {!visitor && <section className="arrival" hidden={expanded} aria-label="Oficina de futuros possíveis">
      <div className="arrival-copy">
        <span className="eyebrow">LABORATÓRIO DE INVESTIGAÇÃO · SOLARPUNK</span>
        <h1 id="map-title" ref={!expanded ? headingRef : undefined} tabIndex={-1}>O futuro se<br />faz <span className="together">junto<svg viewBox="0 0 300 16" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11Q145-4 296 6M24 15Q146 3 273 11" /></svg></span><span className="headline-period">.</span></h1>
        <div className="arrival-bottom"><p>Uma comunidade começa com perguntas.<br />Aqui, pessoas e agentes investigam<br className="desktop-break" /> o que podemos construir.</p><a className="action-link" href="#/laboratorio">Abrir a bancada<span aria-hidden="true">↗</span></a></div>
      </div>
      <WorkshopReference />
    </section>}
    <section className="territory-bench" aria-label="Território e primeira investigação">
    <div className="territory-module">
    <header className="module-heading"><h2 id={territoryId} ref={expanded ? headingRef : undefined} tabIndex={-1}><span aria-hidden="true">⌖</span> Território em formação</h2><span>UMA ESTAÇÃO. MUITAS POSSIBILIDADES.</span>
      <div className="map-module-actions" hidden={visitor}>
      <button ref={expandButton} className="map-size-toggle" type="button" onClick={onToggleExpanded} aria-pressed={expanded} aria-label={expanded ? 'Recolher mapa' : 'Expandir mapa'} title={expanded ? 'Recolher mapa (Esc)' : 'Expandir mapa'}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d={expanded ? 'M3 8h5V3m8 0v5h5M3 16h5v5m8 0v-5h5' : 'M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5'} /></svg>
        <span>{expanded ? 'Recolher' : 'Expandir'}</span>
      </button>
      <button ref={chatButtonRef} type="button" className="map-chat-toggle" onClick={onToggleChat} aria-expanded={chatOpen} aria-controls="conversation-surface" aria-label={chatOpen ? 'Recolher chat' : 'Abrir chat'} title={chatOpen ? 'Recolher chat' : 'Abrir chat'}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M4 4h16v12H9l-5 4Z" /></svg><span>Conversar</span>
      </button>
      </div>
    </header>
    <div ref={viewportRef} className={`map-stage${pressed ? ' is-grabbing' : ''}${dragging ? ' is-panning' : ''}`} tabIndex={0} role="region" aria-label="Mapa do laboratório" aria-describedby={panHelpId} {...handlers}>
      <p id={panHelpId} className="sr-only">Pressione e segure para arrastar o mapa. Use a roda do mouse para aproximar ou afastar. Pelo teclado, use as setas para deslocar, mais e menos para zoom e Home para centralizar. O movimento é limitado.{!visitor && ' Para entrar, clique no edifício ou no título Laboratório.'}</p>
      <div className="map-world" style={{ transform: `translate3d(${pan.x}px, ${pan.y}px, 0) scale(${zoom})` }}>
        <svg className="map-grid" width="2400" height="1400" aria-hidden="true">
          <defs><pattern id={gridId} width="112" height="64" patternUnits="userSpaceOnUse"><path d="M 56 0 L 112 32 L 56 64 L 0 32 Z" fill="none" /></pattern></defs>
          <rect width="100%" height="100%" fill={`url(#${gridId})`} />
        </svg>
        <section className="map-location" aria-label="Estação científica de Yavin">
          <div className="laboratory-artwork">
            {imageFailed ? <p className="artwork-error" role="status">A ilustração não pôde ser carregada. Você pode entrar pelo link abaixo.</p> : <svg className="laboratory-scene" viewBox="0 0 1536 1024" aria-label="Laboratório: estação hexagonal com claraboia, painéis solares e vegetação tropical" role="group">
              <image href={laboratoryArtwork} width="1536" height="1024" preserveAspectRatio="xMidYMid meet" onError={() => setImageFailed(true)} />
              {!visitor && <a href="#/laboratorio" aria-label="Entrar no laboratório pelo mapa" tabIndex={-1}>
                <title>Entrar no laboratório</title>
                <path className="laboratory-hit-area" d="M 380 200 L 780 70 L 1175 200 L 1180 300 L 1400 420 L 1390 630 L 1100 830 L 740 900 L 390 760 L 235 625 L 215 450 L 280 350 Z" />
              </a>}
              <foreignObject x="1055" y="570" width="370" height="380">
                {visitor ? <div className="map-citizen map-citizen-static"><img src={silasMapArtwork} alt="Silas, junto à estação científica" width={512} height={768} draggable={false} /><span>Silas</span></div> : <button className="map-citizen" type="button" onClick={onOpenSilasChat} aria-label="Conversar com Silas" aria-controls="conversation-surface" title="Conversar com Silas">
                  <img src={silasMapArtwork} alt="" width={512} height={768} draggable={false} />
                  <span>Silas <span aria-hidden="true">↗</span></span>
                </button>}
              </foreignObject>
            </svg>}
          </div>
          <div className="map-location-caption">
            <h3>{visitor ? 'Laboratório' : <a href="#/laboratorio" className="laboratory-title-link" aria-label="Entrar no laboratório">Laboratório <span aria-hidden="true">↗</span></a>}</h3>
            <p className="map-description">{visitor ? 'Estação científica · o primeiro lugar de Yavin' : 'Estação científica · entrar para conversar'}</p>
          </div>
        </section>
      </div>
      {pressed && <span className="map-grab-feedback" style={{ left: grabPoint.x, top: grabPoint.y }} aria-hidden="true" />}
      <div className="map-controls" role="group" aria-label="Controles do mapa">
        <button type="button" onClick={zoomIn} aria-label="Aproximar mapa" title="Aproximar mapa" disabled={zoom >= maxZoom}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg></button>
        <button type="button" onClick={zoomOut} aria-label="Afastar mapa" title="Afastar mapa" disabled={zoom <= minZoom}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M5 12h14" /></svg></button>
        <button type="button" onClick={reset} aria-label="Centralizar mapa" title="Centralizar mapa" disabled={pan.x === 0 && pan.y === 0}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><circle cx="12" cy="12" r="6" /><path d="M12 2v5m0 10v5M2 12h5m10 0h5" /></svg>
        </button>
      </div>
    </div>
    <footer className="map-footer"><span>Arraste para explorar · role para aproximar</span><span>{Math.round(zoom * 100)}%</span></footer>
    </div>
    {!visitor && <aside className="investigation-note" hidden={expanded} aria-labelledby="energy-title">
      <div className="note-label"><span>O PRIMEIRO CAMPO</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m13 2-9 12h7l-1 8 10-12h-8Z" /></svg></div>
      <h2 id="energy-title">Energia<br /> para começar.</h2>
      <p>Como gerar, armazenar e compartilhar a energia de uma comunidade?</p>
      <div className="research-topics"><span>GERAÇÃO</span><span>ARMAZENAMENTO</span><span>DISTRIBUIÇÃO</span></div>
      <a href="#/laboratorio" className="note-link">Investigar com Silas <span aria-hidden="true">↗</span></a>
      <small>Um ponto de partida, aberto à investigação.</small>
    </aside>}
    </section>
    <footer className="territory-footer" hidden={expanded}><span>YAVIN / UM EXPERIMENTO EM COMUNIDADE</span><span>Investigar. Experimentar. Construir.</span></footer>
  </main>;
}
