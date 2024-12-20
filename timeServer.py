import tkinter as tk
import pika
import socket
from datetime import datetime, timedelta, timezone

tempo_atualizacao = 5000  # Tempo padrão de 5 segundos

# Conexão global para RabbitMQ
connection = None
channel = None

# Função para conectar ao broker RabbitMQ uma vez
def conectar_broker():
    global connection, channel
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='time_broadcast', exchange_type='topic')
    except Exception as e:
        print(f"Erro ao conectar ao broker: {e}")

# Função para obter o IP local da máquina
def obter_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conecta a um endereço IP fictício na rede para obter o IP local
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"  # Default para localhost
    finally:
        s.close()
    return ip

# Função para enviar mensagens ao broker
def enviar_mensagem(mensagem, routing_key):
    global channel
    try:
        # Publica a mensagem no exchange com a routing_key da time zone
        channel.basic_publish(exchange='time_broadcast', routing_key=routing_key, body=mensagem)
        print(f"Mensagem enviada para {routing_key}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# Função para gerar os horários baseados em UTC com timezone-aware
def gerar_time_zones():
    timezones = []
    brasil_format = "%d-%m-%Y %H:%M:%S"
    now = datetime.now(timezone.utc)  # Hora atual em UTC, ciente de fuso horário

    # Gerar horários de UTC-12 até UTC+14
    for utc_offset in range(-12, 15):
        local_time = now + timedelta(hours=utc_offset)
        formatted_time = local_time.strftime(brasil_format)
        timezones.append((f"UTC{utc_offset:+03d}", formatted_time))
    
    return timezones

# Função para atualizar os horários e enviar ao broker
def atualizar_time_zones():
    global tempo_atualizacao
    try:
        timezones = gerar_time_zones()

        # Atualiza os horários na interface e envia a mensagem ao broker
        for i, (timezone, horario) in enumerate(timezones):
            labels[i].config(text=f"{timezone}: {horario}")
            enviar_mensagem(horario, routing_key=timezone)

        # Logar as time zones enviadas
        logar_sincronizacao("Servidor", [tz for tz, _ in timezones])

        # Reagendar a próxima atualização
        root.after(tempo_atualizacao, atualizar_time_zones)
    except Exception as e:
        print(f"Erro ao atualizar time zones: {e}")

# Função para registrar os logs na interface e no arquivo
def logar_sincronizacao(cliente_ip, timezones_sincronizados):
    # Formatar a string de log
    now = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
    log_msg = (f"[{now}] - {cliente_ip} sent to stream the timezones: {', '.join(timezones_sincronizados)}\n")

    # Exibir log na interface
    log_text.insert(tk.END, log_msg)
    log_text.see(tk.END)  # Rolagem automática para o último log

# Função para alterar o tempo de atualização
def alterar_tempo():
    global tempo_atualizacao
    try:
        novo_tempo = int(entry_tempo.get())
        tempo_atualizacao = novo_tempo
        log_text.insert(tk.END, f"Tempo de atualização alterado para {tempo_atualizacao} milissegundos.\n")
        log_text.see(tk.END)
    except ValueError:
        log_text.insert(tk.END, "Erro: O valor inserido deve ser um número inteiro.\n")
        log_text.see(tk.END)

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
frame_logs.grid(sticky='n', row=0, column=1, padx=10, pady=10)

# Caixa de texto para exibir os logs
log_text = tk.Text(frame_logs, width=75, height=30, bg="black", fg="white", font=("Helvetica", 12))
log_text.pack(padx=10, pady=10)

# Frame para alterar o tempo de atualização
frame_tempo = tk.Frame(root)
frame_tempo.grid(sticky='s', row=0, column=1, padx=10, pady=50)

# Entrada para tempo de atualização
label_tempo = tk.Label(frame_tempo, text="Tempo de atualização (ms):")
label_tempo.pack(side=tk.RIGHT)

entry_tempo = tk.Entry(frame_tempo)
entry_tempo.pack(side=tk.RIGHT)

# Botão para aplicar o tempo de atualização
btn_alterar_tempo = tk.Button(frame_tempo, text="Alterar", command=alterar_tempo)
btn_alterar_tempo.pack(side=tk.RIGHT, padx=5)

# Obter o IP local e exibir na interface
ip_local = obter_ip_local()
porta = 5672  # Porta padrão do RabbitMQ
label_info_ip = tk.Label(frame_tempo, text=f"Servidor IP: {ip_local} | Porta: {porta}", font=("Helvetica", 12), bg="black", fg="white", padx=10, pady=10)
label_info_ip.pack(pady=10)


# Conectar ao broker antes de iniciar as atualizações
conectar_broker()

# Inicializar com todos os horários
atualizar_time_zones()

# Configurações da janela principal
root.geometry("1200x600")  # Tamanho da janela ajustado

# Iniciar a interface gráfica
root.mainloop()
