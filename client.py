import pika

# Função para processar as mensagens recebidas
def callback(ch, method, properties, body):
    print("Horário recebido:")
    print(body.decode())

# Conectar ao broker RabbitMQ
def conectar_ao_broker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar o exchange de broadcast
    channel.exchange_declare(exchange='time_broadcast', exchange_type='fanout')

    # Criar uma fila exclusiva para o cliente
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Vincular a fila ao exchange
    channel.queue_bind(exchange='time_broadcast', queue=queue_name)

    # Iniciar o consumo de mensagens
    print("Aguardando mensagens de horários...")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    conectar_ao_broker()
