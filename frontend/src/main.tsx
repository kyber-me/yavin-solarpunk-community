import { StrictMode, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { createRoot } from 'react-dom/client';
import { ConversationPanel } from './components/ConversationPanel';
import { MapView } from './components/MapView';
import { WorkshopReference } from './components/WorkshopReference';
import { Arrival } from './components/Arrival';
import { VisitorMap } from './components/VisitorMap';
import { useArrivalSound } from './arrivalSound';
import { ManifestoPage } from './components/ManifestoPage';
import { AdminPage } from './components/AdminPage';
import { IdealizadorLoginPage } from './components/IdealizadorLoginPage';
import { hasIdealizadorAccess } from './idealizadorAccess';
import './styles.css';
import './map.css';

function subscribeToRoute(onChange: () => void) {
  window.addEventListener('hashchange', onChange);
  return () => window.removeEventListener('hashchange', onChange);
}
const getRoute = () => window.location.hash === '#/laboratorio' ? 'laboratory' : 'map';

function Workspace({ active }: { active: boolean }) {
  const route = useSyncExternalStore(subscribeToRoute, getRoute);
  const inLaboratory = route === 'laboratory';
  const [mapExpanded, setMapExpanded] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [silasChatRequest, setSilasChatRequest] = useState(0);
  const chatButton = useRef<HTMLButtonElement>(null);
  const previousChatOpen = useRef(false);
  const mapHeading = useRef<HTMLHeadingElement>(null);
  const previousRoute = useRef(route);

  useEffect(() => {
    if (!active) return;
    document.title = inLaboratory ? 'Bancada de conversa · Yavin' : 'Yavin · Oficina de futuros possíveis';
    if (previousRoute.current !== route) {
      if (inLaboratory) document.getElementById('panel-title')?.focus();
      else mapHeading.current?.focus();
    }
    previousRoute.current = route;
  }, [route, inLaboratory, active]);

  useEffect(() => {
    if (!active || inLaboratory) return;
    if (chatOpen) document.getElementById('panel-title')?.focus({ preventScroll: true });
    else if (previousChatOpen.current) {
      chatButton.current?.focus({ preventScroll: true });
      chatButton.current?.scrollIntoView({ block: 'nearest' });
    }
    previousChatOpen.current = chatOpen;
  }, [chatOpen, inLaboratory, silasChatRequest, active]);

  return <div className={`app-shell ${inLaboratory ? 'in-laboratory' : mapExpanded ? 'map-expanded' : ''}`}>
    <a className="skip-link" href={inLaboratory ? '#panel-title' : '#map-title'} onClick={event => {
      event.preventDefault();
      (inLaboratory ? document.getElementById('panel-title') : mapHeading.current)?.focus();
    }}>Ir para o conteúdo</a>
    <header className="workspace-header">
      <a className="wordmark" href="#/mapa" aria-label="Yavin, início"><svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><circle cx="20" cy="20" r="7" fill="currentColor" /><path d="M20 0v9m0 22v9M0 20h9m22 0h9M6 6l7 7m14 14 7 7M6 34l7-7M27 13l7-7" stroke="currentColor" strokeWidth="3" /></svg>YAVIN<span className="brand-period">.</span></a>
      <span className="workspace-caption">Oficina de futuros possíveis</span>
      <nav className="header-navigation" aria-label="Navegação principal"><a href="#/mapa" aria-current={!inLaboratory ? 'page' : undefined}>Território</a><a href="#/laboratorio" aria-current={inLaboratory ? 'page' : undefined}>Laboratório <span aria-hidden="true">↗</span></a><a href="#/manifesto">Manifesto</a><a href="#/admin">Harness</a></nav>
      <span className="preview-badge">PRÉVIA LOCAL</span>
    </header>
    <nav className="workspace-rail" aria-label="Espaços de trabalho">
      <a href="#/mapa" aria-current={!inLaboratory ? 'page' : undefined}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2ZM9 3v16M15 5v16" /></svg><span>Território</span></a>
      <a href="#/laboratorio" aria-current={inLaboratory ? 'page' : undefined}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M8 3h8M10 3v7L4 20h16l-6-10V3M7 15h10" /></svg><span>Laboratório</span></a>
      <a href="#/admin" aria-label="Abrir painel de harness">Harness</a><span className="rail-note">PENSAR · FAZER · REFAZER</span>
    </nav>
    <div className={`workspace-content ${inLaboratory ? 'laboratory-workspace' : 'map-workspace'} ${!inLaboratory && chatOpen ? 'drawer-open' : ''}`} onKeyDownCapture={event => {
      if (!inLaboratory && chatOpen && event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        setChatOpen(false);
      }
    }}>
      <MapView hidden={inLaboratory} headingRef={mapHeading} expanded={mapExpanded} onToggleExpanded={() => setMapExpanded(value => !value)} chatOpen={chatOpen} onToggleChat={() => setChatOpen(value => !value)} chatButtonRef={chatButton} onOpenSilasChat={() => { setChatOpen(true); setSilasChatRequest(value => value + 1); }} />
      <main className="open-workspace" hidden={!inLaboratory} aria-label="Contexto do laboratório">
        <a className="back-to-map" href="#/mapa">← Voltar ao território</a>
        <div className="lab-context"><span className="eyebrow">A BANCADA ESTÁ ABERTA</span><h2>Ideias soltas.<br />Futuros<br /><em>em construção.</em></h2><p>Um lugar para pensar junto, fazer perguntas e encontrar o próximo passo.</p></div>
        <WorkshopReference compact />
        <div className="lab-focus"><span className="eyebrow">PRIMEIRO CAMPO DE INVESTIGAÇÃO</span><h3>Energia <span aria-hidden="true">↗</span></h3><p>Geração, armazenamento e distribuição. Começamos por uma pergunta pequena.</p></div>
        <p className="context-footnote">Uma hipótese abre caminhos.<br />Uma decisão precisa de fundamentos.</p>
      </main>
      <div id="conversation-surface" className="conversation-surface" hidden={!inLaboratory && !chatOpen}>
        <ConversationPanel silasChatRequest={silasChatRequest} drawer={!inLaboratory} onCollapse={!inLaboratory ? () => setChatOpen(false) : undefined} />
      </div>
    </div>
  </div>;
}

const getExperience = () => {
  const hash = window.location.hash;
  if (hash === '#/admin') return hasIdealizadorAccess() ? 'admin' : 'idealizador-login';
  if (hash === '#/acesso') return 'idealizador-login';
  if (hash === '#/mapa' || hash === '#/laboratorio') return 'atelier';
  if (hash === '#/visita') return 'visit';
  if (hash === '#/manifesto') return 'manifesto';
  if (window.location.pathname === '/admin') return hasIdealizadorAccess() ? 'admin' : 'idealizador-login';
  return 'arrival';
};

function App() {
  const experience = useSyncExternalStore(subscribeToRoute, getExperience);
  const sound = useArrivalSound(experience !== 'atelier' && experience !== 'admin');
  const [atelierVisited, setAtelierVisited] = useState(experience === 'atelier');
  const previousExperience = useRef(experience);
  useEffect(() => {
    if (experience === 'atelier') setAtelierVisited(true);
    else document.title = experience === 'visit' ? 'Visite Yavin · Território em formação' : experience === 'manifesto' ? 'Manifesto Solarpunk · Yavin' : experience === 'admin' ? 'Admin · Yavin' : experience === 'idealizador-login' ? 'Acesso do Idealizador · Yavin' : 'Yavin · O futuro tem lugar';
    if (previousExperience.current !== experience) {
      window.scrollTo(0, 0);
      if (experience === 'arrival') document.getElementById('arrival-title')?.focus();
      if (experience === 'visit') document.getElementById('visitor-territory-title')?.focus();
      if (experience === 'manifesto') document.getElementById('manifesto-title')?.focus();
      if (experience === 'admin') document.getElementById('admin-title')?.focus();
      if (experience === 'idealizador-login') document.getElementById('idealizador-login-title')?.focus();
    }
    previousExperience.current = experience;
  }, [experience]);
  return <>
    {experience === 'arrival' && <Arrival sound={sound} />}
    {experience === 'visit' && <VisitorMap sound={sound} />}
    {experience === 'manifesto' && <ManifestoPage sound={sound} />}
    {experience === 'admin' && <AdminPage />}
    {experience === 'idealizador-login' && <IdealizadorLoginPage />}
    {(atelierVisited || experience === 'atelier') && <div hidden={experience !== 'atelier'}><Workspace active={experience === 'atelier'} /></div>}
  </>;
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
