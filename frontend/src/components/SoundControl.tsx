import type { ArrivalSound } from '../arrivalSound';

export function SoundControl({ sound }: { sound: ArrivalSound }) {
  return <button className="arrival-sound" type="button" onClick={sound.toggle} aria-pressed={sound.enabled} aria-label={sound.enabled ? 'Desativar som ambiente' : 'Ativar som ambiente'} title={sound.enabled && !sound.playing ? 'O som começa ao interagir' : undefined}>
    <span className={`sound-bars${sound.playing ? ' is-playing' : ''}`} aria-hidden="true"><i /><i /><i /><i /></span>
    <span>{!sound.enabled ? 'Som desligado' : sound.playing ? 'Som ligado' : 'Som ao interagir'}</span>
  </button>;
}
