"""Configuração editável do relatório. Caminhos relativos partem desta pasta."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKLOG = Path(r"C:\Users\a0072716\OneDrive - Telefonica\HQSuporte - APPREDE\Backlog.xlsx")
PASTA_BAIXATOA = Path(r"C:\Users\a0072716\OneDrive - Telefonica\HQSuporte - APPREDE\BAIXATOA")
OUTPUT = BASE_DIR / 'output'
LOGS = BASE_DIR / 'logs'
ABA_BACKLOG = 0  # Primeira aba; pode ser substituído pelo nome da aba.
CSV_SEPARADOR = ','  # Altere para ';' se necessário.
CSV_ENCODING = 'utf-8-sig'  # Altere para 'cp1252' se necessário.
ANEXAR_BACKLOG = True
EMAIL_TO = ';'.join([
    'wilson.gfilho@telefonica.com', 'antonio.fontana@telefonica.com',
    'Jose.Grolli@telefonica.com', 'Danielli.Gois@telefonica.com',
    'Eliane.Terres@telefonica.com',
])
EMAIL_CC = ';'.join([
    'Marcos.Neves@telefonica.com', 'Oseias.Galli@telefonica.com',
    'Francisco.LBarbosa@telefonica.com', 'cintia.diniz@telefonica.com',
    'isabella.przibella@telefonica.com', 'juliana.fcruz@telefonica.com',
    'joni.amaral@telefonica.com',
])
TIPOS_VALIDOS = [
    'Instalação Dados', 'Migração de Acesso', 'Instalação Internet X',
    'Retirada Roteador', 'Instalação Internet X Light', 'Instalação Dados Roteador',
]
