# DESKBOT — 3D Printing & CAD Assembly Guide

This folder contains the complete mechanical CAD model for the cute DESKBOT companion robot.

---

## 📁 CAD File
* **`deskbot_model.scad`**: Parametric OpenSCAD design file. You can open this in [OpenSCAD](https://openscad.org/) (free & open source) and export individual STL files with one click (`F6` to render, `F7` to export STL).

---

## 🖨️ Recommended 3D Printing Settings

| Parameter | Recommended Value | Reason |
| :--- | :--- | :--- |
| **Material** | **PLA** or **PETG** | PLA gives great surface detail and aesthetic finish; PETG provides extra strength for servo brackets. |
| **Layer Height** | **0.16 mm – 0.20 mm** | Smooth rounded head and body contours. |
| **Infill** | **20% – 25% (Gyroid or Grid)** | Strong enough for servo mounting screws while staying lightweight. |
| **Wall Lines (Perimeters)** | **3 walls** (~1.2 mm to 1.6 mm) | Ensures screw holes and snap-fits do not crack. |
| **Supports** | **Tree / Organic Supports (On)** | Only needed for the head front display opening and neck bracket cavities. |

---

## 🧩 Assembly Steps

```
[ Head with OLED Eyes & Mic ]
             ▲
             │ (M2 Screws)
[ 2-DOF Pan/Tilt Neck Bracket (SG90 Servos) ]
             ▲
             │ (M2 Screws)
[ Torso / Body (Arduino Nano ESP32 & Speaker) ]
             ▲
             │ (Press-Fit / Snap)
[ Weighted Desk Base with Rubber Pads ]
```

1. **Head Assembly:**
   * Slide the **0.96" I2C OLED screen** into the internal front brackets behind the viewing window. Secure with tiny drops of hot glue or M2 screws.
   * Insert the **INMP441 Microphone** behind the 2.5mm front mic hole.
   * Attach the tilt servo horn to the inside ceiling/pivot of the head.

2. **Neck Assembly:**
   * Mount the **Tilt Servo (SG90)** into the upper neck bracket.
   * Mount the **Pan Servo (SG90)** into the lower torso socket.

3. **Torso Assembly:**
   * Slide the **Arduino Nano ESP32** into the internal chassis rails.
   * Align the USB-C port with the rear cutout for easy desktop cable connection.
   * Place the **3W mini speaker** facing the front decorative grille slots.

4. **Base:**
   * Attach 4 adhesive rubber feet to the base recesses to prevent desk slipping during motor movements.
