import time

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from robo_interfaces.action import Deslocar


class RoboDeslocamentoClienteCancelar(Node):

    def __init__(self):
        super().__init__('robo_deslocamento_cliente_cancelar')

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

    def enviar_meta_e_cancelar(self):
        self.cliente.wait_for_server()

        meta = Deslocar.Goal()
        meta.latitude = 10.0
        meta.longitude = 10.0
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

        self.get_logger().info(
            'Meta aceita. O cancelamento sera solicitado em 5 segundos.'
        )

        futuro_resultado = manipulador.get_result_async()

        instante_inicial = time.monotonic()

        while (
            time.monotonic() - instante_inicial < 5.0
            and not futuro_resultado.done()
        ):
            rclpy.spin_once(self, timeout_sec=0.1)

        if futuro_resultado.done():
            resposta = futuro_resultado.result()

            if resposta is not None:
                self.get_logger().info(
                    'A acao terminou antes do cancelamento. '
                    f'Distancia: {resposta.result.distancia_percorrida:.3f}'
                )
            return

        self.get_logger().info('Solicitando cancelamento...')

        futuro_cancelamento = manipulador.cancel_goal_async()
        rclpy.spin_until_future_complete(self, futuro_cancelamento)

        resposta_cancelamento = futuro_cancelamento.result()

        if (
            resposta_cancelamento is None
            or not resposta_cancelamento.goals_canceling
        ):
            self.get_logger().error(
                'O servidor nao confirmou o cancelamento.'
            )

        rclpy.spin_until_future_complete(self, futuro_resultado)

        resposta = futuro_resultado.result()

        if resposta is not None:
            self.get_logger().info(
                f'Distancia percorrida ate o fim: '
                f'{resposta.result.distancia_percorrida:.3f}'
            )
            self.get_logger().info(
                f'Status final: {resposta.status}'
            )


def main(args=None):
    rclpy.init(args=args)

    no = RoboDeslocamentoClienteCancelar()

    try:
        no.enviar_meta_e_cancelar()
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()