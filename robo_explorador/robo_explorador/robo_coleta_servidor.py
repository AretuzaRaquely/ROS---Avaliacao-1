import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetarAmostra


class RoboColetaServidor(Node):

    def __init__(self):
        super().__init__('robo_coleta_servidor')

        self.servico = self.create_service(
            ColetarAmostra,
            'coleta_material',
            self.processar_coleta
        )

        self.get_logger().info(
            'Servidor coleta_material iniciado.'
        )

    def processar_coleta(self, requisicao, resposta):
        profundidade = requisicao.profundidade
        numero = random.random()

        resposta.sucesso = numero <= 0.7

        self.get_logger().info(
            f'Profundidade solicitada: {profundidade:.2f} m'
        )
        self.get_logger().info(
            f'Numero sorteado: {numero:.3f}'
        )
        self.get_logger().info(
            f'Sucesso: {resposta.sucesso}'
        )

        return resposta


def main(args=None):
    rclpy.init(args=args)

    no = RoboColetaServidor()

    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()