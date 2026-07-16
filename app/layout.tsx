import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "INEP Atlas — Banco de Questões ENEM",
    template: "%s — INEP Atlas",
  },
  description:
    "Banco de questões do ENEM com matriz de referência, microdados oficiais e análise de dificuldade pela TRI.",
  other: { "codex-preview": "development" },
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

const nav = [
  ["Visão geral", "/"],
  ["Banco", "/banco"],
  ["Matriz", "/matriz"],
  ["Estudar", "/legacy/estudar.html"],
  ["Meu painel", "/legacy/meu-painel.html"],
  ["Microdados", "/legacy/painel-oficial.html"],
  ["Materiais", "/legacy/materiais.html"],
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <header className="topbar">
          <a className="wordmark" href="/" aria-label="INEP Atlas — início">
            <span className="wordmark-mark">IA</span>
            <span className="wordmark-copy">
              <strong>INEP Atlas</strong>
              <small>Inteligência para o ENEM</small>
            </span>
          </a>
          <nav className="topnav" aria-label="Navegação principal">
            {nav.map(([label, href]) => <a href={href} key={href}>{label}</a>)}
          </nav>
          <a className="header-cta" href="/legacy/estudar.html">Iniciar estudo</a>
        </header>
        {children}
        <footer className="footer">
          <div>
            <strong>INEP Atlas</strong>
            <p>Leitura estratégica dos itens do ENEM, com dados oficiais e critérios transparentes.</p>
          </div>
          <div className="footer-meta">
            <span>540 questões não regulares</span>
            <span>120 habilidades da matriz</span>
            <span>Microdados INEP 2009–2025</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
