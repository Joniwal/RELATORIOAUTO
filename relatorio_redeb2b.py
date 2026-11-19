"""Gera relatório D-1. O envio exige a opção explícita --enviar."""
import argparse
from datetime import date, timedelta
from html import escape
import json
import logging
from pathlib import Path
import sys

import pandas as pd
import config


def validar_colunas(df, obrigatorias, origem):
    df.columns = df.columns.astype(str).str.strip()
    faltam = set(obrigatorias) - set(df.columns)
    if faltam:
        raise ValueError(f'{origem}: colunas ausentes: {", ".join(sorted(faltam))}')


def analisar(backlog, pasta_toa, data_ref, *, permitir_sem_csv=False):
    base = pd.read_excel(backlog, sheet_name=config.ABA_BACKLOG)
    validar_colunas(base, ['Data_RFS', 'Pedido', 'Cliente', 'Carteira'], 'Backlog')
    original = base['Data_RFS']
    datas = pd.to_datetime(original, dayfirst=True, errors='coerce', format='mixed')
    invalidas = original.notna() & original.astype(str).str.strip().ne('') & datas.isna()
    if invalidas.any():
        raise ValueError(f'Backlog: {invalidas.sum()} datas Data_RFS inválidas. Corrija a planilha.')
    base['Data_RFS'] = datas.dt.date
    ativacoes = base[base['Data_RFS'] == data_ref]
    arquivos = sorted(Path(pasta_toa).glob(f'*_{data_ref:%d_%m_%y}.csv'))
    if not arquivos and not permitir_sem_csv:
        raise FileNotFoundError(f'Nenhum CSV *_{data_ref:%d_%m_%y}.csv em {pasta_toa}')
    partes = []
    for arquivo in arquivos:
        df = pd.read_csv(arquivo, sep=config.CSV_SEPARADOR, encoding=config.CSV_ENCODING)
        validar_colunas(df, ['Tipo'], arquivo.name)
        partes.append(df)
    toa = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=['Tipo'])
    campo = toa[toa['Tipo'].astype(str).str.strip().isin(config.TIPOS_VALIDOS)]
    dias = [data_ref-timedelta(days=i) for i in range(29, -1, -1)]
    evolucao = base['Data_RFS'].value_counts().reindex(dias, fill_value=0)
    indicadores = {
        'Ativações': len(ativacoes), 'Pedidos': int(ativacoes['Pedido'].nunique()),
        'Clientes': int(ativacoes['Cliente'].nunique()),
        'Atividades Campo': len(campo) if arquivos else 'Indisponível (sem CSV)',
        'D-2': int(evolucao.loc[data_ref-timedelta(days=1)]),
        'Média 7 Dias': round(float(evolucao.iloc[-7:].mean()), 2),
    }
    return indicadores, ativacoes, campo, evolucao, arquivos


def gerar_graficos(ativacoes, campo, evolucao, destino):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    imagens = []
    for coluna, df, nome in [('Carteira', ativacoes, 'carteiras'),
                              ('Cliente', ativacoes, 'clientes'), ('Tipo', campo, 'tipos')]:
        fig, ax = plt.subplots(figsize=(11, 6))
        serie = df[coluna].dropna().value_counts().head(10).sort_values()
        if serie.empty:
            ax.text(.5, .5, 'Sem registros disponíveis', ha='center', transform=ax.transAxes)
        else:
            serie.plot.barh(ax=ax, color='#660099')
        ax.set_title(f'Top 10 — {coluna}')
        ax.set_xlabel('Quantidade')
        fig.tight_layout()
        caminho = destino / f'{nome}.png'
        fig.savefig(caminho, dpi=140)
        plt.close(fig)
        imagens.append((f'Top 10 — {coluna}', caminho))
    for quantidade, nome in [(7, 'evolucao7dias'), (30, 'tendencia30dias')]:
        fig, ax = plt.subplots(figsize=(11, 6))
        serie = evolucao.iloc[-quantidade:]
        ax.plot(pd.to_datetime(serie.index), serie.values, marker='o', color='#660099')
        ax.set_title(f'Ativações — últimos {quantidade} dias')
        ax.set_ylim(bottom=0)
        ax.grid(alpha=.25)
        fig.autofmt_xdate()
        fig.tight_layout()
        caminho = destino / f'{nome}.png'
        fig.savefig(caminho, dpi=140)
        plt.close(fig)
        imagens.append((f'Evolução de {quantidade} dias', caminho))
    return imagens


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=date.fromisoformat, default=date.today()-timedelta(days=1), help='Referência AAAA-MM-DD (padrão ontem)')
    parser.add_argument('--backlog', type=Path, default=config.BACKLOG)
    parser.add_argument('--pasta-toa', type=Path, default=config.PASTA_BAIXATOA)
    parser.add_argument('--output', type=Path, default=config.OUTPUT)
    parser.add_argument('--permitir-sem-csv', action='store_true', help='Relatório parcial sinalizado; não assume campo igual a zero')
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument('--rascunho', action='store_true', help='Salva e-mail no Outlook, sem enviar')
    modos.add_argument('--enviar', action='store_true', help='Envia pelo Outlook para os destinatários de config.py')
    args = parser.parse_args(argv)
    config.LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.FileHandler(config.LOGS / f'relatorio_{date.today():%Y%m%d}.log', encoding='utf-8'), logging.StreamHandler()])
    try:
        indicadores, ativacoes, campo, evolucao, arquivos = analisar(
            args.backlog, args.pasta_toa, args.data, permitir_sem_csv=args.permitir_sem_csv)
        destino = args.output / f'{args.data:%Y%m%d}'
        destino.mkdir(parents=True, exist_ok=True)
        imagens = gerar_graficos(ativacoes, campo, evolucao, destino)
        from pdf_report import gerar_pdf
        pdf = destino / f'RelatorioExecutivo_{args.data:%Y%m%d}.pdf'
        gerar_pdf(pdf, args.data.strftime('%d/%m/%Y'), indicadores, imagens,
                  ativacoes['Carteira'].value_counts().head(10), ativacoes['Cliente'].value_counts().head(10))
        html = '<meta charset="utf-8"><h2>Relatório Diário Rede B2B</h2>'
        html += f'<p>Referência: {args.data:%d/%m/%Y}</p>'
        html += ''.join(f'<p><b>{escape(k)}</b>: {escape(str(v))}</p>' for k, v in indicadores.items())
        (destino / 'email.html').write_text(html, encoding='utf-8')
        (destino / 'indicadores.json').write_text(json.dumps(indicadores, ensure_ascii=False, indent=2), encoding='utf-8')
        logging.info('PDF gerado: %s; CSVs lidos: %s', pdf, len(arquivos))
        if args.enviar or args.rascunho:
            from email_sender import enviar_email
            anexos = [pdf] + ([args.backlog] if config.ANEXAR_BACKLOG else [])
            enviar_email(f'[REDE B2B] Relatório Diário - {args.data:%d/%m/%Y}', html,
                         anexos, config.EMAIL_TO, config.EMAIL_CC, enviar=args.enviar)
            logging.info('Envio solicitado ao Outlook' if args.enviar else 'Rascunho salvo no Outlook')
        return 0
    except Exception:
        logging.exception('Falha ao gerar/enviar relatório')
        return 1


if __name__ == '__main__':
    sys.exit(main())
