"""Integração COM com Outlook clássico no Windows."""
from pathlib import Path


def enviar_email(assunto, html, anexos, email_to, email_cc, *, enviar=False):
    if not email_to.strip():
        raise ValueError('Preencha EMAIL_TO no config.py.')
    caminhos = [Path(p).resolve(strict=True) for p in anexos]
    import win32com.client
    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To, mail.CC = email_to, email_cc
    mail.Subject, mail.HTMLBody = assunto, html
    for caminho in caminhos:
        mail.Attachments.Add(str(caminho))
    if enviar:
        mail.Send()
    else:
        mail.Save()
