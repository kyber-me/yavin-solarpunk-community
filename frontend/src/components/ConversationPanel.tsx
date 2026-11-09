import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { discardLocalHistory, type Conversation, type Mode } from '../conversations';

import silasAvatar from '../assets/silas-avatar.png';
import { CreateConversationForm } from './CreateConversationForm';
import { ChatApiError, sendMessage, listConversations, listMessages, updateConversationTitle, SENDER_ID, type PersistedMessage, type AgentOption, type ConversationMetadata } from '../chatApi';

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
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [warning, setWarning] = useState('');
  const [listLoading, setListLoading] = useState(true);
  const [listAttempt, setListAttempt] = useState(0);
  const [historyAttempt, setHistoryAttempt] = useState(0);
  const [historyLoadingId, setHistoryLoadingId] = useState('');
  const [historyError, setHistoryError] = useState<{ id: string; message: string } | null>(null);
  const [mode, setMode] = useState<Mode>('conversation');
  const [activeId, setActiveId] = useState('');
  const [creating, setCreating] = useState(false);
  const [editingTitleId, setEditingTitleId] = useState('');
  const [titleDraft, setTitleDraft] = useState('');
  const [titlePending, setTitlePending] = useState(false);
  const [titleError, setTitleError] = useState('');
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
  const readOnly = !!active && (!!active.unavailableReason || historyLoadingId === active.id || historyError?.id === active.id);
  function focusComposer() { if (composer.current?.getClientRects().length) composer.current.focus(); }
  function startCreating() { if (mode !== 'conversation' || listLoading) return; setPreferSilas(false); setCreating(true); }
  const viewMessages = (records: PersistedMessage[], name: string) => records.map(record => ({
    id: record.id, author: record.sender_id === SENDER_ID ? 'Você' : name,
    kind: record.sender_id === SENDER_ID ? 'user' as const : 'agent' as const,
    content: record.content, createdAt: record.created_at,
  }));

  useEffect(() => {
    discardLocalHistory();
    const controller = new AbortController();
    setListLoading(true);
    setWarning('');
    void listConversations(controller.signal).then(records => {
      if (controller.signal.aborted) return;
      setConversations(previous => records.map(record => ({
        id: record.conversation_id, serverConversationId: record.conversation_id,
        participantId: record.participant_id, mode: 'conversation',
        title: record.title, participants: [record.participant_name],
        messages: [], draft: previous.find(item => item.id === record.conversation_id)?.draft ?? '',
        createdAt: record.created_at, unavailableReason: record.active ? undefined : 'Esta conversa está encerrada.',
      })));
      setActiveId(current => records.some(item => item.conversation_id === current) ? current : records[0]?.conversation_id ?? '');
      setHistoryAttempt(value => value + 1);
    }).catch(error => {
      if (!controller.signal.aborted) {
        setConversations([]);
        setActiveId('');
        setWarning(error instanceof Error ? error.message : 'Não foi possível carregar as conversas do servidor.');
      }
    }).finally(() => { if (!controller.signal.aborted) setListLoading(false); });
    return () => controller.abort();
  }, [listAttempt]);

  useEffect(() => {
    if (!activeId) return;
    const controller = new AbortController();
    setHistoryLoadingId(activeId);
    setHistoryError(null);
    void listMessages(activeId, controller.signal).then(records => {
      if (!controller.signal.aborted) setConversations(items => items.map(item => item.id === activeId
        ? { ...item, messages: viewMessages(records, item.participants[0] ?? 'Agente') } : item));
    }).catch(error => {
      if (controller.signal.aborted) return;
      if (error instanceof ChatApiError && (error.status === 404 || error.status === 403)) {
        setConversations(items => items.filter(item => item.id !== activeId));
        setActiveId(current => current === activeId ? '' : current);
      }
      setHistoryError({ id: activeId, message: error instanceof Error ? error.message : 'Não foi possível carregar o histórico.' });
    }).finally(() => { if (!controller.signal.aborted) setHistoryLoadingId(''); });
    return () => controller.abort();
  }, [activeId, historyAttempt]);

  useEffect(() => { history.current?.scrollTo({ top: history.current.scrollHeight }); }, [activeId, active?.messages.length]);
  useEffect(() => {
    if (listLoading || handledSilasRequest.current === silasChatRequest) return;
    handledSilasRequest.current = silasChatRequest;
    setMode('conversation');
    const selected = conversations.find(item => !item.unavailableReason && item.participants.some(name => name.toLocaleLowerCase() === 'silas'));
    if (selected) { setCreating(false); setActiveId(selected.id); }
    else { setPreferSilas(true); setCreating(true); }
  }, [silasChatRequest, conversations, listLoading]);

  function switchMode(next: Mode) {
    setMode(next); setCreating(false); setPreferSilas(false);
    setActiveId(conversations.find(item => item.mode === next)?.id ?? '');
  }
  function updateActive(update: (item: Conversation) => Conversation) {
    setConversations(items => items.map(item => item.id === activeId ? update(item) : item));
  }
  function create(_title: string, _participants: string[], remote?: { agent: AgentOption; metadata: ConversationMetadata; resumed: boolean }) {
    if (!remote) return;
    const { agent, metadata } = remote;
    setConversations(items => items.some(item => item.id === metadata.conversation_id) ? items : [{
      id: metadata.conversation_id, serverConversationId: metadata.conversation_id, participantId: agent.id,
      mode: 'conversation', title: metadata.title, participants: [agent.name],
      messages: [], draft: '', createdAt: metadata.created_at,
    }, ...items]);
    setActiveId(metadata.conversation_id); setHistoryAttempt(value => value + 1);
    setCreating(false); setSendError(null); requestAnimationFrame(focusComposer);
  }
  async function saveTitle(event: FormEvent) {
    event.preventDefault();
    if (!active || titlePending || !titleDraft.trim()) return;
    const conversationId = active.id;
    setTitlePending(true); setTitleError('');
    try {
      const title = await updateConversationTitle(conversationId, titleDraft.trim());
      setConversations(items => items.map(item => item.id === conversationId ? { ...item, title } : item));
      setEditingTitleId('');
    } catch (error) {
      setTitleError(error instanceof Error ? error.message : 'Não foi possível alterar o título.');
    } finally {
      setTitlePending(false);
    }
  }
  async function send(event: FormEvent) {
    event.preventDefault();
    if (sendingLock.current || readOnly || !active?.draft.trim() || !active.serverConversationId) return;
    const target = active;
    const content = target.draft.trim();
    const updateTarget = (update: (item: Conversation) => Conversation) =>
      setConversations(items => items.map(item => item.id === target.id ? update(item) : item));
    const knownIds = new Set(target.messages.map(message => message.id));
    sendingLock.current = true; setSending(true); setSendError(null);
    setAnnouncement('Enviando mensagem. Aguardando resposta.');
    let acknowledged = false;
    try {
      await sendMessage(target.serverConversationId!, content);
      acknowledged = true;
      setAnnouncement('Resposta recebida.');
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Não foi possível enviar a mensagem.';
      setSendError({ id: target.id, message: reason }); setAnnouncement(reason);
      if (error instanceof ChatApiError && (error.status === 404 || error.status === 409 || error.status === 403)) {
        updateTarget(item => ({ ...item, unavailableReason: reason }));
      }
    } finally {
      try {
        const records = await listMessages(target.serverConversationId!);
        const saved = records.some(record => !knownIds.has(record.id) && record.sender_id === SENDER_ID && record.content === content);
        updateTarget(item => ({ ...item, messages: viewMessages(records, item.participants[0] ?? 'Agente'),
          draft: (acknowledged || saved) && item.draft === target.draft ? '' : item.draft }));
      } catch (error) {
        if (error instanceof ChatApiError && (error.status === 404 || error.status === 403)) {
          setConversations(items => items.filter(item => item.id !== target.id));
          setActiveId(current => current === target.id ? '' : current);
        }
        setHistoryError({ id: target.id, message: 'Não foi possível atualizar o histórico. Confira as mensagens antes de reenviar.' });
      }
      sendingLock.current = false; setSending(false);
      if (activeIdRef.current === target.id) focusComposer();
    }
  }

  return <aside className={`conversation-panel${drawer ? ' drawer-panel' : ''}${creating ? ' is-creating' : ''}`} aria-labelledby="panel-title">
    <header className="panel-header">
      <div className="panel-eyebrow"><span className="tiny-dot" />{drawer ? 'TERRITÓRIO / CONVERSAS' : 'LABORATÓRIO / CONVERSAS'}<span>{mode === 'meeting' ? 'REUNIÕES · EM BREVE' : 'CONVERSAS'}</span></div>
      <div className="panel-heading"><h1 id="panel-title" tabIndex={-1}>Vamos pensar juntos.</h1><div className="panel-tools">{active && mode === 'conversation' && <AgentPortrait name={agentName} className="silas-mark" />}{onCollapse && <button className="drawer-close" type="button" onClick={onCollapse} aria-label="Fechar chat" title="Recolher chat (Esc)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg></button>}</div></div>
      <p>Perguntas, hipóteses e próximos passos.</p>
    </header>

    <div className="panel-directory">
    <nav className="mode-switch" aria-label="Tipo de conversa">
      <button aria-pressed={mode === 'conversation'} onClick={() => switchMode('conversation')}><Icon name="chat" />Conversas<span>{conversations.filter(item => item.mode === 'conversation').length}</span></button>
      <button aria-pressed={mode === 'meeting'} onClick={() => switchMode('meeting')}><Icon name="group" />Reuniões<span>{conversations.filter(item => item.mode === 'meeting').length}</span></button>
    </nav>

    <section className="conversation-directory" aria-label={mode === 'meeting' ? 'Suas reuniões' : 'Suas conversas'}>
      <div className="directory-heading"><span>{mode === 'meeting' ? 'MESA DE AGENTES' : 'COM AGENTES'}</span><button className="new-button" disabled={mode === 'meeting' || listLoading} onClick={() => { setPreferSilas(false); setCreating(value => !value); }} aria-expanded={creating}><Icon name="plus" />{mode === 'meeting' ? 'Em breve' : 'Iniciar conversa'}</button></div>
      {creating ? <CreateConversationForm key={`${mode}:${silasChatRequest}`} preferSilas={preferSilas} onCreate={create} onCancel={() => setCreating(false)} /> : <div className="conversation-list">
        {filtered.map(item => <button key={item.id} className={`conversation-item ${item.id === activeId ? 'selected' : ''}`} aria-current={item.id === activeId ? 'true' : undefined} onClick={() => { setActiveId(item.id); setEditingTitleId(''); setAnnouncement(''); }}>
          <Icon name={mode === 'meeting' ? 'group' : 'chat'} /><span><strong>{item.title}</strong><small>{item.messages.at(-1)?.content ?? (mode === 'meeting' ? `${item.participants.length} agentes · ainda sem mensagens` : 'Uma pergunta pode ser o começo.')}</small></span><Icon name="arrow" />
        </button>)}
        {listLoading && mode === 'conversation' && <p role="status">Carregando conversas do servidor…</p>}
        {!listLoading && !filtered.length && <p className="directory-empty">{mode === 'meeting' ? 'Reúna diferentes perspectivas em uma mesma conversa.' : 'Escolha um agente e inicie uma conversa.'}</p>}
      </div>}
    </section>

    {warning && <div className="storage-warning" role="alert"><p>{warning}</p><button className="text-button" onClick={() => setListAttempt(value => value + 1)}>Tentar novamente</button></div>}
    </div>
    <div className="thread-workspace" aria-busy={sending}>
    {active ? <>
      <div className="thread-heading"><span className="thread-avatar" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <AgentPortrait name={agentName} />}</span><div><h2>{active.title}</h2><p>{mode === 'meeting' ? `${active.participants.length} agentes nesta mesa` : `${agentName} · colaborador de Yavin`}</p></div>{mode === 'conversation' && <button type="button" className="text-button rename-button" onClick={() => { setEditingTitleId(active.id); setTitleDraft(active.title); setTitleError(''); }}>Renomear</button>}</div>
      {mode === 'conversation' && editingTitleId === active.id && <form className="rename-form" onSubmit={saveTitle}>
        <label htmlFor="rename-title">Título da conversa</label>
        <input id="rename-title" value={titleDraft} onChange={event => setTitleDraft(event.target.value)} required maxLength={120} disabled={titlePending} />
        <button type="submit" className="primary-button" disabled={titlePending || !titleDraft.trim()}>Salvar</button>
        <button type="button" className="text-button" disabled={titlePending} onClick={() => { setEditingTitleId(''); setTitleError(''); }}>Cancelar</button>
        {titleError && <p className="form-error" role="alert">{titleError}</p>}
      </form>}
      {mode === 'meeting' && <ul className="participant-list" aria-label="Agentes participantes">{active.participants.map(name => <li key={name}>{name}</li>)}</ul>}
      <div className="message-history" ref={history} role="log" aria-label={`Mensagens de ${active.title}`} aria-live="polite" tabIndex={0}>
        {historyLoadingId === active.id ? <p role="status">Carregando mensagens do servidor…</p> : historyError?.id === active.id ? <div role="alert"><p>{historyError.message}</p><button className="text-button" onClick={() => setHistoryAttempt(value => value + 1)}>Tentar novamente</button></div> : !active.messages.length ? <div className="thread-empty">
          <span className="empty-illustration" aria-hidden="true">{mode === 'meeting' ? <Icon name="group" /> : <AgentPortrait name={agentName} />}</span>
          <span className="eyebrow">{mode === 'meeting' ? 'PERSPECTIVAS EM COMUM' : 'UM PRIMEIRO ENCONTRO'}</span>
          <h3>{readOnly ? 'Registro preservado.' : mode === 'meeting' ? 'Uma mesa aberta.' : 'O que vamos descobrir?'}</h3>
          <p>{mode === 'meeting' ? 'Apresente uma questão para os agentes desta reunião. Cada perspectiva terá espaço no mesmo histórico.' : readOnly ? 'Você pode consultar este registro e iniciar uma conversa pelo catálogo.' : `Traga uma pergunta, uma ideia ainda solta ou algo que você gostaria de investigar com ${agentName}.`}</p>
          <button disabled={readOnly || sending} className="suggestion" onClick={() => { updateActive(item => ({ ...item, draft: mode === 'meeting' ? 'Que perspectivas podemos reunir para investigar energia em Yavin?' : `${agentName}, por onde podemos começar a investigar energia em Yavin?` })); composer.current?.focus(); }}>Começar por energia<Icon name="arrow" /></button>
        </div> : <><div className="history-divider">{new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long' }).format(new Date(active.createdAt))}</div>{active.messages.map(message => <article key={message.id} className={`message message-${message.kind ?? (message.author === 'Você' ? 'user' : message.author === 'Silas' ? 'agent' : 'system')}`}><header><span>{message.author}</span><time dateTime={message.createdAt}>{time(message.createdAt)}</time></header><p>{message.content}</p></article>)}<p className="pending-note">{mode === 'meeting' ? 'Reuniões ainda indisponíveis.' : 'Histórico recuperado do servidor.'}</p></>}
      </div>
      {mode === 'conversation' && <div className="conversation-notice">
        {readOnly ? <><p>{active.unavailableReason ?? 'Histórico indisponível para envio no momento.'}</p>
          <button type="button" className="text-button" onClick={startCreating}>Iniciar conversa com um agente</button></>
          : null}
      </div>}
      {sendError?.id === active.id && !readOnly && <p className="form-error send-error" role="alert">{sendError.message} Confira o histórico antes de reenviar.</p>}
      <form className="composer" onSubmit={send}>
        <label className="sr-only" htmlFor="message">{mode === 'meeting' ? 'Mensagem para a reunião' : `Mensagem para ${agentName}`}</label>
        <div className="composer-box"><textarea id="message" ref={composer} rows={3} maxLength={12000} disabled={sending || readOnly} placeholder={mode === 'meeting' ? 'Traga uma questão para a mesa…' : readOnly ? 'Registro disponível para consulta' : `Escreva para ${agentName}…`} value={active.draft} onChange={event => updateActive(item => ({ ...item, draft: event.target.value }))} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} /><div className="composer-actions"><span>Enter para enviar · Shift + Enter para nova linha</span><button className="send-button" type="submit" disabled={sending || readOnly || !active.draft.trim()} aria-label="Enviar mensagem"><Icon name="send" /></button></div></div>
        <p className="connection-note"><span className="tiny-dot" />{mode === 'meeting' ? 'Reunião local · agentes ainda não conectados' : readOnly ? 'Envio indisponível' : sending ? 'Aguardando resposta…' : `Mensagens para ${agentName} pela API local`}</p>
      </form>
    </> : <div className="no-meeting"><Icon name="group" /><h2>{mode === 'meeting' ? 'Mais vozes, uma investigação.' : 'Uma pergunta pode ser o começo.'}</h2><p>{mode === 'meeting' ? 'As reuniões estarão disponíveis após a implementação da persistência.' : 'Escolha um agente disponível para abrir sua bancada de conversa.'}</p><button className="primary-button" disabled={mode === 'meeting' || listLoading} onClick={startCreating}><Icon name="plus" />{mode === 'meeting' ? 'Reuniões em breve' : 'Iniciar conversa'}</button><small>{mode === 'meeting' ? 'Reuniões ficarão disponíveis quando houver persistência no servidor.' : 'A conversa é criada no servidor antes do envio de mensagens.'}</small></div>}
    </div>
    <span className="sr-only" role="status">{announcement}</span>
  </aside>;
}
