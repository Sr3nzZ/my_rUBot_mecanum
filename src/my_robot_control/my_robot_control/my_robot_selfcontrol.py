import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
import math


class RobotSelfControl(Node):

    def __init__(self):
        super().__init__('robot_selfcontrol_node')

        # Configurable parameters
        self.declare_parameter('distance_limit', 0.3)
        self.declare_parameter('speed_factor', 1.0)
        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('rotation_speed', 0.3)
        self.declare_parameter('time_to_stop', 5.0)

        self._distanceLimit = self.get_parameter('distance_limit').value
        self._speedFactor = self.get_parameter('speed_factor').value
        self._forwardSpeed = self.get_parameter('forward_speed').value
        self._rotationSpeed = self.get_parameter('rotation_speed').value
        self._time_to_stop = self.get_parameter('time_to_stop').value

        self._msg = Twist()
        self._msg.linear.x = self._forwardSpeed * self._speedFactor
        self._msg.angular.z = 0.0

        self._cmdVel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.05, self.timer_callback)

        # QoS optimized for LIDAR
        scan_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            scan_qos
        )

        self.start_time = self.get_clock().now().nanoseconds * 1e-9
        self._shutting_down = False
        self._last_info_time = self.start_time
        self._last_speed_time = self.start_time

    def timer_callback(self):
        if self._shutting_down:
            return

        now_sec = self.get_clock().now().nanoseconds * 1e-9
        elapsed_time = now_sec - self.start_time

        self._cmdVel.publish(self._msg)

        if now_sec - self._last_speed_time >= 1:
            self.get_logger().info(
                f"Vx: {self._msg.linear.x:.2f} m/s, "
                f"w: {self._msg.angular.z:.2f} rad/s | "
                f"Time: {elapsed_time:.1f}s"
            )
            self._last_speed_time = now_sec

        if elapsed_time >= self._time_to_stop:
            self.timer.cancel()
            self.stop()
            self.get_logger().info("Robot stopped")
            return

    def laser_callback(self, scan):

        if self._shutting_down:
            return

        angle_min_deg = math.degrees(scan.angle_min)
        angle_inc_deg = math.degrees(scan.angle_increment)

        closest_distance = float("inf")
        angle_closest = 0.0

        for i, distance in enumerate(scan.ranges):

            if math.isfinite(distance) and \
               scan.range_min < distance < scan.range_max:

                angle_deg = angle_min_deg + i * angle_inc_deg

                if distance < closest_distance:
                    closest_distance = distance
                    angle_closest = angle_deg

        if closest_distance == float("inf"):
            return

        # Determine zone
        if -45 <= angle_closest <= 45:
            zone = "FRONT"
        elif 45 < angle_closest <= 110:
            zone = "LEFT"
        elif -110 <= angle_closest < -45:
            zone = "RIGHT"
        elif 110 < angle_closest <= 180:
            zone = "BACK_LEFT"
        elif -180 <= angle_closest < -110:
            zone = "BACK_RIGHT"
        else:
            zone = "BACK"

        # React to obstacle
        if closest_distance < self._distanceLimit:
            if zone == "FRONT":
                self._msg.linear.x = -self._forwardSpeed * self._speedFactor
                self._msg.angular.z = self._rotationSpeed * self._speedFactor
            elif zone == "LEFT":
                self._msg.linear.x = -self._forwardSpeed * self._speedFactor
                self._msg.angular.z = -self._rotationSpeed * self._speedFactor
            elif zone == "RIGHT":
                self._msg.linear.x = -self._forwardSpeed * self._speedFactor
                self._msg.angular.z = self._rotationSpeed * self._speedFactor
            elif zone in ["BACK_LEFT", "BACK_RIGHT"]:
                self._msg.linear.x = self._forwardSpeed * self._speedFactor
                self._msg.angular.z = 0.0
            else:
                self._msg.linear.x = self._forwardSpeed * self._speedFactor
                self._msg.angular.z = 0.0
        else:
            self._msg.linear.x = self._forwardSpeed * self._speedFactor
            self._msg.angular.z = 0.0

    def stop(self):
        self._shutting_down = True
        stop_msg = Twist()
        self._cmdVel.publish(stop_msg)


def main(args=None):
    rclpy.init(args=args)
    robot = RobotSelfControl()

    try:
        rclpy.spin(robot)
    except KeyboardInterrupt:
        pass
    finally:
        # Safety: publish stop once on exit
        try:
            robot._cmdVel.publish(Twist())
        except Exception:
            pass

        robot.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()