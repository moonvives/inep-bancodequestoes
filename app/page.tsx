const difficulty = [
  { label: "Muito fácil", value: 116, color: "#8e7180" },
  { label: "Fácil", value: 161, color: "#aa7b84" },
  { label: "Mediana", value: 155, color: "#b98a6a" },
  { label: "Difícil", value: 78, color: "#9b5961" },
  { label: "Muito difícil", value: 26, color: "#713746" },
];

const routes = [
  { n: "01", title: "Explorar o banco", text: "Busca combinada por área, habilidade, aplicação, ano e dificuldade TRI.", href: "/banco", meta: "540 itens" },
  { n: "02", title: "Ler a matriz", text: "As 120 habilidades oficiais organizadas por área e competência.", href: "/matriz", meta: "4 áreas" },
  { n: "03", title: "Resolver questões", text: "Sessões por sequência, fraquezas, revisão de erros ou sorteio aleatório.", href: "/legacy/estudar.html", meta: "Estudo ativo" },
  { n: "04", title: "Analisar microdados", text: "Parâmetros oficiais de discriminação, dificuldade e acerto ao acaso.", href: "/legacy/painel-oficial.html", meta: "TRI a · b · c" },
];

export default function Home() {
  return (
    <main>
      <section className="hero shell">
        <div className="hero-copy">
          <p className="eyebrow">Banco de questões · Matriz de Referência · TRI</p>
          <h1>O ENEM deixa de ser um arquivo de provas e passa a ser um <em>mapa de decisões.</em></h1>
          <p className="hero-lede">Questões, habilidades e microdados reunidos em uma leitura única: precisa para investigar a prova, clara para organizar o estudo.</p>
          <div className="hero-actions">
            <a className="button primary" href="/banco">Explorar as questões</a>
            <a className="button secondary" href="/matriz">Abrir a matriz completa</a>
          </div>
          <div className="hero-note"><span>Base preservada</span> PPL, 2ª Aplicação, Libras e Digital · 2012–2024</div>
        </div>

        <div className="hero-data" aria-label="Resumo analítico">
          <div className="data-head">
            <span>Leitura da base</span>
            <span className="live-dot">Dados carregados</span>
          </div>
          <div className="big-number"><strong>540</strong><span>questões<br/>catalogadas</span></div>
          <div className="metric-row">
            <div><small>Dificuldade média</small><strong>615,0</strong><span>parâmetro b</span></div>
            <div><small>Itens calibrados</small><strong>536</strong><span>99,3% da base</span></div>
          </div>
          <div className="distribution">
            <div className="distribution-title"><span>Distribuição de dificuldade</span><small>536 itens válidos</small></div>
            <div className="stacked-bar">
              {difficulty.map(d => <span key={d.label} style={{ width: `${(d.value / 536) * 100}%`, background: d.color }} title={`${d.label}: ${d.value}`} />)}
            </div>
            <div className="legend">
              {difficulty.map(d => <span key={d.label} style={{ borderColor: d.color }}>{d.label}<b>{d.value}</b></span>)}
            </div>
          </div>
        </div>
      </section>

      <section className="signal-strip">
        <span>4 áreas do conhecimento</span>
        <span>30 habilidades por área</span>
        <span>8 competências em Natureza</span>
        <span>18 anos de microdados</span>
      </section>

      <section className="shell section-block">
        <div className="section-heading">
          <div><p className="eyebrow">Navegação por intenção</p><h2>Entre pela pergunta que você quer responder.</h2></div>
          <p>O mesmo acervo pode servir à investigação estatística, à revisão por habilidade ou à prática deliberada.</p>
        </div>
        <div className="route-grid">
          {routes.map(route => (
            <a className="route-card" href={route.href} key={route.n}>
              <div className="route-top"><span>{route.n}</span><small>{route.meta}</small></div>
              <h3>{route.title}</h3>
              <p>{route.text}</p>
              <b>Acessar</b>
            </a>
          ))}
        </div>
      </section>

      <section className="shell editorial-grid">
        <article className="matrix-callout">
          <div>
            <p className="eyebrow light">Matriz oficial do ENEM</p>
            <h2>Da habilidade abstrata ao padrão que realmente aparece na prova.</h2>
            <p>A nova leitura reúne Linguagens, Matemática, Ciências da Natureza e Ciências Humanas. Cada habilidade permanece ligada à sua competência e ao texto oficial.</p>
            <a href="/matriz">Consultar as 120 habilidades</a>
          </div>
          <div className="matrix-numbers">
            <span><strong>LC</strong><small>9 competências</small></span>
            <span><strong>MT</strong><small>7 competências</small></span>
            <span><strong>CN</strong><small>8 competências</small></span>
            <span><strong>CH</strong><small>6 competências</small></span>
          </div>
        </article>

        <aside className="method-card">
          <p className="eyebrow">Método</p>
          <h3>Dados que podem ser auditados.</h3>
          <ul>
            <li><span>01</span>Gabaritos e parâmetros vindos dos microdados oficiais.</li>
            <li><span>02</span>Dificuldade apresentada na escala de proficiência do ENEM.</li>
            <li><span>03</span>Histórico pessoal mantido apenas no dispositivo.</li>
          </ul>
          <a href="/legacy/sobre.html">Ver fontes e critérios</a>
        </aside>
      </section>
    </main>
  );
}
