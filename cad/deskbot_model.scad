// ==============================================================================
// DESKBOT — Cute 3D Desktop Companion Robot CAD Model
// OpenSCAD Parametric Design
// Designed for 3D Printing (FDM / SLA) — PLA or PETG
// ==============================================================================

$fn = 60; // Smooth curves

// ------------------------------------------------------------------------------
// GLOBAL PARAMETERS & DIMENSIONS (in mm)
// ------------------------------------------------------------------------------
WALL_THICKNESS = 2.4;
TOLERANCE = 0.3; // 3D printing clearance

// Head Dimensions
HEAD_WIDTH = 68;
HEAD_HEIGHT = 54;
HEAD_DEPTH = 50;
HEAD_CORNER_RADIUS = 10;

// OLED Display (Standard 0.96" I2C SSD1306)
OLED_PCB_W = 27.5;
OLED_PCB_H = 27.8;
OLED_SCREEN_W = 24.5;
OLED_SCREEN_H = 13.0;

// Body Dimensions
BODY_WIDTH = 58;
BODY_HEIGHT = 44;
BODY_DEPTH = 48;
BODY_CORNER_RADIUS = 8;

// SG90 Micro Servo Dimensions
SERVO_L = 23.0;
SERVO_W = 12.2;
SERVO_H = 22.8;

// Arduino Nano ESP32 Dimensions
MCU_L = 45.0;
MCU_W = 18.0;
MCU_H = 8.0;

// Base Dimensions
BASE_DIA = 74;
BASE_HEIGHT = 8;


// ------------------------------------------------------------------------------
// HELPER MODULE: Rounded Box
// ------------------------------------------------------------------------------
module rounded_box(w, h, d, r) {
    hull() {
        translate([r, r, r]) sphere(r=r);
        translate([w - r, r, r]) sphere(r=r);
        translate([r, h - r, r]) sphere(r=r);
        translate([w - r, h - r, r]) sphere(r=r);
        translate([r, r, d - r]) sphere(r=r);
        translate([w - r, r, d - r]) sphere(r=r);
        translate([r, h - r, d - r]) sphere(r=r);
        translate([w - r, h - r, d - r]) sphere(r=r);
    }
}


// ------------------------------------------------------------------------------
// MODULE 1: Cute Robot Head Shell
// ------------------------------------------------------------------------------
module robot_head() {
    difference() {
        // Outer rounded head casing
        rounded_box(HEAD_WIDTH, HEAD_HEIGHT, HEAD_DEPTH, HEAD_CORNER_RADIUS);

        // Hollow interior for electronics
        translate([WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS])
            rounded_box(
                HEAD_WIDTH - 2 * WALL_THICKNESS,
                HEAD_HEIGHT - 2 * WALL_THICKNESS,
                HEAD_DEPTH - 2 * WALL_THICKNESS,
                HEAD_CORNER_RADIUS - 1.5
            );

        // Front Face Display Window (for OLED eyes)
        translate([
            (HEAD_WIDTH - OLED_SCREEN_W) / 2,
            -1,
            (HEAD_HEIGHT - OLED_SCREEN_H) / 2 + 2
        ])
            cube([OLED_SCREEN_W, WALL_THICKNESS + 2, OLED_SCREEN_H]);

        // Front Microphone Hole (2.5mm hole for INMP441 mic)
        translate([HEAD_WIDTH / 2, -1, 10])
            rotate([-90, 0, 0])
                cylinder(r=1.25, h=WALL_THICKNESS + 2);

        // Bottom Neck Pivot Opening (for tilt bracket)
        translate([HEAD_WIDTH / 2, HEAD_DEPTH / 2, -1])
            cylinder(r=8, h=WALL_THICKNESS + 2);
    }

    // Cute Ears / Antennas (Left and Right)
    translate([-4, HEAD_HEIGHT / 2, HEAD_DEPTH / 2])
        rotate([0, 90, 0])
            cylinder(r1=6, r2=4, h=5);

    translate([HEAD_WIDTH - 1, HEAD_HEIGHT / 2, HEAD_DEPTH / 2])
        rotate([0, 90, 0])
            cylinder(r1=4, r2=6, h=5);

    // Internal OLED Mounting Brackets
    translate([(HEAD_WIDTH - OLED_PCB_W) / 2, WALL_THICKNESS, (HEAD_HEIGHT - OLED_PCB_H) / 2])
        difference() {
            cube([OLED_PCB_W, 3, OLED_PCB_H]);
            translate([2, -1, 2])
                cube([OLED_PCB_W - 4, 5, OLED_PCB_H - 4]);
        }
}


// ------------------------------------------------------------------------------
// MODULE 2: 2-DOF Pan / Tilt Neck Mechanism
// ------------------------------------------------------------------------------
module neck_pan_tilt() {
    // Tilt Servo Mount (Attaches inside head)
    difference() {
        cube([SERVO_L + 6, SERVO_W + 6, SERVO_H + 4], center=true);
        cube([SERVO_L + TOLERANCE, SERVO_W + TOLERANCE, SERVO_H + 6], center=true);
    }

    // Joint Bracket
    translate([0, 0, -12])
        cylinder(r=5, h=10);
}


// ------------------------------------------------------------------------------
// MODULE 3: Cute Torso / Body
// ------------------------------------------------------------------------------
module robot_body() {
    difference() {
        // Outer body shell
        rounded_box(BODY_WIDTH, BODY_HEIGHT, BODY_DEPTH, BODY_CORNER_RADIUS);

        // Hollow interior for Arduino Nano ESP32 and wiring
        translate([WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS])
            rounded_box(
                BODY_WIDTH - 2 * WALL_THICKNESS,
                BODY_HEIGHT - 2 * WALL_THICKNESS,
                BODY_DEPTH - 2 * WALL_THICKNESS,
                BODY_CORNER_RADIUS - 1.5
            );

        // Top Opening for Neck Pan Servo
        translate([BODY_WIDTH / 2, BODY_DEPTH / 2, BODY_HEIGHT - WALL_THICKNESS - 1])
            cube([SERVO_L + TOLERANCE, SERVO_W + TOLERANCE, WALL_THICKNESS + 2], center=true);

        // Rear USB-C Power Port Cutout
        translate([BODY_WIDTH / 2 - 5, BODY_DEPTH - WALL_THICKNESS - 1, 6])
            cube([10, WALL_THICKNESS + 2, 4]);

        // Front Speaker Sound Grille (3 decorative speaker slots)
        for (i = [-6, 0, 6]) {
            translate([BODY_WIDTH / 2 + i, -1, BODY_HEIGHT / 2 - 4])
                cube([2.5, WALL_THICKNESS + 2, 10]);
        }
    }

    // Internal Arduino Nano ESP32 Mounting Rails
    translate([BODY_WIDTH / 2 - MCU_W / 2 - 1.5, 8, WALL_THICKNESS])
        cube([2, MCU_L, 4]);

    translate([BODY_WIDTH / 2 + MCU_W / 2 - 0.5, 8, WALL_THICKNESS])
        cube([2, MCU_L, 4]);
}


// ------------------------------------------------------------------------------
// MODULE 4: Weighted Stable Desk Base
// ------------------------------------------------------------------------------
module robot_base() {
    difference() {
        // Circular chamfered base
        cylinder(r1=BASE_DIA / 2, r2=BASE_DIA / 2 - 2, h=BASE_HEIGHT);

        // Recess for body alignment
        translate([0, 0, BASE_HEIGHT - 2])
            cube([BODY_WIDTH - 8, BODY_DEPTH - 8, 3], center=true);

        // 4 Anti-Slip Rubber Feet Recesses on bottom
        for (a = [45, 135, 225, 315]) {
            rotate([0, 0, a])
                translate([BASE_DIA / 2 - 8, 0, -0.5])
                    cylinder(r=5, h=1.5);
        }
    }
}


// ------------------------------------------------------------------------------
// COMPLETE ASSEMBLY VIEW
// ------------------------------------------------------------------------------
module deskbot_full_assembly() {
    // Base
    color("DimGray")
        robot_base();

    // Body
    color("Snow")
        translate([-BODY_WIDTH / 2, -BODY_DEPTH / 2, BASE_HEIGHT + 2])
            robot_body();

    // Neck Mechanism
    color("SkyBlue")
        translate([0, 0, BASE_HEIGHT + BODY_HEIGHT + 8])
            neck_pan_tilt();

    // Head
    color("White")
        translate([-HEAD_WIDTH / 2, -HEAD_DEPTH / 2, BASE_HEIGHT + BODY_HEIGHT + 14])
            robot_head();
}

// Render Complete Robot
deskbot_full_assembly();
