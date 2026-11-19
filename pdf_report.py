"""PDF com resumo, rankings na mesma página e gráficos proporcionais."""
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


def gerar_pdf(caminho_pdf, data_ref, indicadores, imagens, top_carteiras, top_clientes):
    pdf = SimpleDocTemplate(str(caminho_pdf), pagesize=A4, rightMargin=36,
                            leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elementos = [Paragraph('RELATÓRIO DIÁRIO REDE B2B', styles['Title']),
                 Paragraph(f'Data referência: {data_ref}', styles['Heading2']), Spacer(1, 16)]
    for chave, valor in indicadores.items():
        elementos.append(Paragraph(f'<b>{escape(str(chave))}</b>: {escape(str(valor))}', styles['Normal']))
        elementos.append(Spacer(1, 9))
    elementos.append(PageBreak())
    for titulo, serie in [('TOP CARTEIRAS', top_carteiras), ('TOP CLIENTES', top_clientes)]:
        elementos.append(Paragraph(titulo, styles['Heading1']))
        linhas = [['Descrição', 'Qtde']] + [
            [Paragraph(escape(str(k)), styles['Normal']), str(v)] for k, v in serie.items()]
        if len(linhas) == 1:
            linhas.append(['Sem ativações no período', '0'])
        tabela = Table(linhas, colWidths=[pdf.width-65, 65], repeatRows=1)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#660099')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ]))
        elementos.extend([tabela, Spacer(1, 14)])
    for titulo, caminho in imagens:
        elementos.extend([PageBreak(), Paragraph(titulo, styles['Heading1'])])
        img = Image(str(caminho))
        escala = min(pdf.width/img.imageWidth, 620/img.imageHeight)
        img.drawWidth, img.drawHeight = img.imageWidth*escala, img.imageHeight*escala
        elementos.append(img)
    pdf.build(elementos)
