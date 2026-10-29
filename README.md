# ROS 2 — Avaliação 1

**Integrantes:**
- Aretuza Raquely de Oliveira Costa
- Pedro Ricardo Fernandes de Melo

Repositório desenvolvido para a avaliação prática de ROS 2, com implementações em Python e interfaces personalizadas.

## Conteúdo

- `robo_interfaces`: interfaces de mensagens, serviços e ações.
- `robo_explorador`: nós publicadores, assinantes, clientes e servidores.

## Execução

No workspace ROS 2, execute os comandos:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --packages-up-to robo_explorador
source /home/aluno/ros2_ws/install/setup.bash
```
ou para apenas um pacote específico, sem compilar suas dependencias:
```bash
colcon build --packages-select robo_explorador
```

Os nós podem ser executados com `ros2 run`, conforme cada questão da avaliação.
