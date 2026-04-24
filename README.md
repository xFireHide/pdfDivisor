# Processador de PDF para etiquetas (Shopee → impressora térmica)

Programa **desktop** que divide cada página de um PDF em **quatro quadrantes**, gerando **uma etiqueta por página**. Foi criado para **uso pessoal** na operação de uma loja na **Shopee**, onde o arquivo de envio vem com **quatro etiquetas na mesma folha** — formato que não conversa bem com **impressora térmica** (ex.: Zebra e similares), que esperam **uma etiqueta por impressão/página**.

**Sobre ZPL (`.zpl`):** impressoras Zebra costumam usar **ZPL**. Na prática, **minha funcionária tinha dificuldade com esse formato**; o fluxo ficou em **PDF** (visual, familiar), só **separando as etiquetas** antes de imprimir na térmica — sem depender de arquivos `.zpl` no dia a dia.

## Por que este projeto existe

Imprimir direto o PDF da Shopee na térmica era impraticável: **4 etiquetas em quadrantes** na mesma página. Este programa **recorta automaticamente** cada quadrante, ignora quadrantes vazios (heurística) e gera um PDF com **uma etiqueta por página**.

### Contexto da loja (volume que justifica a automação)

![Métricas principais da loja na Shopee — vendas, pedidos e gráfico de tendências](docs/shopee-metricas-principais.png)

*Painel de métricas no momento da captura; os números podem mudar ao longo do tempo.*

## Como usar

Depois de instalar dependências e executar `python desktop.py` (ou `python3 desktop.py`), o fluxo é:

1. Abre uma **janela gráfica** (tkinter): leia o texto de ajuda, clique em **Selecionar PDF…**.
2. Clique em **Processar e salvar como…** — a barra de progresso indica que está trabalhando (o PDF grande pode demorar).
3. Escolha **onde salvar** o PDF processado (nome sugerido: `*_1-etiqueta-por-pagina.pdf`).

### Instalação e execução

**macOS / Linux (recomendado — Python “externally managed” do Homebrew):**

```text
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python desktop.py
```

Ou, na raiz do projeto: `./run.sh` (cria o `.venv` e instala dependências na primeira vez).

**Windows (Prompt na pasta do projeto):**

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python desktop.py
```

## Como funciona (técnico)

| Arquivo | Função |
|--------|--------|
| `processor.py` | Rasteriza o PDF (PyMuPDF), divide em 4 quadrantes, filtra branco, monta o PDF de saída. |
| `desktop.py` | Interface gráfica (tkinter/ttk): selecionar PDF, processar em segundo plano, salvar resultado. |

1. Cada página é renderizada em alta resolução (300 DPI).
2. Divisão em **4 retângulos** (quadrantes).
3. Quadrantes muito claros são ignorados.
4. Cada quadrante válido vira **uma página** no PDF final.

## Requisitos

- **Runtime:** Python 3.10+, `pymupdf`, `pillow` — ver `requirements.txt`.

## Licença e aviso

Projeto para **uso pessoal**. Teste sempre uma amostra antes de imprimir em lote; mudanças no layout das etiquetas da Shopee podem afetar o recorte.
