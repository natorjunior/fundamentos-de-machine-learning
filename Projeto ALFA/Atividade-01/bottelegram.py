import telebot
from PIL import Image
import os
import io
from google.cloud import vision_v1
import uteis
from tika import parser
import re


BOT_NAME = uteis.BOT_NAME
USERNAME = uteis.USERNAME

# CHAVE API do bot do Telegram
CHAVE_API = uteis.CHAVE_API

# Iniciando o bot
bot = telebot.TeleBot(CHAVE_API)

# criando um objeto que representa variável de ambiente do usuário do sistema operacional
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = uteis.GOOGLE_APPLICATION_CREDENTIALS


# Mensagem que vai ser enviada quando receber a mensagem /opcao1. Enviando uma imagem na conversa
@bot.message_handler(commands=['opcao1'])
def opcao1(mensagem):
    img = Image.open('machine_learning.png')
    bot.send_photo(mensagem.chat.id, img)


# Mensagem que vai ser enviada quando receber a mensagem /opcao2
@bot.message_handler(commands=['opcao2'])
def opcao2(mensagem):
    # print(mensagem.date)
    # print(mensagem.chat.first_name)
    # print(mensagem.id)
    # print(mensagem.text)
    bot.send_message(mensagem.chat.id, 'OK. Conversa encerrada. Volte pra conversamos mais viu. Até!!')


# Salvando o documento quando enviar
@bot.message_handler(content_types=['document'])
def get_midias_recebidas(mensagem):
    bot.send_message(mensagem.chat.id, 'Estou fazendo o upload do arquivo')
    # doc = mensagem.message['document']['file_id'].get_file()
    # fileName = mensagem.message['document']['file_name']
    # doc.download(f'')
    # print(mensagem.document.file_id)
    raw = mensagem.document.file_id
    path = raw + ".pdf"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)
    # Enviando mensagem para avisar que a imagem foi salva
    bot.send_message(mensagem.chat.id, 'Documento salvo')

    # Abrindo o arquivo na memória e salvando a imagem na variável content
    with io.open(path, 'rb') as pdf_file:
        content = pdf_file.read()

    # Passando o arquivo pdf
    raw = parser.from_file(path)
    # print(raw)
    # Passando o conteúdo para a variável texto
    texto = raw['content']
    # tirando as quebras de página do texto
    texto = re.sub('\n', '', texto)
    print(texto)

    bot.reply_to(mensagem, f"Consegui entender esses caracteres do arquivo que me passou:\n{texto.strip()}")


# Enviando uma mensagem padrão quando enviar sticker, documento ou audio
@bot.message_handler(content_types=['sticker', 'document', 'audio'])
def get_midias_recebidas(mensagem):
    bot.reply_to(mensagem, "Não consigo entender audio e sticker. Me envie uma mensagem, blz!")


# Salvando a foto no sistema e verificando os caracteres da imagem
@bot.message_handler(content_types=['photo'])
def get_foto(mensagem):
    bot.send_message(mensagem.chat.id, 'Estou fazendo o upload da imagem')
    raw = mensagem.photo[-1].file_id
    # print(mensagem)
    # print(mensagem.photo[-1])

    # atribuindo o nome do file_id e concatenando com a extensão .png
    path = raw+".png"
    # Preparando o arquivo para download
    file_info = bot.get_file(raw)
    # Realizando o download do arquivo
    downloaded_file = bot.download_file(file_info.file_path)
    # abrindo o arquivo e gravando na raiz do projeto
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)
    # Enviando mensagem para avisar que a imagem foi salva
    bot.send_message(mensagem.chat.id, 'Imagem salva')

    # Instancia o cliente para ler a imagem do Cloud Vision
    client = vision_v1.ImageAnnotatorClient()
    # Abrindo o arquivo na memória e salvando a imagem na variável content
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    # Passando a imagem para o Vision
    image = vision_v1.types.Image(content=content)
    # Executa a deteção de texto na imagem
    response = client.text_detection(image=image)
    # retorna os carecteres anotados da imagem
    texts = response.text_annotations
    # print('Texts: ', texts)
    # print('Description: ', texts[0].description)
    # Fazendo a leitura dos caracteres lidos
    texto = ''
    index = 0
    for text in texts:
        if index == 0:
            texto += text.description
        index += 1
    # print(len(texto))
    texto_cpf = texto.find('CPF: ')
    print('CPF: ', texto[texto_cpf+5:texto_cpf+5+14])

    # mostrando os caracteres lidos na imagem
    bot.reply_to(mensagem, f"Consegui entender esses caracteres na imagem que me passou:\n{texto}")


# Passando uma resposta quando o comando for /start e /help para o bot
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    message_return= f"Olá {message.from_user.first_name} {message.from_user.last_name}, " \
                    f"eu sou um bot!\nEu consigo retirar textos de fotos. Também consigo retirar textos de PDF.\n" \
                    f"Porém de arquivos PDF não podem ser arquivos escaneados. Mas para isso acontecer, " \
                    f"é necessário ter em mente algumas regras:\n▪️O bot aceita apenas fotografias. no formato PNG" \
                    f"Gifs e vídeos ainda não são suportados. Ah! E não adianta enviar a foto como documento " \
                    f"também, eu só aceito 'ibagens'.\n▪️Não envie imagens de pessoas caso elas não " \
                    f" não saibam. Vamos respeitar a vontade do amigo de não querer a sua foto " \
                    f"pública.📵\n▪️Não envie nudes. Arrrr, vamos dizer que aqui não é o ambiente " \
                    f"apropriado para você mostrar os seus dotes. \n▪️Fotos com teor racista, " \
                    f"homofóbico, violento, ou que infrinjam, de qualquer forma e maneira serão excluídas, " \
                    f"o usuário identificado e banido.\n"
    bot.reply_to(message,message_return , parse_mode="HTML", disable_web_page_preview=True)


# Função padrão para qualquer mensagem enviada para o bot
def verificar(mensagem):
    # if mensagem.text == 'teste':
    #     return True
    # else:
    #     return False
    # print(mensagem)
    return True


# Resposta padrão
@bot.message_handler(func=verificar)
def responder(mensagem):
    # print(mensagem)
    texto = """
    Escolha uma opção para continuar (clique no item)
    /opcao1 Para receber uma foto minha
    /opcao2 Encerrar
    Se você me mandar um arquivo PDF eu vou tentar converter e mandar o texto pra você 👍!
    Se você me mandar um imagem com extensão PNG eu vou tentar ler o texto da imagem e mandar pra você 👍!
    Se me mandar um audio ou sticker eu vou te pedir para me mandar uma mensagem porque esses formatos eu não entendo. 
    """
    bot.reply_to(mensagem, texto)


# Vai deixar o nosso código em loop ouvindo as mensagens passadas para o bot
bot.polling(none_stop=True, timeout=123)
