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
        FR_LEFT = []
        RIGHT = []
        LEFT = []
        BACK = []
        BK_RIGHT = []
        BK_LEFT = []

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

            elif  -160 <= ang < -110:
                BK_RIGHT.append(d)
            
            elif abs(ang) > 160:
                BACK.append(d)

            elif 110 < ang <= 160:
                BK_LEFT.append(d)

            elif 70 <= ang <= 110:
                LEFT.append(d)

            elif 20 < ang < 70:
                FR_LEFT.append(d)

        min_front = min(FRONT) if FRONT else float('inf')
        min_fr_right = min(FR_RIGHT) if FR_RIGHT else float('inf')
        min_fr_left = min(FR_LEFT) if FR_LEFT else float('inf')
        min_right = min(RIGHT) if RIGHT else float('inf')
        min_left = min(LEFT) if LEFT else float('inf')
        min_back = min(BACK) if BACK else float('inf')
        min_bk_right = min(BK_RIGHT) if BK_RIGHT else float('inf')
        min_bk_left = min(BK_LEFT) if BK_LEFT else float('inf')


        regions = {
            'front': min_front,
            'fr_right': min_fr_right,
            'fr_left': min_fr_left,
            'right': min_right,
            'left': min_left,
            'back': min_back,
            'bk_right': min_bk_right,
            'bk_left': min_bk_left
        }
        closest_region = min(regions, key=regions.get)
        closest_distance = regions[closest_region]

        twist = Twist()
        action = ""

        #------------------------------------------------
        # Too close to wall
        #------------------------------------------------
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

        #------------------------------------------------
        # Obstacle detected -> react to closest one
        #------------------------------------------------
        if closest_distance < self.base_distance:

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
        
        #------------------------------------------------
        # Far from wall
        #------------------------------------------------
        elif math.isfinite(closest_distance):

            error = closest_distance - self.base_distance

            if closest_region in ['right', 'fr_right', 'bk_right']:
                # Mover solo a la derecha
                twist.linear.x = 0.0
                twist.linear.y = -self.v_forward
                side = 'right'
            elif closest_region in ['left', 'fr_left', 'bk_left']:
                # Mover solo a la izquierda
                twist.linear.x = 0.0
                twist.linear.y = self.v_forward
                side = 'left'
            elif closest_region == 'front':
                # Avanzar
                twist.linear.x = self.v_forward
                twist.linear.y = 0.0
                side = 'front'
            elif closest_region == 'back':
                # Retroceder
                twist.linear.x = -self.v_forward
                twist.linear.y = 0.0
                side = 'back'

            action = f"Too far from wall | side={side} dist={closest_distance:.2f} error={error:.2f}"

        #------------------------------------------------
        # Search for a wall
        #------------------------------------------------
        else:
            twist.linear.x = 0.0
            twist.linear.y = -self.v_forward
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
