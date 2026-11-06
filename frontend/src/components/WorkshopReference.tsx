import workshopImage from '../assets/oficina-solar.jpg';

export function WorkshopReference({ compact = false }: { compact?: boolean }) {
  return <figure className={`workshop-reference${compact ? ' compact' : ''}`}>
    <img src={workshopImage} alt="Referência visual: três pessoas numa oficina em uma laje, entre ferramentas, painéis solares e plantas." width={805} height={1000} />
    <figcaption><span>IMAGINAR É UM COMEÇO.</span><span>Referência visual · oficina solar urbana</span></figcaption>
  </figure>;
}
