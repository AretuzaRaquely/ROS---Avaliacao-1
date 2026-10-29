import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetarAmostra


class RoboColetaCliente(Node):

    def __init__(self):
        super().__init__('robo_coleta_cliente')

        self.cliente = self.create_client(
            ColetarAmostra,
            'coleta_material'
        )

    def solicitar_coleta(self):
        while not self.cliente.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Aguardando o servico coleta_material...'
            )

        requisicao = ColetarAmostra.Request()
        requisicao.profundidade = random.uniform(0.1, 0.5)

        self.get_logger().info(
            f'Solicitando coleta a {requisicao.profundidade:.2f} m'
        )

        futuro = self.cliente.call_async(requisicao)
        rclpy.spin_until_future_complete(self, futuro)

        if futuro.result() is not None:
            resposta = futuro.result()

            if resposta.sucesso:
                self.get_logger().info('Coleta bem-sucedida!')
            else:
                self.get_logger().info('Coleta nao foi bem-sucedida.')
        else:
            self.get_logger().error('Falha ao receber a resposta do servico.')


def main(args=None):
    rclpy.init(args=args)

    no = RoboColetaCliente()

    try:
        no.solicitar_coleta()
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()