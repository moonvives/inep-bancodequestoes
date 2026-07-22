#!/usr/bin/env python3
"""Gera o PDF do Resumo Completo de Física para o ENEM a partir de dados.json.

Uso:
    pip install weasyprint
    python3 scripts/resumo-fisica/gerar_pdf.py
"""
import json
import html
import re
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAIZ = BASE.parent.parent
SAIDA = RAIZ / "public" / "materiais" / "resumo-fisica-enem.pdf"


# ---------------------------------------------------------------- LaTeX → HTML

SIMBOLOS = [
    (r"\\Delta", "Δ"), (r"\\delta", "δ"), (r"\\mu", "μ"), (r"\\rho", "ρ"),
    (r"\\tau", "τ"), (r"\\theta", "θ"), (r"\\pi", "π"),
    (r"\\cdots", "⋯"), (r"\\cdot", "·"), (r"\\times", "×"),
    (r"\\Rightarrow", "⇒"), (r"\\uparrow", "↑"), (r"\\downarrow", "↓"),
    (r"\\tan", "tan"), (r"\\cos", "cos"), (r"\\sin", "sen"),
    (r"\\;", " "), (r"\\,", " "),
]


def _achar_grupo(s: str, i: int):
    """A partir de s[i] == '{', retorna (conteúdo, índice após '}')."""
    nivel = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            nivel += 1
        elif s[j] == "}":
            nivel -= 1
            if nivel == 0:
                return s[i + 1:j], j + 1
    return s[i + 1:], len(s)


def _fracoes(s: str) -> str:
    for cmd in ("\\dfrac", "\\tfrac", "\\frac"):
        while cmd in s:
            i = s.index(cmd)
            num, j = _achar_grupo(s, i + len(cmd))
            den, k = _achar_grupo(s, j)
            frac = (f'<span class="frac"><span class="num">{_fracoes(num)}</span>'
                    f'<span class="den">{_fracoes(den)}</span></span>')
            s = s[:i] + frac + s[k:]
    return s


def latex_para_html(tex: str) -> str:
    s = tex
    # \text{...} e \mathrm{...} viram texto comum
    s = re.sub(r"\\(?:text|mathrm)\{([^{}]*)\}", r"\1", s)
    s = _fracoes(s)
    for padrao, sub in SIMBOLOS:
        s = re.sub(padrao, sub, s)
    # sub/sobrescritos: com chaves e com um caractere
    s = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_(\w)", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^{}]+)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"\^(\w)", r"<sup>\1</sup>", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("=", " = ").replace("+", " + ")
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


# ------------------------------------------------------------------ Documento

def esc(t: str) -> str:
    return html.escape(t, quote=False)


def slug(t: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()
               .translate(str.maketrans("áàâãéêíóôõúüçº", "aaaaeeiooouuco")))
    return s.strip("-")


def construir_html(dados: dict) -> str:
    capitulos: dict[str, list[tuple[str, dict]]] = {}
    for titulo, topico in dados.items():
        if titulo.startswith("_"):
            continue
        capitulos.setdefault(topico["aula"], []).append((titulo, topico))

    # ---- sumário
    itens_toc = []
    for c_i, (aula, topicos) in enumerate(capitulos.items(), 1):
        itens_toc.append(
            f'<div class="toc-cap"><a href="#cap-{slug(aula)}">'
            f'<span class="toc-num">{c_i}</span> {esc(aula)}</a></div>')
        for t_i, (titulo, _) in enumerate(topicos, 1):
            itens_toc.append(
                f'<div class="toc-top"><a href="#top-{slug(titulo)}">'
                f'<span class="toc-idx">{c_i}.{t_i}</span>'
                f'<span class="toc-tit">{esc(titulo)}</span>'
                f'<span class="toc-pg"></span></a></div>')

    # ---- corpo
    corpo = []
    for c_i, (aula, topicos) in enumerate(capitulos.items(), 1):
        corpo.append(f'''
        <section class="capitulo" id="cap-{slug(aula)}">
          <div class="cap-banner">
            <div class="cap-num">Aula {c_i}</div>
            <h1>{esc(aula)}</h1>
            <div class="cap-topicos">{" · ".join(esc(t) for t, _ in topicos)}</div>
          </div>''')
        for t_i, (titulo, top) in enumerate(topicos, 1):
            corpo.append(f'<article class="topico" id="top-{slug(titulo)}">')
            corpo.append(f'<h2><span class="h2-idx">{c_i}.{t_i}</span>{esc(titulo)}</h2>')

            for p in top.get("teoria", []):
                corpo.append(f'<p class="teoria">{esc(p)}</p>')

            if top.get("como_cai"):
                corpo.append(f'''<div class="box comocai">
                  <div class="box-rotulo">Como cai no ENEM</div>
                  <p>{esc(top["como_cai"])}</p></div>''')

            for q_i, q in enumerate(top.get("questoes_resolvidas", []), 1):
                passos = "".join(f"<li>{esc(p)}</li>" for p in q["resolucao"])
                corpo.append(f'''<div class="questao">
                  <div class="q-cab">Questão resolvida {q_i}</div>
                  <p class="q-enunciado">{esc(q["enunciado"])}</p>
                  <div class="q-res-rotulo">Resolução</div>
                  <ol class="q-passos">{passos}</ol></div>''')

            if top.get("pegadinha"):
                corpo.append(f'''<div class="box pegadinha">
                  <div class="box-rotulo">Pegadinha</div>
                  <p>{esc(top["pegadinha"])}</p></div>''')

            if top.get("atalho"):
                corpo.append(f'''<div class="box atalho">
                  <div class="box-rotulo">Atalho</div>
                  <p>{esc(top["atalho"])}</p></div>''')

            if top.get("formulas"):
                chips = "".join(
                    f'''<div class="chip"><div class="chip-rotulo">{esc(f["rotulo"])}</div>
                        <div class="chip-formula">{latex_para_html(f["latex"])}</div></div>'''
                    for f in top["formulas"])
                corpo.append(f'<div class="formulas">{chips}</div>')
            corpo.append("</article>")
        corpo.append("</section>")

    # ---- formulário rápido
    linhas_form = []
    for c_i, (aula, topicos) in enumerate(capitulos.items(), 1):
        formulas = [(t, f) for t, top in topicos for f in top.get("formulas", [])]
        if not formulas:
            continue
        linhas_form.append(f'<h3 class="form-aula">{c_i}. {esc(aula)}</h3>')
        linhas = "".join(
            f'''<tr><td class="f-rotulo">{esc(f["rotulo"])}</td>
                <td class="f-formula">{latex_para_html(f["latex"])}</td>
                <td class="f-topico">{esc(t)}</td></tr>'''
            for t, f in formulas)
        linhas_form.append(f'<table class="form-tabela"><tbody>{linhas}</tbody></table>')

    hoje = date.today().strftime("%d/%m/%Y")
    n_topicos = sum(len(t) for t in capitulos.values())
    n_questoes = sum(len(top.get("questoes_resolvidas", []))
                     for tops in capitulos.values() for _, top in tops)

    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Física para o ENEM — Resumo Completo</title>
<style>
:root {{
  --navy: #1b2a4a;
  --azul: #2f6fed;
  --ambar: #b45309;
  --verde: #047857;
  --cinza: #5b6472; --linha: #d9dee8; --linha-suave: #e8ebf1;
}}
@page {{
  size: A4; margin: 20mm 17mm 18mm 17mm;
  @bottom-center {{
    content: counter(page);
    font-family: "DejaVu Sans"; font-size: 8pt; color: #8a93a3;
  }}
  @top-right {{
    content: string(capitulo);
    font-family: "DejaVu Sans"; font-size: 7.5pt; color: #8a93a3;
    letter-spacing: 0.08em; text-transform: uppercase;
  }}
}}
@page capa {{ margin: 0; @bottom-center {{ content: none }} @top-right {{ content: none }} }}
@page sumario {{ @top-right {{ content: none }} }}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "DejaVu Serif", serif; font-size: 9.2pt;
       line-height: 1.55; color: #262b35; }}
h1, h2, h3, .box-rotulo, .q-cab, .q-res-rotulo, .chip, .toc-cap, .toc-top,
.cap-num, .cap-topicos, .capa, .f-topico {{ font-family: "DejaVu Sans", sans-serif; }}

/* ---------- capa (clara, para impressão) ---------- */
.capa {{ page: capa; width: 210mm; height: 297mm; background: #fff;
        color: var(--navy); padding: 32mm 26mm; display: flex; flex-direction: column; }}
.capa .marca {{ font-size: 9pt; letter-spacing: 0.35em; text-transform: uppercase;
               color: var(--azul); border-bottom: 2px solid var(--navy); padding-bottom: 6mm; }}
.capa h1 {{ margin-top: 40mm; font-size: 34pt; line-height: 1.12; font-weight: bold;
           color: var(--navy); }}
.capa h1 .fina {{ color: var(--cinza); font-weight: normal; }}
.capa .sub {{ margin-top: 8mm; font-size: 11.5pt; color: var(--cinza);
             max-width: 132mm; line-height: 1.55; font-family: "DejaVu Serif", serif; }}
.capa .stats {{ margin-top: 16mm; display: flex; gap: 12mm; }}
.capa .stat {{ border-left: 1.5px solid var(--azul); padding-left: 4mm; }}
.capa .stat b {{ display: block; font-size: 17pt; color: var(--navy); }}
.capa .stat span {{ font-size: 7.8pt; color: var(--cinza); text-transform: uppercase;
                   letter-spacing: 0.12em; }}
.capa .rodape {{ margin-top: auto; font-size: 8.3pt; color: #8a93a3;
                border-top: 1px solid var(--linha); padding-top: 5mm; }}

/* ---------- sumário ---------- */
.sumario {{ page: sumario; page-break-before: always; }}
.sumario h1 {{ font-size: 19pt; color: var(--navy); margin-bottom: 8mm;
              border-bottom: 2.5px solid var(--navy); padding-bottom: 3mm; }}
.toc-cap {{ margin: 5mm 0 1.5mm; }}
.toc-cap a {{ color: var(--navy); font-weight: bold; font-size: 11pt; text-decoration: none; }}
.toc-num {{ display: inline-block; width: 7mm; color: var(--azul); }}
.toc-top a {{ display: flex; align-items: baseline; text-decoration: none;
             color: #3c4454; font-size: 9.3pt; padding: 0.9mm 0 0.9mm 7mm; }}
.toc-idx {{ width: 10mm; color: #8a93a3; font-size: 8.3pt; }}
.toc-pg {{ flex: 1; }}
.toc-top a::after {{ content: leader('.') " " target-counter(attr(href url), page);
                    color: #8a93a3; font-size: 8.3pt; }}

/* ---------- capítulos ---------- */
.capitulo {{ page-break-before: always; }}
.cap-banner {{ border-bottom: 2.5px solid var(--navy); padding-bottom: 5mm;
              margin-bottom: 8mm; }}
.cap-num {{ font-size: 8.5pt; letter-spacing: 0.3em; text-transform: uppercase;
           color: var(--azul); }}
.cap-banner h1 {{ font-size: 22pt; margin: 1.5mm 0 3mm; color: var(--navy);
                 string-set: capitulo content(); }}
.cap-topicos {{ font-size: 8.4pt; color: var(--cinza); line-height: 1.6; }}

.topico {{ margin-bottom: 9mm; }}
h2 {{ font-size: 13pt; color: var(--navy); margin: 7mm 0 3.2mm;
     padding-bottom: 1.6mm; border-bottom: 1px solid var(--linha);
     page-break-after: avoid; }}
.h2-idx {{ color: var(--azul); margin-right: 3mm; font-size: 10.5pt; }}
p.teoria {{ margin: 0 0 2.6mm; text-align: justify; hyphens: auto; }}

/* ---------- caixas (fundo branco, borda colorida) ---------- */
.box {{ background: #fff; border: 1px solid var(--linha-suave);
       border-radius: 1.5mm; padding: 3mm 4mm 3mm 4.5mm; margin: 3.5mm 0;
       page-break-inside: avoid; }}
.box p {{ margin: 0; font-size: 8.9pt; }}
.box-rotulo {{ font-size: 7.5pt; font-weight: bold; letter-spacing: 0.14em;
              text-transform: uppercase; margin-bottom: 1.4mm; }}
.comocai {{ border-left: 1mm solid var(--azul); }}
.comocai .box-rotulo {{ color: var(--azul); }}
.pegadinha {{ border-left: 1mm solid var(--ambar); }}
.pegadinha .box-rotulo {{ color: var(--ambar); }}
.atalho {{ border-left: 1mm solid var(--verde); }}
.atalho .box-rotulo {{ color: var(--verde); }}

/* ---------- questões ---------- */
.questao {{ border: 1px solid var(--linha); border-radius: 1.5mm; margin: 3.5mm 0;
           page-break-inside: avoid; overflow: hidden; }}
.q-cab {{ color: var(--navy); font-weight: bold;
         font-size: 8pt; letter-spacing: 0.12em; text-transform: uppercase;
         padding: 2.2mm 4mm 1.8mm; border-bottom: 1px solid var(--linha-suave); }}
.q-enunciado {{ padding: 2.6mm 4mm 1mm; font-style: italic; color: #3c4454;
               font-size: 8.9pt; }}
.q-res-rotulo {{ padding: 2mm 4mm 0; font-size: 7.4pt; font-weight: bold;
                color: #8a93a3; letter-spacing: 0.14em; text-transform: uppercase; }}
.q-passos {{ padding: 1.5mm 4mm 3.2mm 9mm; }}
.q-passos li {{ margin-bottom: 1.2mm; font-size: 8.9pt; }}
.q-passos li::marker {{ color: var(--azul); font-weight: bold;
                       font-family: "DejaVu Sans", sans-serif; }}

/* ---------- fórmulas ---------- */
.formulas {{ display: flex; flex-wrap: wrap; gap: 2.5mm; margin: 3.5mm 0; }}
.chip {{ border: 1px solid var(--linha); border-top: 0.7mm solid var(--navy);
        border-radius: 1.5mm; padding: 2.2mm 4mm; background: #fff;
        page-break-inside: avoid; }}
.chip-rotulo {{ font-size: 7.3pt; color: var(--cinza); text-transform: uppercase;
               letter-spacing: 0.08em; margin-bottom: 1mm; }}
.chip-formula {{ font-size: 10.5pt; color: var(--navy); }}

.frac {{ display: inline-block; vertical-align: middle; text-align: center;
        font-size: 88%; line-height: 1.15; margin: 0 0.3mm; }}
.frac .num {{ display: block; border-bottom: 0.5pt solid currentColor; padding: 0 1mm; }}
.frac .den {{ display: block; padding: 0 1mm; }}
sub, sup {{ font-size: 68%; }}

/* ---------- formulário rápido ---------- */
.formulario {{ page-break-before: always; }}
.formulario > h1 {{ font-size: 19pt; color: var(--navy); margin-bottom: 2mm;
                   border-bottom: 2.5px solid var(--navy); padding-bottom: 3mm;
                   string-set: capitulo "Formulário rápido"; }}
.formulario .intro {{ color: var(--cinza); margin: 3mm 0 5mm; font-size: 9pt; }}
.form-aula {{ font-size: 10.5pt; color: var(--navy); margin: 5mm 0 2mm; }}
.form-tabela {{ width: 100%; border-collapse: collapse; }}
.form-tabela td {{ border: 1px solid var(--linha); padding: 1.8mm 3mm; vertical-align: middle; }}
.f-rotulo {{ width: 34%; font-size: 8.6pt; }}
.f-formula {{ width: 38%; font-size: 10pt; color: var(--navy);
             font-family: "DejaVu Sans", sans-serif; }}
.f-topico {{ width: 28%; font-size: 7.8pt; color: var(--cinza); }}
</style></head><body>

<div class="capa">
  <div class="marca">Física &nbsp;·&nbsp; Ciências da Natureza</div>
  <h1>Física para o ENEM<br><span class="fina">Resumo Completo</span></h1>
  <div class="sub">Teoria essencial, como cada tema cai na prova, questões-modelo
    resolvidas passo a passo, pegadinhas, atalhos e formulário rápido.</div>
  <div class="stats">
    <div class="stat"><b>{len(capitulos)}</b><span>aulas</span></div>
    <div class="stat"><b>{n_topicos}</b><span>tópicos</span></div>
    <div class="stat"><b>{n_questoes}</b><span>questões resolvidas</span></div>
  </div>
  <div class="rodape">Material de estudo sintetizado das videoaulas · uso pessoal · {hoje}</div>
</div>

<section class="sumario">
  <h1>Sumário</h1>
  {"".join(itens_toc)}
  <div class="toc-cap"><a href="#formulario"><span class="toc-num">★</span> Formulário rápido</a></div>
</section>

{"".join(corpo)}

<section class="formulario" id="formulario">
  <h1>Formulário rápido</h1>
  <p class="intro">Todas as fórmulas do material, agrupadas por aula, para revisão de véspera.</p>
  {"".join(linhas_form)}
</section>

</body></html>"""


def main() -> None:
    dados = json.loads((BASE / "dados.json").read_text(encoding="utf-8"))
    html_doc = construir_html(dados)
    (BASE / "resumo.html").write_text(html_doc, encoding="utf-8")

    from weasyprint import HTML
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc, base_url=str(BASE)).write_pdf(str(SAIDA))
    print(f"PDF gerado: {SAIDA}")


if __name__ == "__main__":
    main()
