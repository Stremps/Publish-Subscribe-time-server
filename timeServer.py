import tkinter as tk
from datetime import datetime, timedelta

# Arquivo de log
log_file = "logs_sincronizacao.txt"

# Função para gerar os horários baseados em UTC
def gerar_time_zones():
    timezones = []
    brasil_format = "%d-%m-%Y %H:%M:%S"
    now = datetime.utcnow()  # Hora atual em UTC

    # Gerar horários de UTC-12 até UTC+14
    for utc_offset in range(-12, 15):
        local_time = now + timedelta(hours=utc_offset)
        formatted_time = local_time.strftime(brasil_format)
        timezones.append(f"UTC{utc_offset:+03d}: {formatted_time}")
    
    return timezones

# Função para atualizar os horários na interface
def atualizar_time_zones():
    timezones = gerar_time_zones()
    
    for i, label in enumerate(labels):
        label.config(text=timezones[i])
    
    root.after(1000, atualizar_time_zones)  # Atualizar a cada 10 segundos

# Função para logar sincronização
def logar_sincronizacao(cliente_ip, timezones_sincronizados, horario_cliente):
    # Formatar a string de log
    log_msg = (f"Cliente {cliente_ip} synchronized {timezones_sincronizados} - "
               f"Client time: {horario_cliente} ---> Server times: {', '.join(timezones_sincronizados)}\n")

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

# Atualizar os horários inicialmente
atualizar_time_zones()

# Criar um frame para os logs (metade direita)
frame_logs = tk.Frame(root, bg="black")
frame_logs.grid(row=0, column=1, padx=10, pady=10)

# Caixa de texto para exibir os logs
log_text = tk.Text(frame_logs, width=50, height=30, bg="black", fg="white", font=("Helvetica", 12))
log_text.pack(padx=10, pady=10)

# Exemplo de como logar uma sincronização (substituir por evento real)
logar_sincronizacao("192.168.1.100", ["UTC+00", "UTC+01"], "19-10-2024 13:14:52")

# Configurações da janela principal
root.geometry("1200x600")  # Tamanho da janela ajustado

# Iniciar a interface gráfica
root.mainloop()
