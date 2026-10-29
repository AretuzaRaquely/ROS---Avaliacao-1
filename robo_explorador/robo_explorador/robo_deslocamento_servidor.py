
import asyncio
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.task import Future

from robo_interfaces.action import Deslocar


class RoboDeslocamentoServidor(Node):

    def __init__(self):
        super().__init__('robo_deslocamento_servidor')

        # Posicao inicial simulada do robo
        self.latitude_atual = 0.0
        self.longitude_atual = 0.0

        # Cria o servidor da acao
        self.servidor = ActionServer(
            self,
            Deslocar,
            'deslocar_robo',
            execute_callback=self.executar_deslocamento,
            goal_callback=self.aceitar_meta,
            cancel_callback=self.aceitar_cancelamento
        )

        self.get_logger().info(
            'Servidor da acao deslocar_robo iniciado.'
        )

    def aceitar_meta(self, meta):
        # Rejeita metas que nao representam deslocamento
        if (
            meta.latitude == self.latitude_atual
            and meta.longitude == self.longitude_atual
        ):
            self.get_logger().info(
                'Meta rejeitada: o robo ja esta nessa localizacao.'
            )
            return GoalResponse.REJECT

        # As velocidades devem ser positivas
        if (
            meta.velocidade_latitudinal <= 0.0
            or meta.velocidade_longitudinal <= 0.0
        ):
            self.get_logger().info(
                'Meta rejeitada: as velocidades devem ser positivas.'
            )
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def aceitar_cancelamento(self, goal_handle):
        self.get_logger().info('Cancelamento solicitado.')
        return CancelResponse.ACCEPT

    async def aguardar_um_segundo(self):
        # Aguarda sem bloquear o processamento dos eventos do ROS
        futuro = Future()

        temporizador = self.create_timer(
            1.0,
            lambda: (
                futuro.set_result(True)
                if not futuro.done()
                else None
            )
        )

        try:
            await futuro
        finally:
            temporizador.cancel()
            self.destroy_timer(temporizador)

    async def executar_deslocamento(self, goal_handle):
        meta = goal_handle.request

        resultado = Deslocar.Result()
        feedback = Deslocar.Feedback()

        distancia_total = 0.0

        while True:
            # Verifica se o cliente solicitou cancelamento
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()

                resultado.distancia_percorrida = distancia_total

                self.get_logger().info(
                    'Acao cancelada. '
                    f'Distancia percorrida: {distancia_total:.3f}'
                )

                return resultado

            # Calcula a diferenca entre a posicao atual e o destino
            diferenca_lat = meta.latitude - self.latitude_atual
            diferenca_lon = meta.longitude - self.longitude_atual

            # Encerra quando o destino for alcancado
            if diferenca_lat == 0.0 and diferenca_lon == 0.0:
                break

            # Calcula o deslocamento deste segundo, sem ultrapassar o destino
            deslocamento_lat = math.copysign(
                min(
                    abs(diferenca_lat),
                    meta.velocidade_latitudinal
                ),
                diferenca_lat
            )

            deslocamento_lon = math.copysign(
                min(
                    abs(diferenca_lon),
                    meta.velocidade_longitudinal
                ),
                diferenca_lon
            )

            # Atualiza a posicao simulada
            self.latitude_atual += deslocamento_lat
            self.longitude_atual += deslocamento_lon

            # Soma a distancia percorrida neste intervalo
            distancia_total += math.hypot(
                deslocamento_lat,
                deslocamento_lon
            )

            # Publica o feedback com a posicao atual
            feedback.latitude_atual = self.latitude_atual
            feedback.longitude_atual = self.longitude_atual

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Posicao atual: '
                f'latitude={self.latitude_atual:.2f}, '
                f'longitude={self.longitude_atual:.2f}'
            )

            # Aguarda um segundo antes da proxima atualizacao
            await self.aguardar_um_segundo()

        # Informa que a acao foi concluida com sucesso
        goal_handle.succeed()

        resultado.distancia_percorrida = distancia_total

        self.get_logger().info(
            'Deslocamento concluido. '
            f'Distancia percorrida: {distancia_total:.3f}'
        )

        return resultado


def main(args=None):
    rclpy.init(args=args)

    no = RoboDeslocamentoServidor()

    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
