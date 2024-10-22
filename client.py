import tkinter as tk
import pika
import threading
import time

# Variáveis globais para a fila e controle
connection = None
channel = None
queue_name = None
consumindo = False
stop_consuming = False

# Função para conectar ao broker RabbitMQ com reconexão automática
def conectar_broker(ip, port, usuario, senha):
    global connection, channel
    try:
        # Fechar a conexão anterior, se ainda estiver aberta
        if connection and connection.is_open:
            connection.close()
            print("Conexão anterior fechada.")

        # Definir as credenciais de autenticação
        credentials = pika.PlainCredentials(usuario, senha)

        # Tentar conectar ao broker com IP, Porta e Credenciais especificados
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip, port=int(port), credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange='time_broadcast', exchange_type='topic')
        print("Conectado ao broker.")
        return connection, channel
    except Exception as e:
        print(f"Erro ao conectar ao broker: {e}")
        return None, None

# Função para assinar novas time zones
def assinar_timezones(timezones):
    global channel, queue_name
    if channel and channel.is_open:
        for tz in timezones:
            try:
                channel.queue_bind(exchange='time_broadcast', queue=queue_name, routing_key=tz)
                print(f"Assinado na time zone: {tz}")
            except Exception as e:
                print(f"Erro ao assinar {tz}: {e}")
    else:
        print("Canal fechado, não é possível assinar.")

# Função para consumir mensagens em uma thread
def consumir_mensagens():
    global channel, queue_name, stop_consuming
    if channel and channel.is_open:
        try:
            def callback(ch, method, properties, body):
                routing_key = method.routing_key
                log_text.insert(tk.END, f"Sincronizando horário {routing_key}: {body.decode()}\n")
                log_text.see(tk.END)

            # Iniciar a sincronização e escutar o broker
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            while not stop_consuming:
                try:
                    channel.connection.process_data_events(time_limit=1)
                except pika.exceptions.ConnectionClosed:
                    print("Conexão perdida durante o consumo. Tentando reconectar...")
                    break
        except Exception as e:
            print(f"Erro ao consumir mensagens: {e}")

# Função chamada ao clicar em "Sincronizar"
def sincronizar_horarios():
    global queue_name, consumindo, stop_consuming, connection, channel

    # Obter IP, Porta, Usuário e Senha fornecidos pelo usuário
    ip_servidor = entry_ip.get()
    porta_servidor = entry_port.get()
    usuario = entry_user.get()
    senha = entry_pass.get()

    timezones_selecionadas = [lb_timezones.get(i) for i in lb_timezones.curselection()]
    
    if not timezones_selecionadas:
        log_text.insert(tk.END, "Nenhuma time zone selecionada para sincronização.\n")
    else:
        log_text.insert(tk.END, f"Time zones selecionadas: {', '.join(timezones_selecionadas)}\n")

        # Criar ou reconectar ao broker e criar uma nova fila exclusiva
        connection, channel = conectar_broker(ip_servidor, porta_servidor, usuario, senha)
        if channel and channel.is_open:
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            print(f"Fila exclusiva criada: {queue_name}")

            # Assinar as novas time zones
            assinar_timezones(timezones_selecionadas)

            # Iniciar a thread de consumo
            if not consumindo:
                consumindo = True
                stop_consuming = False
                consumer_thread = threading.Thread(target=consumir_mensagens)
                consumer_thread.start()
            else:
                stop_consumindo = True  # Sinaliza para parar o consumo anterior e reiniciar
                time.sleep(1)  # Pequena pausa para garantir que o consumo anterior parou
                stop_consumindo = False
                consumer_thread = threading.Thread(target=consumir_mensagens)
                consumer_thread.start()

# Configurar a interface gráfica
root = tk.Tk()
root.title("Cliente - Time Zones e Sincronização")

# Criar uma lista de time zones
timezones = [f"UTC{offset:+03d}" for offset in range(-12, 15)]

# Frame para a seleção de time zones
frame_timezones = tk.Frame(root)
frame_timezones.grid(row=0, column=0, padx=10, pady=10)

# Label para lista de time zones
label_timezones = tk.Label(frame_timezones, text="Selecione as Time Zones:")
label_timezones.pack()

# Listbox com múltipla seleção de time zones
lb_timezones = tk.Listbox(frame_timezones, selectmode=tk.MULTIPLE, height=10, width=30)
for tz in timezones:
    lb_timezones.insert(tk.END, tz)
lb_timezones.pack()

# Botão para sincronizar os horários
btn_sincronizar = tk.Button(frame_timezones, text="Sincronizar", command=sincronizar_horarios)
btn_sincronizar.pack(pady=5)

# Frame para exibir os logs
frame_logs = tk.Frame(root)
frame_logs.grid(row=0, column=1, padx=10, pady=10)

# Caixa de texto para logs
log_text = tk.Text(frame_logs, width=75, height=15, bg="black", fg="white", font=("Helvetica", 12))
log_text.pack(padx=10, pady=10)

# Frame para inserir IP, Porta, Usuário e Senha do servidor
frame_conexao = tk.Frame(root, bg="black")
frame_conexao.grid(row=0, column=2, padx=10, pady=10)

# Label e entrada para o IP do servidor
label_ip = tk.Label(frame_conexao, text="IP do Servidor:", bg="black", fg="white", font=("Helvetica", 12))
label_ip.pack(pady=5)
entry_ip = tk.Entry(frame_conexao, width=20)
entry_ip.pack(pady=5)

# Label e entrada para a Porta do servidor
label_port = tk.Label(frame_conexao, text="Porta do Servidor:", bg="black", fg="white", font=("Helvetica", 12))
label_port.pack(pady=5)
entry_port = tk.Entry(frame_conexao, width=10)
entry_port.pack(pady=5)

# Label e entrada para o nome de usuário do servidor
label_user = tk.Label(frame_conexao, text="Usuário:", bg="black", fg="white", font=("Helvetica", 12))
label_user.pack(pady=5)
entry_user = tk.Entry(frame_conexao, width=20)
entry_user.pack(pady=5)

# Label e entrada para a senha do servidor
label_pass = tk.Label(frame_conexao, text="Senha:", bg="black", fg="white", font=("Helvetica", 12))
label_pass.pack(pady=5)
entry_pass = tk.Entry(frame_conexao, show="*", width=20)
entry_pass.pack(pady=5)

# Configurações da janela principal
root.geometry("1200x600")  # Tamanho da janela ajustado
root.mainloop()
