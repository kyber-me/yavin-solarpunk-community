import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { newConversation, readConversations, STORAGE_KEY, type Conversation, type Mode } from '../conversations';

import silasAvatar from '../assets/silas-avatar.png';
import { CreateConversationForm } from './CreateConversationForm';
import { ChatApiError, sendMessage, type AgentOption, type ConversationMetadata } from '../chatApi';

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

function AgentPortrait({ name, className = '' }: { name: string; className?: string }) {
  return name.toLocaleLowerCase() === 'silas'
    ? <img className={`silas-portrait ${className}`} src={silasAvatar} alt={`Retrato de ${name}`} width={38} height={38} />
    : <span className={`agent-monogram ${className}`} aria-label={name}>{name.slice(0, 1).toLocaleUpperCase()}</span>;
}

const time = (date: string) => new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date(date));

export function ConversationPanel({ drawer = false, onCollapse, silasChatRequest = 0 }: { drawer?: boolean; onCollapse?: () => void; silasChatRequest?: number }) {
  const [initial] = useState(readConversations);
  const [conversations, setConversations] = useState(initial.conversations);
  const [warning, setWarning] = useState(initial.warning);
  const [mode, setMode] = useState<Mode>('conversation');
  const [activeId, setActiveId] = useState(initial.conversations.find(item => item.mode === 'conversation')?.id ?? '');
  const [creating, setCreating] = useState(false);
  const [preferSilas, setPreferSilas] = useState(false);
  const [sendError, setSendError] = useState<{ id: string; message: string } | null>(null);
  const sendingLock = useRef(false);
  const activeIdRef = useRef(activeId);
  activeIdRef.current = activeId;
  const [announcement, setAnnouncement] = useState('');
  const [sending, setSending] = useState(false);
  const handledSilasRequest = useRef(0);
  const history = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const filtered = conversations.filter(item => item.mode === mode);
  const active = filtered.find(item => item.id === activeId);
  const agentName = active?.participants[0] ?? 'Agente';
  const readOnly = mode === 'conversation' && !!active && (!active.serverConversationId || !!active.unavailableReason);
  function focusComposer() {
    if (composer.current?.getClientRects().length) composer.current.focus();
  }
  function startCreating() { setPreferSilas(false); setCreating(true); }

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
    const selected = conversations.find(item => item.mode === 'conversation' && item.serverConversationId
      && !item.unavailableReason && item.participants[0]?.toLocaleLowerCase() === 'silas');
    if (selected) { setCreating(false); setActiveId(selected.id); }
    else { setPreferSilas(true); setCreating(true); }
  }, [silasChatRequest, conversations, activeId]);

  function switchMode(next: Mode) {
    setMode(next);
    setCreating(false);
    setPreferSilas(false);
    setActiveId(conversations.find(item => item.mode === next)?.id ?? '');
  }

  function updateActive(update: (item: Conversation) => Conversation) {
    setConversations(items => items.map(item => item.id === activeId ? update(item) : item));
  }

  function create(title: string, participants: string[], remote?: { agent: AgentOption; metadata: ConversationMetadata; resumed: boolean }) {
    const existing = remote ? conversations.find(item => item.serverConversationId === remote.metadata.conversation_id) : undefined;
    const item: Conversation = existing ?? {
      ...newConversation(mode, title, participants),
      ...(remote ? {
        serverConversationId: remote.metadata.conversation_id,
        participantId: remote.agent.id,
        createdAt: remote.metadata.created_at,
        resumed: remote.resumed,
      } : {}),
    };
    if (!existing) setConversations(items => [item, ...items]);
    else setConversations(items => items.map(entry => entry.id === item.id
      ? { ...entry, participants, participantId: remote?.agent.id ?? entry.participantId, resumed: entry.resumed || remote?.resumed, unavailableReason: undefined } : entry));
    setActiveId(item.id);
    setCreating(false);
    setSendError(null);
    setAnnouncement(`${remote?.resumed ? 'Conversa retomada' : mode === 'meeting' ? 'Reunião criada' : 'Conversa criada'}: ${item.title}`);
    requestAnimationFrame(focusComposer);
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    if (sendingLock.current || readOnly || !active?.draft.trim()) return;
    const target = active;
    const content = target.draft.trim();
    const message = { id: crypto.randomUUID(), author: 'Você', kind: 'user' as const, content, createdAt: new Date().toISOString() };
    const updateTarget = (update: (item: Conversation) => Conversation) =>
      setConversations(items => items.map(item => item.id === target.id ? update(item) : item));
    if (target.mode === 'meeting') {
      updateTarget(item => ({ ...item, draft: '', messages: [...item.messages, message] }));
      setAnnouncement('Mensagem registrada localmente. As reuniões ainda não estão conectadas.');
      focusComposer();
      return;
    }
    if (!target.serverConversationId) return;
    sendingLock.current = true;
    setSending(true);
    setSendError(null);
    const recipient = target.participants[0] ?? 'o agente';
    setAnnouncement(`Enviando mensagem para ${recipient}. Aguardando resposta.`);
    try {
      const answer = await sendMessage(target.serverConversationId, content);
      updateTarget(item => ({
        ...item, draft: item.draft === target.draft ? '' : item.draft,
        messages: [...item.messages, message, {
          id: crypto.randomUUID(), author: recipient, kind: 'agent', content: answer, createdAt: new Date().toISOString(),
        }],
      }));
      setAnnouncement(`Resposta de ${recipient} recebida.`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Não foi possível enviar a mensagem.';
      setSendError({ id: target.id, message: reason });
      if (error instanceof ChatApiError && (error.status === 404 || error.status === 409)) {
        updateTarget(item => ({ ...item, unavailableReason: reason }));
      }
      setAnnouncement(reason);
    } finally {
      sendingLock.current = false;
      setSending(false);
      if (activeIdRef.current === target.id) focusComposer();
    }
  }

  return <aside className={`conversation-panel${drawer ? ' drawer-panel' : ''}${creating ? ' is-creating' : ''}`} aria-labelledby="panel-title">
    <header className="panel-header">
      <div className="panel-eyebrow"><span className="tiny-dot" />{drawer ? 'TERRITÓRIO / CONVERSAS' : 'LABORATÓRIO / CONVERSAS'}<span>{mode === 'meeting' ? 'REUNIÕES LOCAIS' : 'CONVERSAS'}</span></div>
      <div className="panel-heading"><h1 id="panel-title" tabIndex={-1}>Vamos pensar juntos.</h1><div className="panel-tools">{active && mode === 'conversation' && <AgentPortrait name={agentName} className="silas-mark" />}{onCollapse && <button className="drawer-close" type="button" onClick={onCollapse} aria-label="Fechar chat" title="Recolher chat (Esc)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg></button>}</div></div>
      <p>Perguntas, hipóteses e próximos passos.</p>
    </header>

    <div className="panel-directory">
    <nav className="mode-switch" aria-label="Tipo de conversa">
      <button aria-pressed={mode === 'conversation'} onClick={() => switchMode('conversation')}><Icon name="chat" />Conversas<span>{conversations.filter(item => item.mode === 'conversation').length}</span></button>
      <button aria-pressed={mode === 'meeting'} onClick={() => switchMode('meeting')}><Icon name="group" />Reuniões<span>{conversations.filter(item => item.mode === 'meeting').length}</span></button>
    </nav>

    <section className="conversation-directory" aria-label={mode === 'meeting' ? 'Suas reuniões' : 'Suas conversas'}>
      <div className="directory-heading"><span>{mode === 'meeting' ? 'MESA DE AGENTES' : 'COM AGENTES'}</span><button className="new-button" onClick={() => { setPreferSilas(false); setCreating(value => !value); }} aria-expanded={creating}><Icon name="plus" />{mode === 'meeting' ? 'Nova reunião' : 'Iniciar conversa'}</button></div>
      {creating ? <CreateConversationForm key={`${mode}:${silasChatRequest}`} mode={mode} preferSilas={preferSilas} onCreate={create} onCancel={() => setCreating(false)} /> : <div className="conversation-list">
        {filtered.map(item => <button key={item.id} className={`conversation-item ${item.id === activeId ? 'selected' : ''}`} aria-current={item.id === activeId ? 'true' : undefined} onClick={() => { setActiveId(item.id); setAnnouncement(''); }}>
          <Icon name={mode === 'meeting' ? 'group' : 'chat'} /><span><strong>{item.title}</strong><small>{item.messages.at(-1)?.content ?? (mode === 'meeting' ? `${item.participants.length} agentes · ainda sem mensagens` : 'Uma pergunta pode ser o começo.')}</small></span><Icon name="arrow" />
        </button>)}
        {!filtered.length && <p className="directory-empty">{mode === 'meeting' ? 'Reúna diferentes perspectivas em uma mesma conversa.' : 'Escolha um agente e inicie uma conversa.'}</p>}
      </div>}
    </section>

    {warning && <p className="storage-warning" role="alert">{warning}</p>}
    </div>
    <div className="thread-workspace" aria-busy={sending}>
    {active ? <>
      <div className="thread-heading"><span className="thread-avatar" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <AgentPortrait name={agentName} />}</span><div><h2>{active.title}</h2><p>{mode === 'meeting' ? `${active.participants.length} agentes nesta mesa` : `${agentName} · colaborador de Yavin`}</p></div><span className="local-tag">{mode === 'meeting' || !active.serverConversationId ? 'REGISTRO LOCAL' : agentName}</span></div>
      {mode === 'meeting' && <ul className="participant-list" aria-label="Agentes participantes">{active.participants.map(name => <li key={name}>{name}</li>)}</ul>}
      <div className="message-history" ref={history} role="log" aria-label={`Mensagens de ${active.title}`} aria-live="polite" tabIndex={0}>
        {!active.messages.length ? <div className="thread-empty">
          <span className="empty-illustration" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <AgentPortrait name={agentName} />}</span>
          <span className="eyebrow">{mode === 'meeting' ? 'PERSPECTIVAS EM COMUM' : 'UM PRIMEIRO ENCONTRO'}</span>
          <h3>{readOnly ? 'Registro preservado.' : mode === 'meeting' ? 'Uma mesa aberta.' : active.resumed ? 'Vamos retomar a conversa.' : 'O que vamos descobrir?'}</h3>
          <p>{mode === 'meeting' ? 'Apresente uma questão para os agentes desta reunião. Cada perspectiva terá espaço no mesmo histórico.' : readOnly ? 'Você pode consultar este registro e iniciar uma conversa pelo catálogo.' : `Traga uma pergunta, uma ideia ainda solta ou algo que você gostaria de investigar com ${agentName}.`}</p>
          <button disabled={readOnly || sending} className="suggestion" onClick={() => { updateActive(item => ({ ...item, draft: mode === 'meeting' ? 'Que perspectivas podemos reunir para investigar energia em Yavin?' : `${agentName}, por onde podemos começar a investigar energia em Yavin?` })); composer.current?.focus(); }}>Começar por energia<Icon name="arrow" /></button>
        </div> : <><div className="history-divider">{new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long' }).format(new Date(active.createdAt))}</div>{active.messages.map(message => <article key={message.id} className={`message message-${message.kind ?? (message.author === 'Você' ? 'user' : message.author === 'Silas' ? 'agent' : 'system')}`}><header><span>{message.author}</span><time dateTime={message.createdAt}>{time(message.createdAt)}</time></header><p>{message.content}</p></article>)}<p className="pending-note">{mode === 'meeting' ? 'Reunião local. Mensagens salvas neste navegador.' : 'Histórico salvo neste navegador.'}</p></>}
      </div>
      {mode === 'conversation' && <div className="conversation-notice">
        {readOnly ? <><p>{active.unavailableReason ?? 'Este é um registro local anterior. Seu histórico e rascunho foram preservados; para enviar mensagens, inicie uma conversa com um agente.'}</p>
          <button type="button" className="text-button" onClick={startCreating}>Iniciar conversa com um agente</button></>
          : active.resumed && <p>Conversa retomada. O histórico exibido é deste navegador; o agente pode ter contexto de mensagens anteriores.</p>}
      </div>}
      {sendError?.id === active.id && !readOnly && <p className="form-error send-error" role="alert">{sendError.message} Seu rascunho foi preservado.</p>}
      <form className="composer" onSubmit={send}>
        <label className="sr-only" htmlFor="message">{mode === 'meeting' ? 'Mensagem para a reunião' : `Mensagem para ${agentName}`}</label>
        <div className="composer-box"><textarea id="message" ref={composer} rows={3} maxLength={12000} disabled={sending || readOnly} placeholder={mode === 'meeting' ? 'Traga uma questão para a mesa…' : readOnly ? 'Registro disponível para consulta' : `Escreva para ${agentName}…`} value={active.draft} onChange={event => updateActive(item => ({ ...item, draft: event.target.value }))} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} /><div className="composer-actions"><span>Enter para enviar · Shift + Enter para nova linha</span><button className="send-button" type="submit" disabled={sending || readOnly || !active.draft.trim()} aria-label="Enviar mensagem"><Icon name="send" /></button></div></div>
        <p className="connection-note"><span className="tiny-dot" />{mode === 'meeting' ? 'Reunião local · agentes ainda não conectados' : readOnly ? 'Registro local · envio indisponível' : sending ? 'Aguardando resposta…' : `Mensagens para ${agentName} pela API local`}</p>
      </form>
    </> : <div className="no-meeting"><Icon name="group" /><h2>{mode === 'meeting' ? 'Mais vozes, uma investigação.' : 'Uma pergunta pode ser o começo.'}</h2><p>{mode === 'meeting' ? 'Crie uma reunião para organizar uma conversa com Silas e outros agentes.' : 'Escolha um agente disponível para abrir sua bancada de conversa.'}</p><button className="primary-button" onClick={startCreating}><Icon name="plus" />{mode === 'meeting' ? 'Criar primeira reunião' : 'Iniciar conversa'}</button><small>{mode === 'meeting' ? 'Nesta prévia, participantes e mensagens são salvos apenas neste navegador.' : 'A conversa é criada no servidor antes do envio de mensagens.'}</small></div>}
    </div>
    <span className="sr-only" role="status">{announcement}</span>
  </aside>;
}
