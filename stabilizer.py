"""
Using Kalman Filter as a point stabilizer to stabilize a 2D point.
利用卡尔曼滤波器作为点稳定器来稳定二维点。
"""
import numpy as np
import cv2


class Stabilizer:
    """
    Using Kalman filter as a point stabilizer.
    采用卡尔曼滤波器作为点稳定器。
    """

    def __init__(self, state_num=4, measure_num=2, cov_process=0.0001, cov_measure=0.1):
        """Initialization"""
        # Currently we only support scalar and point, so check user input first.
        # 目前我们只支持标量和点，所以首先检查用户输入。
        assert state_num == 4 or state_num == 2, "Only scalar and point supported, Check state_num please."

        # Store the parameters. 存储参数。
        self.state_num = state_num
        self.measure_num = measure_num

        # The filter itself. 过滤器本身。
        # 表示转移矩阵维度为state_num，测量矩阵维度为measure_num， 0表示没有控制向量.
        self.filter = cv2.KalmanFilter(state_num, measure_num, 0)

        # Store the state. 存储状态。
        self.state = np.zeros((state_num, 1), dtype=np.float32)  # 建立shape为（state_num，1）的0矩阵

        # Store the measurement result. 存储测量结果。
        self.measurement = np.array((measure_num, 1), np.float32)  # 存放数组的大小为(measure_num, 1)

        # Store the prediction. 存储预测。
        self.prediction = np.zeros((state_num, 1), np.float32)

        # Kalman parameters setup for scalar. 标量的卡尔曼参数设置。
        if self.measure_num == 1:
            self.filter.transitionMatrix = np.array([[1, 1],
                                                     [0, 1]], np.float32)  # 设置转移矩阵。

            self.filter.measurementMatrix = np.array([[1, 1]], np.float32)  # 设置测量矩阵。

            self.filter.processNoiseCov = np.array([[1, 0],
                                                    [0, 1]], np.float32) * cov_process  # 设置过程噪声协方差矩阵。

            self.filter.measurementNoiseCov = np.array(
                [[1]], np.float32) * cov_measure  # 设置测量噪声协方差矩阵。

        # Kalman parameters setup for point. 点的卡尔曼参数设置。
        if self.measure_num == 2:
            self.filter.transitionMatrix = np.array([[1, 0, 1, 0],
                                                     [0, 1, 0, 1],
                                                     [0, 0, 1, 0],
                                                     [0, 0, 0, 1]], np.float32)

            self.filter.measurementMatrix = np.array([[1, 0, 0, 0],
                                                      [0, 1, 0, 0]], np.float32)

            self.filter.processNoiseCov = np.array([[1, 0, 0, 0],
                                                    [0, 1, 0, 0],
                                                    [0, 0, 1, 0],
                                                    [0, 0, 0, 1]], np.float32) * cov_process

            self.filter.measurementNoiseCov = np.array([[1, 0],
                                                        [0, 1]], np.float32) * cov_measure

    def update(self, measurement):
        """Update the filter"""
        # Make kalman prediction  让卡尔曼预测
        self.prediction = self.filter.predict()

        # Get new measurement  获得新的测量
        if self.measure_num == 1:
            self.measurement = np.array([[np.float32(measurement[0])]])
        else:
            self.measurement = np.array([[np.float32(measurement[0])],
                                         [np.float32(measurement[1])]])

        # Correct according to mesurement
        self.filter.correct(self.measurement)

        # Update state value.
        self.state = self.filter.statePost

    def set_q_r(self, cov_process=0.1, cov_measure=0.001):
        """Set new value for processNoiseCov and measurementNoiseCov."""
        if self.measure_num == 1:
            self.filter.processNoiseCov = np.array([[1, 0],
                                                    [0, 1]], np.float32) * cov_process
            self.filter.measurementNoiseCov = np.array([[1]], np.float32) * cov_measure
        else:
            self.filter.processNoiseCov = np.array([[1, 0, 0, 0],
                                                    [0, 1, 0, 0],
                                                    [0, 0, 1, 0],
                                                    [0, 0, 0, 1]], np.float32) * cov_process
            self.filter.measurementNoiseCov = np.array([[1, 0],
                                                        [0, 1]], np.float32) * cov_measure


def main():
    """Test code"""
    global mp
    mp = np.array((2, 1), np.float32)  # 定义measurement为mp

    def onmouse(k, x, y, s, p):
        global mp
        mp = np.array([[np.float32(x)], [np.float32(y)]])

    cv2.namedWindow("kalman")
    cv2.setMouseCallback("kalman", onmouse)
    kalman = Stabilizer(4, 2)
    frame = np.zeros((480, 640, 3), np.uint8)  # drawing canvas

    while True:
        kalman.update(mp)
        point = kalman.prediction
        state = kalman.filter.statePost
        cv2.circle(frame, (state[0], state[1]), 2, (255, 0, 0), -1)
        cv2.circle(frame, (point[0], point[1]), 2, (0, 255, 0), -1)
        cv2.imshow("kalman", frame)
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break


if __name__ == '__main__':
    main()
