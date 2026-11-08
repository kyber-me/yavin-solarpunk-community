import { Fragment, type ReactNode } from 'react';
import manifesto from '../../../backend/src/agents/base_knowledge/manifestos/manifesto-solarpunk.md?raw';
import conceptsUrl from '../../../backend/src/agents/base_knowledge/manifestos/conceitos-fundamentais.md?url';
import type { ArrivalSound } from '../arrivalSound';
import { SoundControl } from './SoundControl';
import '../manifesto.css';

// The source is the repository's reference document. Render its text and emphasis
// as React nodes; never execute embedded HTML or duplicate a separately edited copy.
function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[\s\S]+?\*\*|\[[^\]]+\]\([^)]+\)|\*[^*]+\*)/g).filter(Boolean).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={index}>{inline(part.slice(2, -2))}</strong>;
    if (part.startsWith('*') && part.endsWith('*')) return <em key={index}>{inline(part.slice(1, -1))}</em>;
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link) {
      const concepts = link[2] === './conceitos-fundamentais.md';
      const href = concepts ? conceptsUrl : /^https?:\/\//.test(link[2]) ? link[2] : undefined;
      return <a key={index} href={href} download={concepts ? 'conceitos-fundamentais.md' : undefined}>{inline(link[1])}</a>;
    }
    return <Fragment key={index}>{part}</Fragment>;
  });
}

function block(text: string, index: number) {
  if (text.startsWith('# ')) return null;
  if (text.trim() === '---') return <hr key={index} />;
  if (text.startsWith('## ')) return <h2 key={index}>{inline(text.slice(3))}</h2>;
  if (text.startsWith('>')) return <aside key={index} className="manifesto-source">{text.split('\n').map((line, i) => <p key={i}>{inline(line.replace(/^>\s?/, '').trimEnd())}</p>)}</aside>;
  if (text.startsWith('- ')) return <ul key={index}>{text.split('\n').map((line, i) => <li key={i}>{inline(line.replace(/^- /, ''))}</li>)}</ul>;
  const normalized = text.replace(/\n/g, ' ');
  if (normalized.startsWith('**Somos solarpunks porque')) return <blockquote className="manifesto-declaration" key={index}><p>{inline(normalized)}</p></blockquote>;
  if (normalized.startsWith('**O solarpunk é um futuro')) return <p className="manifesto-closing" key={index}>{inline(normalized)}</p>;
  return <p key={index}>{inline(normalized)}</p>;
}

export function ManifestoPage({ sound }: { sound: ArrivalSound }) {
  const blocks = manifesto.trim().split(/\n\s*\n/);
  const metadata = blocks.find(text => text.startsWith('>'));
  return <div className="manifesto-shell">
    <a className="skip-link" href="#manifesto-title" onClick={event => { event.preventDefault(); document.getElementById('manifesto-title')?.focus(); }}>Ir para o manifesto</a>
    <header className="manifesto-header">
      <a href="#/" className="arrival-brand" aria-label="Yavin, início"><span>yavin<span className="arrival-brand-dot">.</span></span></a>
      <nav aria-label="Menu superior"><a href="#/">Início</a><a href="#/manifesto" aria-current="page">Manifesto</a></nav>
      <SoundControl sound={sound} />
    </header>
    <main>
      <section className="manifesto-cover" aria-labelledby="manifesto-title">
        <div className="manifesto-cover-copy"><h1 id="manifesto-title" tabIndex={-1}>Manifesto<br /><em>Solarpunk.</em></h1>{metadata && block(metadata, -1)}<a className="manifesto-read" href="#manifesto-text" onClick={event => { event.preventDefault(); document.getElementById('manifesto-text')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth' }); document.getElementById('manifesto-text')?.focus({ preventScroll: true }); }}>Ler o manifesto <span aria-hidden="true">↓</span></a></div>
        <figure><img src="/images/manifesto-solarpunk-v1.png" alt="Ilustração de uma oficina comunitária solarpunk, com pessoas, ferramentas, um pequeno robô e vegetação tropical." /></figure>
      </section>
      <article id="manifesto-text" className="manifesto-text" aria-label="Texto integral do Manifesto Solarpunk" tabIndex={-1}>{blocks.filter(text => text !== metadata).map(block)}</article>
    </main>
    <footer className="manifesto-footer"><a href="#/">← Voltar a Yavin</a><a href="#manifesto-title" onClick={event => { event.preventDefault(); window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth' }); document.getElementById('manifesto-title')?.focus({ preventScroll: true }); }}>Voltar ao início ↑</a></footer>
    <p className="sr-only" role="status">{sound.error}</p>
  </div>;
}
