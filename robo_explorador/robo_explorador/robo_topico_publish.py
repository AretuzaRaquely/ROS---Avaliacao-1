import random
import rclpy
from rclpy.node import Node
from robo_interfaces.msg import Monitoramento


class RoboTopicoPublish(Node):

    def __init__(self):
        super().__init__('robo_topico_publish')

        self.publicador = self.create_publisher(
            Monitoramento,
            'monitoramento',
            10
        )

        self.timer = self.create_timer(1.0, self.publicar_dados)

    def publicar_dados(self):
        mensagem = Monitoramento()

        mensagem.nivel_oxigenio = float(random.randint(1, 100))
        mensagem.temperatura = float(random.randint(1, 100))

        self.publicador.publish(mensagem)

        self.get_logger().info(
            f'Oxigenio: {mensagem.nivel_oxigenio:.0f} | '
            f'Temperatura: {mensagem.temperatura:.0f}'
        )


def main(args=None):
    rclpy.init(args=args)

    no = RoboTopicoPublish()

    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()