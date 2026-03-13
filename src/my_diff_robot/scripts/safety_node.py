#!/usr/bin/env python3
import copy
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
from rclpy.executors import ExternalShutdownException
class SafetyController(Node):
    def __init__(self):
        super().__init__('safety_controller')

       
        self.stop_distance = 0.5          
        self.slow_distance_margin = 0.6   
        self.publish_hz = 20.0            

        
        self.latest_cmd = TwistStamped()
        self.min_front = float('inf')     
        self.min_rear = float('inf')      
        self.got_scan = False

        
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(TwistStamped, '/teleop_cmd_vel', self.cmd_callback, 10)
        self.cmd_pub = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)

        
        self.create_timer(1.0 / self.publish_hz, self._on_timer)

        self.get_logger().info('SafetyController ready (Directional collision avoidance active)')

    def cmd_callback(self, msg: TwistStamped):
        self.latest_cmd = msg

    def scan_callback(self, scan: LaserScan):
        if not hasattr(scan, 'ranges') or not scan.ranges:
            return

        angle_min = scan.angle_min
        angle_inc = scan.angle_increment

        mf = float('inf')
        mr = float('inf')

        for i, r in enumerate(scan.ranges):
            
            if not math.isfinite(r) or r <= 0.05:
                continue

            angle = angle_min + i * angle_inc
            
            angle = (angle + math.pi) % (2 * math.pi) - math.pi

            
            if -math.pi/2 <= angle <= math.pi/2:
                if r < mf: mf = r
            else:
                if r < mr: mr = r

        self.min_front = mf
        self.min_rear = mr
        self.got_scan = True

    def _on_timer(self):
        if not self.got_scan:
            return

        safe_cmd = copy.deepcopy(self.latest_cmd)
        v_cmd = safe_cmd.twist.linear.x

        
        if v_cmd > 0.0:
            md = self.min_front
            direction = "FRONT"
        elif v_cmd < 0.0:
            md = self.min_rear
            direction = "REAR"
        else:
            
            md = float('inf')
            direction = "NONE"

        slow_dist = self.stop_distance + self.slow_distance_margin

        
        if md <= self.stop_distance and v_cmd != 0.0:
            safe_cmd.twist.linear.x = 0.0
            self.get_logger().warn(f'STOP (hard) — Obstacle in {direction} at {md:.3f}m (<= {self.stop_distance}m)', throttle_duration_sec=0.5)
        
        elif md <= slow_dist and v_cmd != 0.0:
            
            scale = (md - self.stop_distance) / (slow_dist - self.stop_distance)
            safe_cmd.twist.linear.x = v_cmd * scale
            self.get_logger().info(f'Brake — {direction} md={md:.3f}m, scale={scale:.2f}', throttle_duration_sec=0.5)

        
        safe_cmd.header.stamp = self.get_clock().now().to_msg()
        self.cmd_pub.publish(safe_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SafetyController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
       
        if rclpy.ok():
           rclpy.shutdown()

if __name__ == '__main__':
    main()