import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
                             QToolTip, QMenuBar, QMenu, QAction, QMessageBox, QComboBox, QFrame, QFontDialog)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class RocketSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(800, 600)
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setWindowTitle('Rocket Simulator')

        # Menu bar for theme and font selection
        menu_bar = QMenuBar(self)
        theme_menu = QMenu('Theme', self)
        font_menu = QMenu('Font', self)
        menu_bar.addMenu(theme_menu)
        menu_bar.addMenu(font_menu)

        theme_action_group = QAction('Black', self)
        theme_action_group.triggered.connect(self.set_black_theme)
        theme_menu.addAction(theme_action_group)

        theme_action_group = QAction('White', self)
        theme_action_group.triggered.connect(self.set_white_theme)
        theme_menu.addAction(theme_action_group)

        theme_action_group = QAction('System', self)
        theme_action_group.triggered.connect(self.set_system_theme)
        theme_menu.addAction(theme_action_group)

        font_size_action = QAction('Set Font Size', self)
        font_size_action.triggered.connect(self.set_font_size)
        font_menu.addAction(font_size_action)

        font_style_action = QAction('Set Font Style', self)
        font_style_action.triggered.connect(self.set_font_style)
        font_menu.addAction(font_style_action)

        layout = QVBoxLayout()
        layout.setMenuBar(menu_bar)

        # Frame for rocket parameters
        param_frame = QFrame(self)
        param_frame.setFrameShape(QFrame.Box)
        param_frame.setFrameShadow(QFrame.Raised)
        param_frame.setStyleSheet("background-color: lightgreen;")

        param_layout = QVBoxLayout()
        self.inputs = {}
        params = [
            ("Thrust (N)", "Force produced by the rocket engines. Example: 20000."),
            ("Gravity (m/s^2)", "Acceleration due to gravity. Example: 9.81 for Earth."),
            ("Dry Mass (kg)", "Mass of the rocket without fuel. Example: 800."),
            ("Wet Mass (kg)", "Mass of the rocket with fuel. Example: 1500."),
            ("Length (m)", "Length of the rocket. Example: 10."),
            ("Diameter (m)", "Diameter of the rocket. Example: 1."),
            ("Material", "Material of the rocket. Example: Aluminum."),
            ("Specific Impulse (s)", "Specific impulse of the rocket engine. Example: 300."),
            ("Launch Angle (degrees)", "Angle of launch. Example: 45."),
            ("Avionics Weight (kg)", "Weight of the avionics. Example: 50."),
            ("Initial Velocity (m/s)", "Initial velocity of the rocket. Example: 0."),
            ("Initial Acceleration (m/s^2)", "Initial acceleration of the rocket. Example: 0."),
            ("Wind Speed (m/s)", "Speed of the wind. Example: 5."),
            ("Temperature (C)", "Ambient temperature. Example: 20."),
            ("Humidity (%)", "Relative humidity. Example: 50."),
        ]

        for param, tooltip in params:
            hbox = QHBoxLayout()
            label = QLabel(param)
            line_edit = QLineEdit()
            line_edit.setToolTip(tooltip)
            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            param_layout.addLayout(hbox)
            self.inputs[param] = line_edit

        param_frame.setLayout(param_layout)
        layout.addWidget(param_frame)

        # Add a button to run the simulation
        self.run_button = QPushButton("Run Simulation", self)
        self.run_button.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_button)

        # Add a dropdown for graph type selection
        self.graph_type_combo = QComboBox(self)
        self.graph_type_combo.addItems(["Altitude vs Time", "Velocity vs Time", "Acceleration vs Time", "3D Trajectory"])
        layout.addWidget(self.graph_type_combo)

        self.setLayout(layout)
        self.show()

    def set_black_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def set_white_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, Qt.white)
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, Qt.white)
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def set_system_theme(self):
        self.setPalette(self.style().standardPalette())

    def set_font_size(self):
        font, ok = QFontDialog.getFont(self.font(), self, "Select Font Size")
        if ok:
            self.setFont(font)

    def set_font_style(self):
        font, ok = QFontDialog.getFont(self.font(), self, "Select Font Style")
        if ok:
            self.setFont(font)

    def run_simulation(self):
        # Extract values from input fields
        try:
            Thrust = float(self.inputs["Thrust (N)"].text())
            G = float(self.inputs["Gravity (m/s^2)"].text())
            dry_mass = float(self.inputs["Dry Mass (kg)"].text())
            wet_mass = float(self.inputs["Wet Mass (kg)"].text())
            length = float(self.inputs["Length (m)"].text())
            diameter = float(self.inputs["Diameter (m)"].text())
            material = self.inputs["Material"].text()
            specific_impulse = float(self.inputs["Specific Impulse (s)"].text())
            launch_angle = float(self.inputs["Launch Angle (degrees)"].text())
            avionics_weight = float(self.inputs["Avionics Weight (kg)"].text())
            initial_velocity = float(self.inputs["Initial Velocity (m/s)"].text())
            initial_acceleration = float(self.inputs["Initial Acceleration (m/s^2)"].text())
            wind_speed = float(self.inputs["Wind Speed (m/s)"].text())
            temperature = float(self.inputs["Temperature (C)"].text())
            humidity = float(self.inputs["Humidity (%)"].text())
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numerical values")
            return

        graph_type = self.graph_type_combo.currentText()
        simulate_rocket(Thrust, G, dry_mass, wet_mass, length, diameter, material, specific_impulse, launch_angle, avionics_weight, initial_velocity, initial_acceleration, wind_speed, temperature, humidity, graph_type)

def simulate_rocket(Thrust, G, dry_mass, wet_mass, length, diameter, material, specific_impulse, launch_angle, avionics_weight, initial_velocity, initial_acceleration, wind_speed, temperature, humidity, graph_type):
    # Simulation parameters
    burn_time = 50  # Example value, adjust as needed
    dt = 0.1       # Example value, adjust as needed
    Cd = 0.5       # Example value, adjust as needed
    A = np.pi * (diameter / 2) ** 2
    rho = 1.225    # Air density at sea level in kg/m^3

    # Functions to calculate forces
    def thrust(t):
        return Thrust if t <= burn_time else 0

    def drag(v):
        if np.linalg.norm(v) == 0:
            return np.array([0.0, 0.0, 0.0])
        return 0.5 * Cd * A * rho * np.linalg.norm(v) ** 2 * -v / np.linalg.norm(v)

    def mass(t):
        if t <= burn_time:
            return wet_mass - (wet_mass - dry_mass) * (t / burn_time)
        else:
            return dry_mass

    # Initial conditions
    v = np.array([0.0, 0.0, initial_velocity])  # velocity in 3D (vx, vy, vz)
    r = np.array([0.0, 0.0, 0.0])  # position in 3D (x, y, z)
    angle = np.radians(launch_angle)   # launch angle in degrees

    # Apply launch angle to initial thrust direction
    thrust_direction = np.array([np.cos(angle), 0, np.sin(angle)])

    # Lists to store simulation data
    time = np.arange(0, 200, dt)
    positions = np.zeros((len(time), 3))  # store (x, y, z) positions
    velocities = np.zeros((len(time), 3))  # store (vx, vy, vz) velocities
    accelerations = np.zeros((len(time), 3))  # store (ax, ay, az) accelerations

    # Define the RK4 method for updating position and velocity
    def rk4_step(f, y, t, dt):
        k1 = f(y, t)
        k2 = f(y + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = f(y + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = f(y + dt * k3, t + dt)
        return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    # Define the function to calculate the derivatives
    def derivatives(y, t):
        r, v = y[:3], y[3:]
        m = mass(t)
        F_thrust = thrust(t) * thrust_direction
        F_drag = drag(v)
        F_gravity = np.array([0, 0, -m * G])
        F_net = F_thrust + F_drag + F_gravity
        a = F_net / m
        return np.concatenate((v, a))

    # Initial state vector [r0, v0]
    y = np.concatenate((r, v))

    # Simulation loop
    for i in range(1, len(time)):
        t = time[i]
        y = rk4_step(derivatives, y, t, dt)
        positions[i], velocities[i] = y[:3], y[3:]
        accelerations[i] = derivatives(y, t)[3:]

    # Plotting results
    if graph_type == "3D Trajectory":
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2])
        ax.set_title('3D Rocket Trajectory')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
    elif graph_type == "Altitude vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, positions[:, 2])  # Plot Z position over time
        plt.title('Altitude vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Altitude (m)')
    elif graph_type == "Velocity vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, np.linalg.norm(velocities, axis=1))  # Plot magnitude of velocity over time
        plt.title('Velocity vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (m/s)')
    elif graph_type == "Acceleration vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, np.linalg.norm(accelerations, axis=1))  # Plot magnitude of acceleration over time
        plt.title('Acceleration vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (m/s^2)')

    plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RocketSimulator()
    sys.exit(app.exec_())
