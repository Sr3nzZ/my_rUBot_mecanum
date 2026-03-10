import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class WallFollowerHolonomic(Node):

    def __init__(self):
        super().__init__('wall_follower_holonomic_node')

        # Parameters
        self.declare_parameter('distance_limit', 0.5)   # desired wall distance
        self.declare_parameter('forward_speed', 0.20)
        self.declare_parameter('kp', 1.2)               # lateral controller gain
        self.declare_parameter('time_to_stop', 30.0)

        self.base_distance = float(self.get_parameter('distance_limit').value)
        self.v_forward = float(self.get_parameter('forward_speed').value)
        self.kp = float(self.get_parameter('kp').value)
        self.time_to_stop = float(self.get_parameter('time_to_stop').value)

        self.cmd = Twist()

        # ROS entities
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            qos_profile_sensor_data
        )

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timers
        self.cmd_timer = self.create_timer(0.1, self.cmd_publish_timer_cb)
        self.stop_timer = self.create_timer(0.05, self.stop_watchdog)
        self.info_timer = self.create_timer(1.0, self.log_info)

        self._state_action = "Idle"
        self._last_action_logged = None
        self._shutting_down = False

        self.start_time_s = self.get_clock().now().nanoseconds * 1e-9

        self.get_logger().info("Holonomic Wall Follower with proportional control started")

    #--------------------------------------------------------
    def stop_watchdog(self):

        if self._shutting_down:
            return

        now = self.get_clock().now().nanoseconds * 1e-9

        if now - self.start_time_s >= self.time_to_stop:
            self.get_logger().info("Stopping due to timeout")
            self.stop()

    #--------------------------------------------------------
    def stop(self):

        self._shutting_down = True

        self.cmd = Twist()

        try:
            self.publisher.publish(self.cmd)
        except Exception:
            pass

        for t in [self.cmd_timer, self.stop_timer, self.info_timer]:
            try:
                t.cancel()
            except Exception:
                pass

    #--------------------------------------------------------
    def cmd_publish_timer_cb(self):

        if self._shutting_down:
            return

        try:
            self.publisher.publish(self.cmd)
        except Exception:
            pass

    #--------------------------------------------------------
    def laser_callback(self, scan):

        if self._shutting_down:
            return

        angle_min = math.degrees(scan.angle_min)
        angle_inc = math.degrees(scan.angle_increment)

        FRONT = []
        FR_RIGHT = []
        RIGHT = []

        for i, d in enumerate(scan.ranges):

            if not math.isfinite(d):
                continue

            if d < scan.range_min or d > scan.range_max:
                continue

            ang = angle_min + i * angle_inc

            if -20 <= ang <= 20:
                FRONT.append(d)

            elif -70 <= ang < -20:
                FR_RIGHT.append(d)

            elif -110 <= ang < -70:
                RIGHT.append(d)

        min_front = min(FRONT) if FRONT else float('inf')
        min_fr_right = min(FR_RIGHT) if FR_RIGHT else float('inf')
        min_right = min(RIGHT) if RIGHT else float('inf')

        twist = Twist()
        action = ""

        #------------------------------------------------
        # FRONT obstacle -> move LEFT
        #------------------------------------------------
        if min_front < self.base_distance:

            twist.linear.x = 0.0
            twist.linear.y = 0.25
            action = f"FRONT {min_front:.2f} m → move LEFT"

        #------------------------------------------------
        # FRONT RIGHT obstacle -> diagonal FRONT LEFT
        #------------------------------------------------
        elif min_fr_right < self.base_distance:

            twist.linear.x = self.v_forward
            twist.linear.y = 0.25
            action = f"FRONT-RIGHT {min_fr_right:.2f} m → move FRONT-LEFT"

        #------------------------------------------------
        # RIGHT wall -> proportional control
        #------------------------------------------------
        elif math.isfinite(min_right):

            error = min_right - self.base_distance

            vy = -self.kp * error

            # limit lateral speed
            vy = max(min(vy, 0.3), -0.3)

            twist.linear.x = self.v_forward
            twist.linear.y = vy

            action = f"Wall follow | dist={min_right:.2f} error={error:.2f}"

        #------------------------------------------------
        # No wall detected -> search wall
        #------------------------------------------------
        else:

            twist.linear.x = 0.0
            twist.linear.y = -0.2

            action = "Searching wall → move RIGHT"

        self.cmd = twist

        if action != self._last_action_logged:
            self.get_logger().info(action)
            self._last_action_logged = action

        self._state_action = action

    #--------------------------------------------------------
    def log_info(self):

        if not self._shutting_down:
            self.get_logger().info(self._state_action)


def main(args=None):

    rclpy.init(args=args)

    node = WallFollowerHolonomic()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.stop()

    finally:
        try:
            node.destroy_node()
        except Exception:
            pass

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
