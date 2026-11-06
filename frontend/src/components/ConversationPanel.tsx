import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { newConversation, readConversations, STORAGE_KEY, type Conversation, type Mode } from '../conversations';

import silasAvatar from '../assets/silas-avatar.png';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

function responseText(value: unknown): string {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return value.map(responseText).filter(Boolean).join('\n');
  if (value && typeof value === 'object') {
    const item = value as Record<string, unknown>;
    if ('content' in item) return responseText(item.content);
    if ('text' in item) return responseText(item.text);
  }
  return value == null ? '' : JSON.stringify(value);
}

function Icon({ name }: { name: 'plus' | 'send' | 'chat' | 'group' | 'arrow' }) {
  const paths: Record<typeof name, ReactNode> = {
    plus: <path d="M12 5v14M5 12h14" />,
    send: <><path d="m4 11 8-8 8 8M12 3v18" /></>,
    chat: <path d="M20 11.5a8 8 0 0 1-8 8H5l-3 3v-11a9 9 0 0 1 18 0Z" />,
    group: <><circle cx="9" cy="8" r="3" /><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M21 20v-2a6 6 0 0 0-4-5" /></>,
    arrow: <path d="m8 5 7 7-7 7" />,
  };
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function CreateConversation({ mode, onCreate, onCancel }: {
  mode: Mode; onCreate: (title: string, participants: string[]) => void; onCancel: () => void;
}) {
  const [title, setTitle] = useState('');
  const [names, setNames] = useState('');
  const [error, setError] = useState('');
  function submit(event: FormEvent) {
    event.preventDefault();
    const participants = ['Silas', ...names.split(',').map(name => name.trim()).filter(Boolean)]
      .filter((name, index, values) => values.findIndex(item => item.toLocaleLowerCase() === name.toLocaleLowerCase()) === index);
    if (mode === 'meeting' && participants.length < 2) {
      setError('Inclua pelo menos mais um agente além de Silas.');
      return;
    }
    onCreate(title.trim() || (mode === 'meeting' ? 'Nova reunião' : 'Nova conversa'), mode === 'meeting' ? participants : ['Silas']);
  }
  return <form className="create-form" onSubmit={submit}>
    <label htmlFor="conversation-title">{mode === 'meeting' ? 'Nome da reunião' : 'Nome da conversa'}</label>
    <input id="conversation-title" autoFocus maxLength={80} value={title} onChange={event => setTitle(event.target.value)} placeholder={mode === 'meeting' ? 'O que vamos investigar?' : 'Sobre o que vamos conversar?'} />
    {mode === 'meeting' && <>
      <label htmlFor="participant-names">Outros agentes</label>
      <input id="participant-names" value={names} maxLength={240} onChange={event => { setNames(event.target.value); setError(''); }} placeholder="Nomes separados por vírgula" aria-describedby="participants-help" aria-invalid={!!error} />
      <small id="participants-help">Silas já está incluído. Participantes são apenas uma configuração local nesta prévia.</small>
    </>}
    {error && <p role="alert" className="form-error">{error}</p>}
    <div className="form-actions"><button type="button" className="text-button" onClick={onCancel}>Cancelar</button><button className="primary-button" type="submit">{mode === 'meeting' ? 'Criar reunião' : 'Criar conversa'}<Icon name="arrow" /></button></div>
  </form>;
}

const time = (date: string) => new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date(date));

export function ConversationPanel({ drawer = false, onCollapse, silasChatRequest = 0 }: { drawer?: boolean; onCollapse?: () => void; silasChatRequest?: number }) {
  const [initial] = useState(readConversations);
  const [conversations, setConversations] = useState(initial.conversations);
  const [warning, setWarning] = useState(initial.warning);
  const [mode, setMode] = useState<Mode>('conversation');
  const [activeId, setActiveId] = useState(initial.conversations.find(item => item.mode === 'conversation')?.id ?? '');
  const [creating, setCreating] = useState(false);
  const [announcement, setAnnouncement] = useState('');
  const [sending, setSending] = useState(false);
  const handledSilasRequest = useRef(0);
  const history = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const filtered = conversations.filter(item => item.mode === mode);
  const active = filtered.find(item => item.id === activeId);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations)); }
    catch { setWarning('Não foi possível salvar neste navegador. O histórico será mantido somente enquanto esta página estiver aberta.'); }
  }, [conversations]);

  useEffect(() => {
    history.current?.scrollTo({ top: history.current.scrollHeight });
  }, [activeId, active?.messages.length]);

  useEffect(() => {
    if (handledSilasRequest.current === silasChatRequest) return;
    handledSilasRequest.current = silasChatRequest;
    setMode('conversation');
    setCreating(false);
    const selected = conversations.find(item => item.id === activeId && item.mode === 'conversation')
      ?? conversations.find(item => item.mode === 'conversation');
    if (selected) setActiveId(selected.id);
    else {
      const item = newConversation('conversation', 'Conversa com Silas', ['Silas']);
      setConversations(items => [item, ...items]);
      setActiveId(item.id);
    }
  }, [silasChatRequest, conversations, activeId]);

  function switchMode(next: Mode) {
    setMode(next);
    setCreating(false);
    setActiveId(conversations.find(item => item.mode === next)?.id ?? '');
  }

  function updateActive(update: (item: Conversation) => Conversation) {
    setConversations(items => items.map(item => item.id === activeId ? update(item) : item));
  }

  function create(title: string, participants: string[]) {
    const item = newConversation(mode, title, participants);
    setConversations(items => [item, ...items]);
    setActiveId(item.id);
    setCreating(false);
    setAnnouncement(`${mode === 'meeting' ? 'Reunião criada' : 'Conversa criada'}: ${title}`);
    requestAnimationFrame(() => composer.current?.focus());
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    if (sending || !active?.draft.trim()) return;
    const content = active.draft.trim();
    const message = { id: crypto.randomUUID(), author: 'Você', content, createdAt: new Date().toISOString() };
    updateActive(item => ({ ...item, draft: '', messages: [...item.messages, message] }));

    if (mode === 'meeting') {
      setAnnouncement('Mensagem registrada localmente. As reuniões ainda não estão conectadas.');
      composer.current?.focus();
      return;
    }

    setSending(true);
    setAnnouncement('Mensagem enviada para Silas. Aguardando resposta.');

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          sender_id: 'idealizador',
          thread_id: active.id,
        }),
      });
      const payload = await response.json() as {
        data?: unknown;
        error?: { message?: string } | null;
      };

      if (!response.ok || payload.error) {
        throw new Error(payload.error?.message ?? 'Não foi possível obter uma resposta de Silas.');
      }

      const answer = responseText(payload.data);
      if (!answer) throw new Error('Silas retornou uma resposta vazia.');

      updateActive(item => ({
        ...item,
        messages: [...item.messages, {
          id: crypto.randomUUID(),
          author: 'Silas',
          content: answer,
          createdAt: new Date().toISOString(),
        }],
      }));
      setAnnouncement('Resposta de Silas recebida.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Não foi possível conectar com Silas.';
      updateActive(item => ({
        ...item,
        messages: [...item.messages, {
          id: crypto.randomUUID(),
          author: 'Sistema',
          content: message,
          createdAt: new Date().toISOString(),
        }],
      }));
      setAnnouncement(message);
    } finally {
      setSending(false);
      composer.current?.focus();
    }
  }

  return <aside className={`conversation-panel${drawer ? ' drawer-panel' : ''}`} aria-labelledby="panel-title">
    <header className="panel-header">
      <div className="panel-eyebrow"><span className="tiny-dot" />{drawer ? 'TERRITÓRIO / CONVERSAS' : 'LABORATÓRIO / CONVERSAS'}<span>COM SILAS</span></div>
      <div className="panel-heading"><h1 id="panel-title" tabIndex={-1}>Vamos pensar juntos.</h1><div className="panel-tools"><img className="silas-mark silas-portrait" src={silasAvatar} alt="Retrato de Silas" width={38} height={38} />{onCollapse && <button className="drawer-close" type="button" onClick={onCollapse} aria-label="Fechar chat" title="Recolher chat (Esc)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg></button>}</div></div>
      <p>Perguntas, hipóteses e próximos passos.</p>
    </header>

    <div className="panel-directory">
    <nav className="mode-switch" aria-label="Tipo de conversa">
      <button aria-pressed={mode === 'conversation'} onClick={() => switchMode('conversation')}><Icon name="chat" />Conversas<span>{conversations.filter(item => item.mode === 'conversation').length}</span></button>
      <button aria-pressed={mode === 'meeting'} onClick={() => switchMode('meeting')}><Icon name="group" />Reuniões<span>{conversations.filter(item => item.mode === 'meeting').length}</span></button>
    </nav>

    <section className="conversation-directory" aria-label={mode === 'meeting' ? 'Suas reuniões' : 'Suas conversas'}>
      <div className="directory-heading"><span>{mode === 'meeting' ? 'MESA DE AGENTES' : 'COM SILAS'}</span><button className="new-button" onClick={() => setCreating(value => !value)} aria-expanded={creating}><Icon name="plus" />{mode === 'meeting' ? 'Nova reunião' : 'Nova conversa'}</button></div>
      {creating ? <CreateConversation key={mode} mode={mode} onCreate={create} onCancel={() => setCreating(false)} /> : <div className="conversation-list">
        {filtered.map(item => <button key={item.id} className={`conversation-item ${item.id === activeId ? 'selected' : ''}`} aria-current={item.id === activeId ? 'true' : undefined} onClick={() => { setActiveId(item.id); setAnnouncement(''); }}>
          <Icon name={mode === 'meeting' ? 'group' : 'chat'} /><span><strong>{item.title}</strong><small>{item.messages.at(-1)?.content ?? (mode === 'meeting' ? `${item.participants.length} agentes · ainda sem mensagens` : 'Uma pergunta pode ser o começo.')}</small></span><Icon name="arrow" />
        </button>)}
        {!filtered.length && <p className="directory-empty">Reúna diferentes perspectivas em uma mesma conversa.</p>}
      </div>}
    </section>

    {warning && <p className="storage-warning" role="alert">{warning}</p>}
    </div>
    <div className="thread-workspace" aria-busy={sending}>
    {active ? <>
      <div className="thread-heading"><span className="thread-avatar" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <img className="silas-portrait" src={silasAvatar} alt="" width={32} height={34} />}</span><div><h2>{active.title}</h2><p>{mode === 'meeting' ? `${active.participants.length} agentes nesta mesa` : 'Silas · colaborador de Yavin'}</p></div><span className="local-tag">{mode === 'meeting' ? 'REGISTRO LOCAL' : 'SILAS'}</span></div>
      {mode === 'meeting' && <ul className="participant-list" aria-label="Agentes participantes">{active.participants.map(name => <li key={name}>{name}</li>)}</ul>}
      <div className="message-history" ref={history} role="log" aria-label={`Mensagens de ${active.title}`} aria-live="polite" tabIndex={0}>
        {!active.messages.length ? <div className="thread-empty">
          <span className="empty-illustration" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <img className="silas-portrait" src={silasAvatar} alt="" width={48} height={48} />}</span>
          <span className="eyebrow">{mode === 'meeting' ? 'PERSPECTIVAS EM COMUM' : 'UM PRIMEIRO ENCONTRO'}</span>
          <h3>{mode === 'meeting' ? 'Uma mesa aberta.' : 'O que vamos descobrir?'}</h3>
          <p>{mode === 'meeting' ? 'Apresente uma questão para os agentes desta reunião. Cada perspectiva terá espaço no mesmo histórico.' : 'Traga uma pergunta, uma ideia ainda solta ou algo que você gostaria de investigar com Silas.'}</p>
          <button className="suggestion" onClick={() => { updateActive(item => ({ ...item, draft: mode === 'meeting' ? 'Que perspectivas podemos reunir para investigar energia em Yavin?' : 'Silas, por onde podemos começar a investigar energia em Yavin?' })); composer.current?.focus(); }}>Começar por energia<Icon name="arrow" /></button>
        </div> : <><div className="history-divider">{new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long' }).format(new Date(active.createdAt))}</div>{active.messages.map(message => <article key={message.id} className={`message message-${message.author === 'Você' ? 'user' : message.author === 'Silas' ? 'agent' : 'system'}`}><header><span>{message.author}</span><time dateTime={message.createdAt}>{time(message.createdAt)}</time></header><p>{message.content}</p></article>)}<p className="pending-note">{mode === 'meeting' ? 'Reunião local. Mensagens salvas neste navegador.' : 'Histórico salvo neste navegador.'}</p></>}
      </div>
      <form className="composer" onSubmit={send}>
        <label className="sr-only" htmlFor="message">{mode === 'meeting' ? 'Mensagem para a reunião' : 'Mensagem para Silas'}</label>
        <div className="composer-box"><textarea id="message" ref={composer} rows={3} maxLength={12000} disabled={sending} placeholder={mode === 'meeting' ? 'Traga uma questão para a mesa…' : 'Escreva para Silas…'} value={active.draft} onChange={event => updateActive(item => ({ ...item, draft: event.target.value }))} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} /><div className="composer-actions"><span>Enter para enviar · Shift + Enter para nova linha</span><button className="send-button" type="submit" disabled={sending || !active.draft.trim()} aria-label="Enviar mensagem"><Icon name="send" /></button></div></div>
        <p className="connection-note"><span className="tiny-dot" />{mode === 'meeting' ? 'Reunião local · agentes ainda não conectados' : sending ? 'Aguardando a resposta de Silas…' : 'Mensagens enviadas à API local de Silas'}</p>
      </form>
    </> : <div className="no-meeting"><Icon name="group" /><h2>Mais vozes, uma investigação.</h2><p>Crie uma reunião para organizar uma conversa com Silas e outros agentes.</p><button className="primary-button" onClick={() => setCreating(true)}><Icon name="plus" />Criar primeira reunião</button><small>Nesta prévia, participantes e mensagens são salvos apenas neste navegador.</small></div>}
    </div>
    <span className="sr-only" role="status">{announcement}</span>
  </aside>;
}
