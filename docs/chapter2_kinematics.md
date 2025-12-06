# Chapter 2: Robotics Basics: Kinematics, Dynamics, and Control

## Introduction to Robotics Fundamentals

To understand how a physical AI system can interact with the world, we must first understand the fundamental principles governing its body—the robot. This chapter delves into the three core pillars of robotics: kinematics, dynamics, and control. **Kinematics** addresses the geometry of motion, describing the robot's position and orientation without considering the forces that cause it. **Dynamics**, on the other hand, models the relationship between forces, torques, and the resulting motion. Finally, **Control** theory provides the tools to generate the necessary motor commands to achieve a desired state or trajectory, bridging the gap between desired actions and physical execution.

## Robot Kinematics: The Geometry of Motion

Kinematics is concerned with the question: "Where is the robot's end-effector (e.g., its hand or gripper) given a set of joint angles?" and its inverse, "What joint angles are needed to place the end-effector at a desired location?"

### Forward Kinematics: From Joints to Space

Forward kinematics calculates the position and orientation of the robot's end-effector from its joint parameters (e.g., angles for revolute joints, displacement for prismatic joints). The most common method for this is the Denavit-Hartenberg (D-H) convention, which establishes a coordinate frame for each link and defines a transformation matrix between consecutive frames.

The transformation from frame `i-1` to frame `i` is represented by a homogeneous transformation matrix, $A_i$, which is a product of four basic transformations:

$$
 A_i = \text{Rot}_z(\theta_i) \cdot \text{Trans}_z(d_i) \cdot \text{Trans}_x(a_i) \cdot \text{Rot}_x(\alpha_i) 
$$

Where:
- $\theta_i$ is the joint angle.
- $d_i$ is the link offset.
- $a_i$ is the link length.
- $\alpha_i$ is the link twist.

To find the final position and orientation of the end-effector (frame $n$) relative to the base (frame $0$), we chain these matrices together:

$$ T^0_n = A_1 A_2 \cdots A_n $$

This final matrix $T^0_n$ contains both the rotation matrix describing the end-effector's orientation and the position vector describing its location in space.

### Inverse Kinematics: From Space to Joints

Inverse kinematics (IK) is the reverse problem: given a desired position and orientation for the end-effector, what are the corresponding joint angles? This is a much harder problem because the equations are non-linear, and multiple solutions (or no solution) can exist. For a simple 2-link planar arm, the solution can be found analytically using trigonometry. However, for complex, high-degree-of-freedom robots, numerical methods are often required.

One common numerical approach uses the Jacobian matrix, $J$, which relates joint velocities ($\dot{q}$) to the end-effector's linear and angular velocities ($\dot{x}$):

$$ \dot{x} = J(q)\dot{q} $$

By inverting or pseudo-inverting this matrix, we can iteratively solve for the joint angles that move the end-effector toward the desired target.

## Robot Dynamics: The Physics of Motion

While kinematics describes motion, dynamics explains why that motion occurs. It models the forces and torques required to produce the desired accelerations of the robot's links, accounting for mass, inertia, gravity, and friction.

### The Newton-Euler Formulation

The Newton-Euler method is a powerful, iterative algorithm for computing the dynamics of a robotic manipulator. It consists of two main passes:

1.  **Forward (Outward) Iteration**: Starting from the base and moving to the end-effector, this pass calculates the velocity and acceleration of each link based on the state of the previous link.
    -   Angular velocity of link $i+1$: $\omega_{i+1}$
    -   Angular acceleration of link $i+1$: $\dot{\omega}_{i+1}$
    -   Linear acceleration of link $i+1$: $\dot{v}_{i+1}$

2.  **Backward (Inward) Iteration**: Starting from the end-effector and moving to the base, this pass calculates the forces and torques acting on each link.
    -   The force $f_i$ and torque $\tau_i$ exerted on link $i$ by link $i-1$ are calculated based on the forces and torques propagated from the outer link ($i+1$) and the link's own inertial properties.

The final result of the backward iteration is the set of joint torques ($\tau$) required to achieve the specified motion, which is the crucial output needed for the control system.

## Robot Control: Making Robots Behave

The control system's job is to take the desired state (from a motion planner) and the current state (from sensors) and compute the necessary joint torques to minimize the difference between them.

### PID Control: The Workhorse of Robotics

The Proportional-Integral-Derivative (PID) controller is one of the most widely used control algorithms in robotics due to its simplicity and effectiveness. It calculates the control output based on three terms:

1.  **Proportional (P) Term**: This term provides a control action proportional to the current error $e(t)$, where $e(t) = \text{desired\_position} - \text{current\_position}$. It provides the immediate response to an error.
    $$ u_p(t) = K_p e(t) $$

2.  **Integral (I) Term**: This term accumulates past errors. It is designed to eliminate steady-state error by increasing the control effort as long as an error persists.
    $$ u_i(t) = K_i \int_0^t e(\tau)d\tau $$

3.  **Derivative (D) Term**: This term acts on the rate of change of the error. It has a damping effect, helping to reduce overshoot and oscillations by "predicting" the future error.
    $$ u_d(t) = K_d \frac{de(t)}{dt} $$

The complete PID control law combines these three actions to calculate the final control output (e.g., motor torque or voltage):

$$ u(t) = K_p e(t) + K_i \int_0^t e(\tau)d\tau + K_d \frac{de(t)}{dt} $$

By tuning the gains ($K_p$, $K_i$, $K_d$), a PID controller can be configured to provide a fast, stable, and accurate response for a wide range of robotic systems.
