import rclpy

from rclpy.node import Node
from robo_interfaces.msg import Monitoramento


class RoboTopicoSubscriber(Node):

    def __init__(self):
        super().__init__('robo_topico_subscriber')

        self.assinante = self.create_subscription(
            Monitoramento,
            'monitoramento',
            self.receber_dados,
            10
        )

    def receber_dados(self, mensagem):
        oxigenio = mensagem.nivel_oxigenio
        temperatura = mensagem.temperatura

        if 10 <= temperatura <= 40 and oxigenio > 80:
            situacao = 'Safe'
        else:
            situacao = 'Not Safe'

        self.get_logger().info(
            f'Oxigenio: {oxigenio:.0f} | '
            f'Temperatura: {temperatura:.0f} | '
            f'Situacao: {situacao}'
        )


def main(args=None):
    rclpy.init(args=args)

    no = RoboTopicoSubscriber()

    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()