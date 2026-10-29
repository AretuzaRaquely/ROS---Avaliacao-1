import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from robo_interfaces.action import Deslocar


class RoboDeslocamentoCliente(Node):

    def __init__(self):
        super().__init__('robo_deslocamento_cliente')

        self.cliente = ActionClient(
            self,
            Deslocar,
            'deslocar_robo'
        )

    def receber_feedback(self, mensagem):
        feedback = mensagem.feedback

        self.get_logger().info(
            f'Feedback: latitude={feedback.latitude_atual:.2f}, '
            f'longitude={feedback.longitude_atual:.2f}'
        )

    def enviar_meta(self):
        self.cliente.wait_for_server()

        meta = Deslocar.Goal()
        meta.latitude = 3.0
        meta.longitude = 4.0
        meta.velocidade_latitudinal = 0.5
        meta.velocidade_longitudinal = 0.5

        self.get_logger().info('Enviando meta de deslocamento...')

        futuro_meta = self.cliente.send_goal_async(
            meta,
            feedback_callback=self.receber_feedback
        )

        rclpy.spin_until_future_complete(self, futuro_meta)

        manipulador = futuro_meta.result()

        if manipulador is None or not manipulador.accepted:
            self.get_logger().error('Meta rejeitada pelo servidor.')
            return

        self.get_logger().info('Meta aceita. Aguardando o resultado...')

        futuro_resultado = manipulador.get_result_async()

        rclpy.spin_until_future_complete(self, futuro_resultado)

        resposta = futuro_resultado.result()

        if resposta is not None:
            self.get_logger().info(
                f'Distancia percorrida: '
                f'{resposta.result.distancia_percorrida:.3f}'
            )
            self.get_logger().info(
                f'Status final: {resposta.status}'
            )


def main(args=None):
    rclpy.init(args=args)

    no = RoboDeslocamentoCliente()

    try:
        no.enviar_meta()
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()