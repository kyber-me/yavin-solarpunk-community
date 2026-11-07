import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createConversation, listAgents, type AgentOption, type ConversationMetadata } from '../chatApi';
import type { Mode } from '../conversations';

type Props = {
  mode: Mode;
  preferSilas: boolean;
  onCreate: (title: string, participants: string[], remote?: { agent: AgentOption; metadata: ConversationMetadata; resumed: boolean }) => void;
  onCancel: () => void;
};

export function CreateConversationForm({ mode, preferSilas, onCreate, onCancel }: Props) {
  const [title, setTitle] = useState('');
  const [names, setNames] = useState('');
  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [participantId, setParticipantId] = useState('');
  const [loading, setLoading] = useState(mode === 'conversation');
  const [catalogError, setCatalogError] = useState('');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [pending, setPending] = useState(false);
  const [existing, setExisting] = useState<{ agent: AgentOption; metadata: ConversationMetadata } | null>(null);
  const inFlight = useRef(false);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  useEffect(() => {
    if (mode !== 'conversation') return;
    const controller = new AbortController();
    setLoading(true);
    setCatalogError('');
    setAgents([]);
    setParticipantId('');
    void listAgents(AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]))
      .then(items => {
        if (controller.signal.aborted) return;
        setAgents(items);
        const preferred = preferSilas ? items.find(item => item.name.toLocaleLowerCase() === 'silas') : undefined;
        setParticipantId(preferred?.id ?? '');
      })
      .catch(reason => {
        if (!controller.signal.aborted) setCatalogError(reason instanceof Error ? reason.message : 'Não foi possível carregar os agentes.');
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [mode, attempt, preferSilas]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (inFlight.current) return;
    setError('');
    if (mode === 'meeting') {
      const participants = ['Silas', ...names.split(',').map(name => name.trim()).filter(Boolean)]
        .filter((name, index, values) => values.findIndex(item => item.toLocaleLowerCase() === name.toLocaleLowerCase()) === index);
      if (participants.length < 2) { setError('Inclua pelo menos mais um agente além de Silas.'); return; }
      onCreate(title.trim() || 'Nova reunião', participants);
      return;
    }
    const agent = agents.find(item => item.id === participantId);
    if (!agent || existing) return;
    inFlight.current = true;
    setPending(true);
    try {
      const result = await createConversation(agent.id);
      if (!mounted.current) return;
      if (result.existing) setExisting({ agent, metadata: result.conversation });
      else onCreate(title.trim() || `Conversa com ${agent.name}`, [agent.name], {
        agent, metadata: result.conversation, resumed: false,
      });
    } catch (reason) {
      if (mounted.current) setError(reason instanceof Error ? reason.message : 'Não foi possível iniciar a conversa.');
    } finally {
      inFlight.current = false;
      if (mounted.current) setPending(false);
    }
  }

  return <form className="create-form" onSubmit={submit} aria-busy={loading || pending}>
    <label htmlFor="conversation-title">{mode === 'meeting' ? 'Nome da reunião' : 'Nome da conversa (opcional)'}</label>
    <input id="conversation-title" autoFocus maxLength={80} disabled={pending} value={title} onChange={event => setTitle(event.target.value)} placeholder={mode === 'meeting' ? 'O que vamos investigar?' : 'Sobre o que vamos conversar?'} />
    {mode === 'meeting' ? <>
      <label htmlFor="participant-names">Outros agentes</label>
      <input id="participant-names" value={names} maxLength={240} onChange={event => { setNames(event.target.value); setError(''); }} placeholder="Nomes separados por vírgula" aria-describedby="participants-help" aria-invalid={!!error} />
      <small id="participants-help">Silas já está incluído. Participantes e mensagens desta reunião são apenas locais.</small>
    </> : <>
      <label htmlFor="conversation-agent">Com quem vamos conversar?</label>
      <select id="conversation-agent" required value={participantId} disabled={loading || pending || !agents.length || !!existing}
        onChange={event => { setParticipantId(event.target.value); setError(''); }}>
        <option value="">{loading ? 'Carregando agentes…' : 'Selecione um agente'}</option>
        {agents.map(agent => <option key={agent.id} value={agent.id}>{agent.name}</option>)}
      </select>
      {loading && <small role="status">Buscando os agentes disponíveis…</small>}
      {!loading && !catalogError && !agents.length && <small role="status">Nenhum agente está disponível para conversar agora.</small>}
      {catalogError && <p className="form-error" role="alert">{catalogError}</p>}
      {!loading && (catalogError || !agents.length) && <button type="button" className="text-button" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button>}
      {existing && <div className="existing-conversation" role="status">
        <p>Já existe uma conversa ativa com {existing.agent.name}.</p>
        <button type="button" className="primary-button" onClick={() => onCreate(title.trim() || `Conversa com ${existing.agent.name}`,
          [existing.agent.name], { ...existing, resumed: true })}>Abrir conversa existente</button>
      </div>}
    </>}
    {error && <p role="alert" className="form-error">{error}</p>}
    <div className="form-actions">
      <button type="button" className="text-button" disabled={pending} onClick={onCancel}>Cancelar</button>
      {!existing && <button className="primary-button" type="submit" disabled={mode === 'conversation' && (pending || loading || !participantId)}>
        {pending ? 'Iniciando…' : mode === 'meeting' ? 'Criar reunião' : 'Iniciar conversa'}
      </button>}
    </div>
  </form>;
}
