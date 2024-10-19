import pika
import tkinter as tk
from datetime import datetime, timedelta, timezone

# Arquivo de log
log_file = "logs_sincronizacao.txt"

# Função para enviar mensagens ao broker
def enviar_mensagem(mensagem):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declara o exchange para envio das mensagens
    channel.exchange_declare(exchange='time_broadcast', exchange_type='fanout')

    # Publica a mensagem no exchange
    channel.basic_publish(exchange='time_broadcast', routing_key='', body=mensagem)
    connection.close()

# Função para gerar os horários baseados em UTC com timezone-aware
def gerar_time_zones():
    timezones = []
    brasil_format = "%d-%m-%Y %H:%M:%S"
    now = datetime.now(timezone.utc)  # Hora atual em UTC, ciente de fuso horário

    # Gerar horários de UTC-12 até UTC+14
    for utc_offset in range(-12, 15):
        local_time = now + timedelta(hours=utc_offset)
        formatted_time = local_time.strftime(brasil_format)
        timezones.append(f"UTC{utc_offset:+03d}: {formatted_time}")
    
    return timezones

# Função para atualizar os horários e enviar ao broker
def atualizar_time_zones():
    timezones = gerar_time_zones()

    # Atualiza os horários na interface e envia a mensagem ao broker
    mensagem = ""
    for i, label in enumerate(labels):
        label.config(text=timezones[i])
        mensagem += timezones[i] + "\n"
    
    # Enviar os horários ao broker
    enviar_mensagem(mensagem)

    # Logar a sincronização no arquivo e na interface
    logar_sincronizacao("Servidor", timezones)

    root.after(1000, atualizar_time_zones)  # Atualizar a cada 10 segundos

# Função para registrar os logs na interface e no arquivo
def logar_sincronizacao(cliente_ip, timezones_sincronizados):
    # Formatar a string de log
    now = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
    log_msg = (f"Cliente {cliente_ip} synchronized at {now} with timezones: {', '.join(timezones_sincronizados)}\n")

    # Exibir log na interface
    log_text.insert(tk.END, log_msg)
    log_text.see(tk.END)  # Rolagem automática para o último log

    # Gravar log no arquivo
    with open(log_file, "a") as f:
        f.write(log_msg)

# Configurar a interface gráfica
root = tk.Tk()
root.title("Servidor de Time Zones - UTC e Logs")

# Definir o estilo do display digital
display_font = ("Helvetica", 18, "bold")
bg_color = "black"
fg_color = "lime"

# Criar um frame para a interface dos horários (metade esquerda)
frame_horarios = tk.Frame(root, bg=bg_color)
frame_horarios.grid(row=0, column=0, padx=10, pady=10)

# Lista de labels para exibir os horários
labels = []

# Criar um grid para organizar os horários em duas colunas
for i in range(27):  # UTC-12 até UTC+14 (27 zonas)
    label = tk.Label(frame_horarios, text="", font=display_font, bg=bg_color, fg=fg_color, padx=10, pady=10)
    label.grid(row=i // 2, column=i % 2, padx=20, pady=10)  # Organizar em duas colunas
    labels.append(label)

# Criar um frame para os logs (metade direita)
frame_logs = tk.Frame(root, bg="black")
frame_logs.grid(row=0, column=1, padx=10, pady=10)

# Caixa de texto para exibir os logs
log_text = tk.Text(frame_logs, width=50, height=30, bg="black", fg="white", font=("Helvetica", 12))
log_text.pack(padx=10, pady=10)

# Inicializar com todos os horários
atualizar_time_zones()

# Configurações da janela principal
root.geometry("1200x600")  # Tamanho da janela ajustado

# Iniciar a interface gráfica
root.mainloop()
