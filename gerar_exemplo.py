"""Dados fictícios para testar sem acessar os arquivos corporativos."""
from datetime import date, timedelta
from pathlib import Path
import pandas as pd


def gerar(destino):
    destino = Path(destino)
    toa = destino / 'BAIXATOA'
    toa.mkdir(parents=True, exist_ok=True)
    referencia = date.today()-timedelta(days=1)
    registros = []
    for i in range(30):
        for j in range(i % 5 + 1):
            registros.append({'Data_RFS': referencia-timedelta(days=i),
                              'Pedido': f'P{i:02}{j:02}', 'Cliente': f'Cliente fictício {j+1}',
                              'Carteira': f'Carteira {j % 3+1}'})
    pd.DataFrame(registros).to_excel(destino/'Backlog.xlsx', index=False)
    pd.DataFrame({'Tipo': ['Instalação Dados', 'Migração de Acesso', 'Outro']}).to_csv(
        toa/f'exemplo_{referencia:%d_%m_%y}.csv', index=False, encoding='utf-8-sig')
    print(f'Dados fictícios em {destino.resolve()}')


if __name__ == '__main__':
    gerar(Path(__file__).resolve().parent/'dados_exemplo')
