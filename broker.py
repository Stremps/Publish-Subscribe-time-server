import pika

# Função para configurar o broker RabbitMQ
def configurar_broker():
    # Estabelece uma conexão com o RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declara o exchange para comunicação usando 'topic' (para uso com routing keys)
    channel.exchange_declare(exchange='time_broadcast', exchange_type='topic')

    print("Broker configurado e aguardando conexões...")

    # O broker não precisa consumir as mensagens, apenas encaminhá-las.
    # Mantém o broker ativo
    try:
        channel.start_consuming()  # Espera indefinidamente por publicadores e assinantes
    except KeyboardInterrupt:
        print("Broker interrompido manualmente.")
        connection.close()

if __name__ == "__main__":
    configurar_broker()
