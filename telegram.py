# -*- coding: utf-8 -*-

import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import re
import logging
from onvotar import calculate

logger = logging.getLogger()

_DNI_PATTERN = re.compile('^([0-9]{8}[^A-Z]?[A-Z])$')
_DOB_PATTERN = re.compile('^([0-9]{8})$')
_ZIP_PATTERN = re.compile('^([0-9]{5})$')

DEFAULT_ERR = (
    'Per conèixer el teu col·legi electoral, '
    'envia un missatge amb les teves dades '
    'separades per espais i '
    'fent servir aquest format: \n'
    'DNI DATA_NAIXEMENT CODI_POSTAL\n\n'
    'Exemple:\n00001714N 01/10/2017 01234'
)

DATA_DISCLAIMER = (
    'Aquest bot utilitza la mateixa tecnologia que '
    'la web original oficial del Referèndum.\n'
    'No desa ni mostra als autors cap dada sensible.'
)

TOKEN = ''
bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.

def _check_input_data(text):
        splitted = text.split(' ')
        if len(splitted) != 3:
                raise ValueError(DEFAULT_ERR)

        raw_dni, raw_date, cp = splitted

        dni = raw_dni.upper().replace(' ','').replace('-','')
        match = _DNI_PATTERN.match(dni)
        if not match:
                raise ValueError('Revisa el format del DNI')

        date = raw_date.upper().replace(' ','').replace('/','')
        match = _DOB_PATTERN.match(date)
        if not match:
                raise ValueError('Revisa el format de la data de naixement')
        date = date[-4:]+date[2:4]+date[:2]

        match = _ZIP_PATTERN.match(cp)
        if not match:
                raise ValueError('Revisa el format del codi postal')

        return dni, date, cp

@bot.message_handler(func=lambda message: True, content_types=["text"])
def my_text(message):
	id_usuari = message.chat.id
	nom_usuari = message.chat.first_name
	text = message.text.split(' ')
	if len(text)!=3:
		print("No es correcte")
	else:
		text=' '.join(text)
		print(text)
		dni, date, cp = _check_input_data(text)
		result = calculate(dni, date, cp)
		print(result)
		if result:
			response = (
				'{}\n{}\n{}\n\n'
				'Districte: {}\n'
				'Secció: {}\n'
				'Mesa: {}'
			).format(*result)
			logger.info(
				'Punt de votacio retornat correctament. %s %s',
				date[:4], cp
			)
		else:
			response = (
				'Alguna de les dades entrades no és correcta.\n'
				'Revisa-les, si us plau.'
			)
			logger.info('Bon format pero dades incorrectes')
		bot.send_message(message.from_user.id,response)

bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algún fallo.