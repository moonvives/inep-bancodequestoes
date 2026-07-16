"use client";

import { useEffect, useMemo, useState } from "react";

type Skill = { area: string; area_nome: string; competencia: number; competencia_descricao: string; habilidade: number; codigo: string; descricao: string };

const areas = [
  ["LC", "Linguagens"], ["MT", "Matemática"], ["CN", "Natureza"], ["CH", "Humanas"],
];

export default function Matriz() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [area, setArea] = useState("CN");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState<number | null>(1);

  useEffect(() => { fetch("/api/matriz-enem.json").then(r => r.json()).then(d => setSkills(d.habilidades)); }, []);
  const selected = useMemo(() => skills.filter(s => s.area === area && (!query || `${s.codigo} ${s.descricao} ${s.competencia_descricao}`.toLocaleLowerCase("pt-BR").includes(query.toLocaleLowerCase("pt-BR")))), [skills, area, query]);
  const groups = [...new Set(selected.map(s => s.competencia))];
  const areaName = skills.find(s => s.area === area)?.area_nome;

  return (
    <main className="shell page-shell matrix-page">
      <section className="page-intro matrix-intro">
        <div><p className="eyebrow">Matriz de Referência do ENEM</p><h1>120 habilidades, sem perder a arquitetura da prova.</h1><p>Leia a formulação oficial dentro de sua competência e compare como cada área transforma conhecimento em ação cognitiva.</p></div>
        <div className="matrix-total"><strong>{selected.length || 30}</strong><span>habilidades<br/>na área</span></div>
      </section>

      <div className="area-tabs" role="tablist" aria-label="Áreas do conhecimento">
        {areas.map(([code,label]) => <button key={code} className={area === code ? "active" : ""} onClick={() => { setArea(code); setOpen(1); }}><strong>{code}</strong><span>{label}</span></button>)}
      </div>

      <div className="matrix-toolbar"><div><small>Área selecionada</small><strong>{areaName || "Carregando…"}</strong></div><label><span>Pesquisar na matriz</span><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Ex.: tecnologia, saúde, argumentação" /></label></div>

      <section className="competency-list">
        {groups.map(comp => {
          const rows = selected.filter(s => s.competencia === comp);
          const active = open === comp;
          return (
            <article className={`competency ${active ? "open" : ""}`} key={comp}>
              <button className="competency-head" onClick={() => setOpen(active ? null : comp)} aria-expanded={active}>
                <span className="competency-number">C{String(comp).padStart(2,"0")}</span>
                <span className="competency-title"><small>Competência de área {comp}</small><strong>{rows[0]?.competencia_descricao}</strong></span>
                <span className="competency-count">{rows.length} habilidades</span>
                <span className="toggle">{active ? "−" : "+"}</span>
              </button>
              {active && <div className="skill-list">{rows.map(row => <div className="skill-row" key={row.codigo}><strong>{row.codigo}</strong><p>{row.descricao}</p><span>Competência {row.competencia}</span></div>)}</div>}
            </article>
          );
        })}
        {!groups.length && skills.length > 0 && <div className="empty-state"><strong>Nenhuma habilidade corresponde à busca.</strong></div>}
      </section>
    </main>
  );
}
