"use client";

import { useEffect, useMemo, useState } from "react";

type Question = {
  numero: number; codigo: string; habilidade: number; competencia: number; area: string;
  edicao: string; ano: number; aplicacao: string; b: number | null; b_texto: string;
  enunciado: string; tier: { nivel: number; rotulo: string } | null;
};

export default function Banco() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [query, setQuery] = useState("");
  const [area, setArea] = useState("");
  const [skill, setSkill] = useState("");
  const [year, setYear] = useState("");
  const [tier, setTier] = useState("");
  const [visible, setVisible] = useState(40);

  useEffect(() => { fetch("/legacy/api/questions.json").then(r => r.json()).then(setQuestions); }, []);

  const filtered = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("pt-BR");
    return questions.filter(q => {
      if (needle && !`${q.codigo} ${q.enunciado} ${q.aplicacao}`.toLocaleLowerCase("pt-BR").includes(needle)) return false;
      if (area && q.area !== area) return false;
      if (skill && q.habilidade !== Number(skill)) return false;
      if (year && q.ano !== Number(year)) return false;
      if (tier && q.tier?.nivel !== Number(tier)) return false;
      return true;
    });
  }, [questions, query, area, skill, year, tier]);

  const clear = () => { setQuery(""); setArea(""); setSkill(""); setYear(""); setTier(""); setVisible(40); };
  const years = [...new Set(questions.map(q => q.ano))].sort((a,b) => b-a);

  return (
    <main className="shell page-shell">
      <section className="page-intro">
        <p className="eyebrow">Acervo pesquisável</p>
        <h1>Banco de questões</h1>
        <p>Localize itens por texto, habilidade, disciplina, ano e faixa de dificuldade. Os filtros trabalham em conjunto.</p>
      </section>

      <section className="filter-panel">
        <div className="search-field">
          <label htmlFor="question-search">Busca livre</label>
          <input id="question-search" value={query} onChange={e => { setQuery(e.target.value); setVisible(40); }} placeholder="Busque por tema, expressão, código ou aplicação" />
        </div>
        <div className="filter-grid">
          <label>Área<select value={area} onChange={e => setArea(e.target.value)}><option value="">Todas</option>{["Biologia","Física","Química","Interdisciplinar"].map(v => <option key={v}>{v}</option>)}</select></label>
          <label>Habilidade<select value={skill} onChange={e => setSkill(e.target.value)}><option value="">H1–H30</option>{Array.from({length:30},(_,i)=>i+1).map(v => <option value={v} key={v}>H{v}</option>)}</select></label>
          <label>Ano<select value={year} onChange={e => setYear(e.target.value)}><option value="">Todos</option>{years.map(v => <option key={v}>{v}</option>)}</select></label>
          <label>Dificuldade<select value={tier} onChange={e => setTier(e.target.value)}><option value="">Todas</option><option value="1">1 · Muito fácil</option><option value="2">2 · Fácil</option><option value="3">3 · Mediana</option><option value="4">4 · Difícil</option><option value="5">5 · Muito difícil</option></select></label>
        </div>
        <div className="filter-foot"><span><strong>{filtered.length}</strong> de {questions.length || "…"} questões</span><button onClick={clear}>Limpar filtros</button></div>
      </section>

      <section className="results-list" aria-live="polite">
        {filtered.slice(0, visible).map(q => (
          <a className="question-row" href={`/legacy/questao.html?q=${q.numero}`} key={q.numero}>
            <div className="question-code"><small>ITEM</small><strong>{q.codigo}</strong></div>
            <div className="question-main">
              <div className="question-tags"><span className={`subject ${q.area.toLowerCase()}`}>{q.area}</span><span>H{q.habilidade}</span><span>C{q.competencia}</span><span>{q.aplicacao}</span></div>
              <p>{q.enunciado || "Enunciado não disponível nesta extração."}</p>
            </div>
            <div className="question-tri"><small>TRI · b</small><strong>{q.b_texto || "—"}</strong><span className={`tier tier-${q.tier?.nivel || 0}`}>{q.tier?.rotulo || "Sem parâmetro"}</span></div>
          </a>
        ))}
        {!filtered.length && questions.length > 0 && <div className="empty-state"><strong>Nenhum item encontrado.</strong><p>Experimente retirar um filtro ou usar outro termo de busca.</p></div>}
      </section>
      {visible < filtered.length && <button className="load-more" onClick={() => setVisible(v => v + 40)}>Carregar mais 40 questões</button>}
    </main>
  );
}
