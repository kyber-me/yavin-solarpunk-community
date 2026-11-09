import classification from '../../../dev/harness/2026-11-08/162407-agentes-base-conhecimento/classificacao-002.json';
import './admin.css';

export function AdminPage() {
  const recorded = new Date(classification.registrado_em).toLocaleString('pt-BR', { dateStyle: 'long', timeStyle: 'short' });

  return <div className="admin-shell">
    <a className="admin-skip" href="#admin-title">Ir para a classificação</a>
    <header className="admin-header"><a href="/" aria-label="Yavin, página inicial" className="admin-brand">YAVIN<span>.</span></a><span>PAINEL DE DESENVOLVIMENTO</span><a href="/#/laboratorio">Voltar ao laboratório ↗</a></header>
    <main className="admin-main">
      <div className="admin-eyebrow">HARNESS / CLASSIFICAÇÃO 002</div>
      <h1 id="admin-title" tabIndex={-1}>Agentes e <em>conhecimento.</em></h1>
      <p className="admin-lead">{classification.tarefa}</p>
      <div className="admin-status"><span>AVALIAÇÃO PROVISÓRIA</span><span>Registrada em {recorded}</span></div>

      <section className="admin-scores" aria-label="Notas da classificação">
        <div><span>COMPLEXIDADE</span><strong>{classification.complexidade}<small>/ 5</small></strong><p>{classification.justificativas.complexidade}</p></div>
        <div><span>RISCO</span><strong>{classification.risco}<small>/ 5</small></strong><p>{classification.justificativas.risco}</p></div>
        <div className="admin-level"><span>NÍVEL DA TAREFA</span><strong>{classification.nivel}<small>/ 5</small></strong><p>Maior valor entre complexidade e risco. O planejamento será feito por fases.</p></div>
      </section>

      <div className="admin-columns">
        <section><h2>O que sustenta a nota</h2><ul>{classification.evidencias.map(item => <li key={item.arquivo}><code>{item.arquivo}</code><p>{item.observacao}</p></li>)}</ul></section>
        <section><h2>Pontos para o plano</h2><ol>{classification.incertezas.map(item => <li key={item}>{item}</li>)}</ol><div className="admin-decision"><strong>Diretrizes registradas</strong><p>Reset integral do banco, inclusive checkpoints. Notion como fonte principal; documentos locais como fallback quando estiver indisponível.</p><p>O reset ainda não foi executado.</p></div></section>
      </div>
      <footer className="admin-footer"><span>Registro {classification.task_id} · Git {classification.revisao_git.slice(0, 7)}</span><span>Visualização local de um registro versionado. Acesso provisório pelo atelier.</span></footer>
    </main>
  </div>;
}
