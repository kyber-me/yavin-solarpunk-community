import { useEffect, useRef, useState, type FormEvent } from 'react';
import { authorizeIdealizador, hasIdealizadorAccess } from '../idealizadorAccess';
import '../idealizador.css';

export function IdealizadorLoginPage() {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);

  useEffect(() => { heading.current?.focus(); }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pending || !key.trim()) return;
    setPending(true);
    setError('');
    try {
      if (!hasIdealizadorAccess()) await authorizeIdealizador(key);
      window.location.hash = '/mapa';
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível validar o acesso.');
    } finally {
      setPending(false);
    }
  }

  return <main className="idealizador-login" aria-labelledby="idealizador-login-title">
    <a className="idealizador-skip" href="#idealizador-login-title">Ir para o acesso</a>
    <header className="idealizador-header">
      <a href="#/" className="idealizador-brand" aria-label="Yavin, página inicial">yavin<span>.</span></a>
      <a href="#/visita">Voltar à visita ↗</a>
    </header>
    <section className="idealizador-card">
      <span className="eyebrow">ACESSO RESERVADO</span>
      <h1 id="idealizador-login-title" ref={heading} tabIndex={-1}>Área do <em>Idealizador.</em></h1>
      <p>Uma passagem provisória para a bancada de desenvolvimento.</p>
      <form onSubmit={submit}>
        <label htmlFor="idealizador-key">Palavra-chave</label>
        <input id="idealizador-key" type="password" autoComplete="current-password" value={key}
          onChange={event => { setKey(event.target.value); setError(''); }} disabled={pending} required />
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="primary-button" type="submit" disabled={pending || !key.trim()}>
          {pending ? 'Verificando…' : 'Entrar'} <span aria-hidden="true">↗</span>
        </button>
      </form>
      <small>Este acesso é um mecanismo provisório de desenvolvimento, não uma autenticação de produção.</small>
    </section>
  </main>;
}
