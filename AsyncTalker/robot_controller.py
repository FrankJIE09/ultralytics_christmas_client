import numpy as np
import time


class RobotController:
    def __init__(self, robot_type, connection_params):
        """
        初始化机器人控制器，根据机器人类型初始化对应的客户端。

        :param robot_type: str，机器人类型，例如 'CPS' 或 'EAGE'。
        :param connection_params: dict，连接参数，例如 IP 地址或 URI。
        """
        self.robot_type = robot_type
        if robot_type == "CPS":
            from robot_control.CPS import CPSClient
            self.client = CPSClient()
            self.client.HRIF_Connect(0, connection_params.get("ip", "127.0.0.1"), connection_params.get("port", 10003))
        elif robot_type == "EAGE":
            from robot_control.eage_robot_client import RobotClient
            self.client = RobotClient(connection_params.get("uri", "ws://localhost:12345"))
            self.client.connect()
        else:
            raise ValueError(f"Unsupported robot type: {robot_type}")

    def move_robot(self, target_pose, speed=50, acceleration=500, ucs="Base", radius=0):
        """
        通用机器人运动方法，根据机器人类型调用不同的运动接口。

        :param target_pose: list，目标位置，格式为 [x, y, z, rx, ry, rz]。
        :param speed: int，运动速度。
        :param acceleration: int，加速度。
        :param ucs: str，坐标系。
        :param radius: float，直线运动半径。
        """
        if self.robot_type == "CPS":
            RawACSpoints = []  # 存储关节位置的列表
            status = self.client.HRIF_ReadCmdJointPos(0, 0, RawACSpoints)  # 读取关节位置
            if status == 0:  # 假设0表示读取成功
                RawACSpoints = [float(point) for point in RawACSpoints]  # 将读取的字符串转换为浮点数
            else:
                print(f"读取关节位置失败，错误码: {status}")
                self.client.HRIF_DisConnect(0)  # 读取失败时断开连接并退出
                exit()
            # 调用 CPS 机器人的运动接口
            ret = self.client.HRIF_MoveL(
                0, 0, points=target_pose, RawACSpoints=RawACSpoints[0:6], tcp="TCP", ucs=ucs,
                speed=speed, Acc=acceleration, radius=radius, isSeek=0, bit=0, state=1, cmdID=1
            )
            if ret == 0:
                # 等待运动完成
                while True:
                    motion_done_result = []
                    motion_done = self.client.HRIF_IsMotionDone(0, 0, motion_done_result)
                    if motion_done == 0 and motion_done_result and motion_done_result[0] == 1:
                        print("CPS Robot motion completed.")
                        break
                    elif motion_done < 0:
                        print(f"CPS Robot motion error, code: {motion_done}")
                        break
                    time.sleep(0.01)
            else:
                print(f"CPS Robot motion failed, error code: {ret}")

        elif self.robot_type == "EAGE":
            # 调用 EAGE 机器人的运动接口
            self.client.move_line(
                geom=target_pose, velocity=speed, acceleration=acceleration,
                coord_name=["_Base", "_Flange"], block=True
            )
            print("EAGE Robot motion completed.")

    def disconnect(self):
        """
        断开机器人连接。
        """
        if self.robot_type == "CPS":
            self.client.HRIF_DisConnect(0)
        elif self.robot_type == "EAGE":
            self.client.close()


# 示例使用
if __name__ == "__main__":
    # 使用 CPS 机器人
    cps_controller = RobotController("CPS", {"ip": "192.168.8.23", "port": 10003})
    cps_controller.move_robot([109, 575, 470, -180, 0, 0], speed=50, acceleration=500, ucs="Base", radius=0)
    cps_controller.disconnect()

    # 使用 EAGE 机器人
    # eage_controller = RobotController("EAGE", {"uri": "ws://192.168.1.2:12345"})
    # eage_controller.move_robot([200, 300, 400, 0, 0, 0], speed=75, acceleration=600)
    # eage_controller.disconnect()
