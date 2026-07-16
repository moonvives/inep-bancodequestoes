# INEP Atlas — Banco de Questões ENEM

Nova plataforma independente para exploração de questões, habilidades e microdados do ENEM.

## O que existe nesta versão

- página inicial editorial com síntese analítica da base;
- banco pesquisável com 540 questões de Ciências da Natureza das edições não regulares;
- filtros combináveis por texto, área, habilidade, ano e dificuldade TRI;
- Matriz de Referência completa, com 120 habilidades das quatro áreas;
- modos de estudo, painel pessoal, microdados oficiais e materiais preservados da base anterior;
- histórico de estudo e PIN mantidos localmente no dispositivo;
- interface responsiva para computador, tablet e celular.

## Origem e preservação

O projeto usa como fonte de leitura o conteúdo de `moonvives/enem-plataforma-GERAL`, sem alterar esse repositório nem o site já publicado. Todo o desenvolvimento desta versão ocorre de forma independente neste repositório.

## Desenvolvimento

```bash
npm ci
npm run dev
```

Para validar a versão de produção:

```bash
npm run build
```
