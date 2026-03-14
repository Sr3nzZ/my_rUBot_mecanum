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
        self.declare_parameter('distance_limit', 0.35)   # desired wall distance
        self.declare_parameter('forward_speed', 0.20)
        self.declare_parameter('kp', 1.2)               # lateral controller gain
        self.declare_parameter('time_to_stop', 30.0)
        self.declare_parameter('time_to_turn', 5.0)     # time to turn if wall is too long

        self.base_distance = float(self.get_parameter('distance_limit').value)
        self.v_forward = float(self.get_parameter('forward_speed').value)
        self.kp = float(self.get_parameter('kp').value)
        self.time_to_stop = float(self.get_parameter('time_to_stop').value)
        self.time_to_turn = float(self.get_parameter('time_to_turn').value)

        self.cmd = Twist()
        self.right_wall_front_time = 0.0  # timer to turn if wall is too long

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

        #--------------------------------------------------------
        # Define regions by angle ranges
        #--------------------------------------------------------
        regions_def = {
            'front': (-20, 20),
            'fr_right': (-70, -20),
            'fr_left': (20, 70),
            'right': (-110, -70),
            'left': (70, 110),
            'bk_right': (-160, -110),
            'bk_left': (110, 160),
            'back': (160, 180)
        }

        # Initialize minimum distances dictionary
        regions = {key: float('inf') for key in regions_def}

        #--------------------------------------------------------
        # Process each LIDAR measurement
        #--------------------------------------------------------
        for i, d in enumerate(scan.ranges):

            if not math.isfinite(d) or d < scan.range_min or d > scan.range_max:
                continue

            ang = angle_min + i * angle_inc

            for region, (start, end) in regions_def.items():
                # Negative back
                if region == 'back' and (ang > 160 or ang < -160):
                    regions[region] = min(regions[region], d)
                elif start <= ang <= end:
                    regions[region] = min(regions[region], d)

        closest_region = min(regions, key=regions.get)
        closest_distance = regions[closest_region]

        twist = Twist()
        action = ""

        #--------------------------------------------------------
        # Too close to wall
        #--------------------------------------------------------
        if closest_distance < self.base_distance - 0.10:
            
            if closest_region in ['front', 'fr_right', 'fr_left']:
                twist.linear.x = -self.v_forward
                twist.linear.y = 0.0
                action = f"Too close to FRONT → move BACK"

            elif closest_region in ['right', 'bk_right']:
                twist.linear.x = 0.0
                twist.linear.y = self.v_forward
                action = f"Too close to RIGHT → move LEFT"

            elif closest_region in ['left', 'bk_left']:
                twist.linear.x = 0.0
                twist.linear.y = -self.v_forward
                action = f"Too close to LEFT → move RIGHT"

            elif closest_region == 'back':
                twist.linear.x = self.v_forward
                twist.linear.y = 0.0
                action = f"Too close to BACK → move front"

        #--------------------------------------------------------
        # Obstacle detected -> react to closest one
        #--------------------------------------------------------
        elif closest_distance < self.base_distance:

            if closest_region == "front":
                twist.linear.x = 0.0
                twist.linear.y = self.v_forward
                action = f"FRONT {closest_distance:.2f}m -> Move left"

            elif closest_region == "left":
                twist.linear.x = -self.v_forward
                twist.linear.y = 0.0
                action = f"LEFT {closest_distance:.2f} m → move BACK"

            elif closest_region == "back":
                twist.linear.x = 0.0
                twist.linear.y = -self.v_forward
                action = f"BACK {closest_distance:.2f} m → move RIGHT"

            elif closest_region == "bk_right":
                twist.linear.x = self.v_forward
                twist.linear.y = -self.v_forward
                action = f"BACK-RIGHT {closest_distance:.2f} m → move FRONT-RIGHT"

            elif closest_region == "bk_left":
                twist.linear.x = -self.v_forward
                twist.linear.y = -self.v_forward
                action = f"BACK-LEFT {closest_distance:.2f} m → move BACK-RIGHT"

            elif closest_region == "fr_right":
                twist.linear.x = self.v_forward
                twist.linear.y = self.v_forward
                action = f"FRONT-RIGHT {closest_distance:.2f} m → move FRONT-LEFT"

            elif closest_region == "fr_left":
                twist.linear.x = -self.v_forward
                twist.linear.y = self.v_forward
                action = f"FRONT-LEFT {closest_distance:.2f} m → move BACK-LEFT"

            elif closest_region == "right":
                twist.linear.x = self.v_forward
                twist.linear.y = 0.0
                action = f"RIGHT {closest_distance:.2f} m → move FRONT"

        #--------------------------------------------------------
        # Far from wall
        #--------------------------------------------------------
        elif math.isfinite(closest_distance):

            error = closest_distance - self.base_distance

            if closest_region in ['right', 'fr_right', 'bk_right']:
                twist.linear.x = 0.0
                twist.linear.y = -self.v_forward
                side = 'right'
            elif closest_region in ['left', 'fr_left', 'bk_left']:
                twist.linear.x = 0.0
                twist.linear.y = self.v_forward
                side = 'left'
            elif closest_region == 'front':
                twist.linear.x = self.v_forward
                twist.linear.y = 0.0
                side = 'front'
            elif closest_region == 'back':
                twist.linear.x = -self.v_forward
                twist.linear.y = 0.0
                side = 'back'

            action = f"Too far from wall | side={side} dist={closest_distance:.2f} error={error:.2f}"

        #--------------------------------------------------------
        # Search for a wall
        #--------------------------------------------------------
        else:
            twist.linear.x = 0.0
            twist.linear.y = -self.v_forward
            action = "Searching wall → move RIGHT"

        #--------------------------------------------------------
        # Turn 90º right if right wall is too long
        #--------------------------------------------------------
        dt = 0.1 
        if closest_region in ['right', 'fr_right', 'bk_right'] and regions['front'] > self.base_distance:
            self.right_wall_front_time += dt
            if self.right_wall_front_time >= self.time_to_turn:
                # Turn right 90º
                twist.linear.x = 0.0
                twist.linear.y = 0.0
                twist.angular.z = -math.pi / 2
                action = f"Turning right 90° after {self.time_to_turn}s following wall"
                self.right_wall_front_time = 0.0
        else:
            self.right_wall_front_time = 0.0

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
