# REL AUTOMATICO

Projeto montado a partir do documento Estrutura do Projeto RELATORIA AUTO.
Lê Backlog.xlsx e os CSVs BAIXATOA da data de referência, gera PDF executivo,
cinco gráficos, resumo HTML e indicadores JSON. Opcionalmente salva rascunho
ou solicita envio ao Outlook. O padrão gera arquivos sem enviar e-mail.

## 1. Instalar no Windows

1. Extraia esta pasta para um local fixo, por exemplo C:\RelatorioB2B.
2. Instale Python 3.11 ou superior com o inicializador `py`.
3. Dê dois cliques em `instalar.bat` e aguarde o término.
4. Abra `config.py` no Bloco de Notas e confira BACKLOG e PASTA_BAIXATOA.
   Os caminhos do Word foram preservados e precisam existir no seu computador.
5. Confira também EMAIL_TO e EMAIL_CC. Os destinatários do Word foram preservados.
   ANEXAR_BACKLOG=True inclui a planilha completa no e-mail; mude para False se
   quiser anexar somente o PDF.

O projeto pode estar em outra pasta: os scripts usam a própria localização.
Não é necessário copiar tudo para C:\RelatorioB2B.

## 2. Testar com dados fictícios

Abra o terminal na pasta do projeto e execute:

```bat
.venv\Scripts\python.exe gerar_exemplo.py
executar.bat --backlog dados_exemplo\Backlog.xlsx --pasta-toa dados_exemplo\BAIXATOA
```

Abra `output\AAAAMMDD\RelatorioExecutivo_AAAAMMDD.pdf` e `email.html`.
Nenhum e-mail é criado ou enviado nesse teste.

## 3. Usar os dados reais

Dê dois cliques em `testar.bat` para gerar o relatório e manter a janela aberta.
Ou execute no terminal:

```bat
executar.bat
executar.bat --data 2026-11-18
```

A data padrão é ontem, no relógio local do Windows. Sábados, domingos e feriados
também contam como dias corridos. A média usa os sete dias terminando na referência,
incluindo dias sem ativações. D-2 é o dia anterior à referência.

Os arquivos gerados ficam em `output\AAAAMMDD`; repetir a mesma data sobrescreve
os relatórios dessa data. Logs diários ficam em `logs` e falhas retornam código 1.

## 4. Conferir e enviar pelo Outlook

O módulo usa automação COM do Outlook clássico instalado no Windows com a conta
configurada. O aplicativo precisa disponibilizar Outlook.Application; a integração
não foi validada no novo Outlook. Confira a configuração no seu computador.

```bat
executar.bat --rascunho
```

Abra Rascunhos no Outlook e confira os destinatários, o resumo e os anexos.
Para solicitar o envio imediato pela conta padrão do Outlook:

```bat
executar.bat --enviar
```

O retorno de Send significa que o Outlook aceitou a solicitação; verifique a
Caixa de Saída e Itens Enviados para acompanhar o envio. Não há deduplicação:
executar --enviar duas vezes pode produzir dois e-mails.

## 5. Agendar no Windows

Somente após validar o PDF e o rascunho, abra Agendador de Tarefas > Criar Tarefa.

1. Em Geral, escolha sua conta e “Executar somente quando o usuário estiver conectado”.
2. Em Disparadores, crie a frequência e o horário desejados.
3. Em Ações, escolha Iniciar um programa.
4. Programa: `C:\RelatorioB2B\.venv\Scripts\python.exe`.
5. Argumentos: `"C:\RelatorioB2B\relatorio_redeb2b.py" --enviar`.
6. Iniciar em: `C:\RelatorioB2B`.
7. Em Configurações, escolha não iniciar nova instância se a tarefa já estiver executando.
8. Execute a tarefa manualmente uma vez e confira logs, PDF e Outlook.

Adapte os caminhos se extraiu em outra pasta. O computador deve estar ligado,
a sessão conectada, os arquivos OneDrive disponíveis localmente e o Outlook
operacional. Nenhuma tarefa é cadastrada automaticamente por este projeto.

## Dados esperados e regras

| Origem | Campos/regras |
| --- | --- |
| Backlog.xlsx | Primeira aba; colunas Data_RFS, Pedido, Cliente, Carteira |
| Data_RFS | Datas Excel ou texto de data; datas inválidas preenchidas interrompem a execução |
| CSV | Nomes terminando em _DD_MM_AA.csv; coluna Tipo |
| Codificação CSV | UTF-8 com BOM aceito, separador vírgula; ajustável em config.py |
| Ativações | Quantidade de linhas do Backlog na referência |
| Pedidos e Clientes | Valores distintos não vazios nas ativações |
| Atividades Campo | Linhas dos CSVs cujo Tipo pertence à lista TIPOS_VALIDOS |
| Duplicidades CSV | Mantidas como no Word; não foi fornecida uma chave para remover duplicados |

Os CSVs são selecionados pelo nome do arquivo; não há filtro interno por data
nem por status. A contagem não pressupõe que toda atividade seja concluída.
Essas regras reproduzem o documento e podem ser ajustadas conforme sua base.

Se nenhum CSV for localizado, a execução falha antes de enviar. Para gerar
um relatório parcial, use `--permitir-sem-csv`; o indicador de campo fica
explicitamente indisponível. Pasta incorreta também causará ausência de CSV.

Erros de coluna: confira cabeçalhos e ABA_BACKLOG. Erros de codificação ou
separador: altere CSV_ENCODING e CSV_SEPARADOR. Erros de acesso: feche arquivos
bloqueados e marque as fontes no OneDrive como disponíveis neste dispositivo.

## Validação e limites

Inclui dados sintéticos para testar geração e regras sem os arquivos reais.
A execução com as planilhas corporativas e o envio Outlook dependem do seu ambiente.
O pacote não instala nem configura a conta Outlook e não executa envios ao ser extraído.

Validação realizada na preparação: compilação dos módulos e testes de indicadores,
CSV ausente, relatório parcial, período vazio e data inválida com dados fictícios.
Geração visual do PDF e gráficos não foi executada: matplotlib, reportlab e pillow
não estavam disponíveis e o ambiente não conseguiu acessar o instalador online.
O envio e o rascunho Outlook também não foram executados.
