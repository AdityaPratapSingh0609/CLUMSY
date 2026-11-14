/*
 * DESKBOT / J.A.R.V.I.S. Companion Firmware (Stage 14)
 * Dual-Target Support:
 *   1. Arduino Uno (R3 / R4) + HC-05 / HM-10 Bluetooth Serial
 *      - I2C SSD1306 OLED (128x64) -> SDA: A4, SCL: A5
 *      - Pan Servo (SG90)          -> Pin D9 (PWM)
 *      - Tilt Servo (SG90)         -> Pin D10 (PWM)
 *      - Bluetooth UART            -> Pin D2 (RX), Pin D3 (TX) + USB Serial
 *   2. Arduino Nano ESP32 / ESP32-WROOM / ESP32-S3
 *      - I2C SSD1306 OLED (128x64) -> SDA: D21, SCL: D22
 *      - Pan Servo (SG90)          -> Pin D18 (PWM)
 *      - Tilt Servo (SG90)         -> Pin D19 (PWM)
 *      - Built-in BluetoothSerial ("Deskbot-Companion") + USB Serial
 *
 * Features:
 *   - Non-linear Cubic Easing (easeInOutCubic) preventing mechanical gear snaps
 *   - Hardware Servo Angle Limiters (15 deg to 165 deg)
 *   - Dual Protocol Parser: Compact (<P90,T95,Ehappy>) & JSON packets
 *   - 10-second Bluetooth Watchdog auto-centering to IDLE (90 deg / 90 deg)
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#if defined(ESP32)
  #include <ESP32Servo.h>
  #include <BluetoothSerial.h>
  BluetoothSerial SerialBT;
  const int PIN_PAN_SERVO  = 18;
  const int PIN_TILT_SERVO = 19;
#else
  // Arduino Uno (R3 / R4)
  #include <Servo.h>
  #include <SoftwareSerial.h>
  const int PIN_BT_RX      = 2;
  const int PIN_BT_TX      = 3;
  const int PIN_PAN_SERVO  = 9;
  const int PIN_TILT_SERVO = 10;
  SoftwareSerial SerialBT(PIN_BT_RX, PIN_BT_TX);
#endif

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

#define SERVO_MIN_DEG 15
#define SERVO_MAX_DEG 165
#define WATCHDOG_TIMEOUT_MS 10000UL

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Servo panServo;
Servo tiltServo;

// Cubic easing motion state
float startPan = 90.0f, currentPan = 90.0f, targetPan = 90.0f;
float startTilt = 90.0f, currentTilt = 90.0f, targetTilt = 90.0f;
unsigned long moveStartMs = 0;
unsigned long moveDurationMs = 260;

String currentExpression = "idle";
unsigned long lastBlinkTime = 0;
unsigned long lastPacketTime = 0;
bool isBlinking = false;

int clampServoAngle(int deg) {
  if (deg < SERVO_MIN_DEG) return SERVO_MIN_DEG;
  if (deg > SERVO_MAX_DEG) return SERVO_MAX_DEG;
  return deg;
}

float easeInOutCubic(float t) {
  if (t <= 0.0f) return 0.0f;
  if (t >= 1.0f) return 1.0f;
  if (t < 0.5f) return 4.0f * t * t * t;
  float p = -2.0f * t + 2.0f;
  return 1.0f - (p * p * p) * 0.5f;
}

void setTargetPose(int newPan, int newTilt, const String& expr) {
  startPan = currentPan;
  startTilt = currentTilt;
  targetPan = (float)clampServoAngle(newPan);
  targetTilt = (float)clampServoAngle(newTilt);
  currentExpression = expr;
  moveStartMs = millis();
  lastPacketTime = moveStartMs;
}

void parseCommandPacket(String line) {
  line.trim();
  if (line.length() == 0) return;

  int pan = (int)targetPan;
  int tilt = (int)targetTilt;
  String expr = currentExpression;

  // Compact Arduino Uno frame: <P90,T105,Elistening>
  if (line.startsWith("<") && line.endsWith(">")) {
    int pIdx = line.indexOf('P');
    int tIdx = line.indexOf('T');
    int eIdx = line.indexOf('E');
    if (pIdx > 0) pan = line.substring(pIdx + 1, line.indexOf(',', pIdx)).toInt();
    if (tIdx > 0) tilt = line.substring(tIdx + 1, line.indexOf(',', tIdx)).toInt();
    if (eIdx > 0) expr = line.substring(eIdx + 1, line.length() - 1);
    setTargetPose(pan, tilt, expr);
    Serial.print(F("ACK:"));
    Serial.print(clampServoAngle(pan));
    Serial.print(F(","));
    Serial.print(clampServoAngle(tilt));
    Serial.print(F(","));
    Serial.println(expr);
    return;
  }

  // Lightweight JSON extractor (works on 2KB SRAM Arduino Uno without heap fragmentation)
  int panKey = line.indexOf("\"pan\":");
  if (panKey >= 0) {
    pan = line.substring(panKey + 6).toInt();
  }
  int tiltKey = line.indexOf("\"tilt\":");
  if (tiltKey >= 0) {
    tilt = line.substring(tiltKey + 7).toInt();
  }
  int exprKey = line.indexOf("\"expression\":\"");
  if (exprKey >= 0) {
    int startQ = exprKey + 14;
    int endQ = line.indexOf('"', startQ);
    if (endQ > startQ) {
      expr = line.substring(startQ, endQ);
    }
  }
  setTargetPose(pan, tilt, expr);
  Serial.println(F("{\"ack\":true}"));
}

void drawEyes(const String& expr, bool blink);

void setup() {
  Serial.begin(115200);
#if defined(ESP32)
  SerialBT.begin("Deskbot-Companion");
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  panServo.setPeriodHertz(50);
  tiltServo.setPeriodHertz(50);
  panServo.attach(PIN_PAN_SERVO, 500, 2400);
  tiltServo.attach(PIN_TILT_SERVO, 500, 2400);
#else
  SerialBT.begin(9600);
  panServo.attach(PIN_PAN_SERVO);
  tiltServo.attach(PIN_TILT_SERVO);
#endif

  panServo.write(90);
  tiltServo.write(90);
  lastPacketTime = millis();

  if (display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    display.clearDisplay();
    drawEyes("happy", false);
    display.display();
  }
}

void loop() {
  if (Serial.available()) {
    parseCommandPacket(Serial.readStringUntil('\n'));
  }
  if (SerialBT.available()) {
    parseCommandPacket(SerialBT.readStringUntil('\n'));
  }

  unsigned long now = millis();

  // Bluetooth watchdog: return to neutral idle after 10s of silence
  if (currentExpression != "idle" && (now - lastPacketTime > WATCHDOG_TIMEOUT_MS)) {
    setTargetPose(90, 90, "idle");
  }

  // Non-linear cubic easing servo interpolation
  float elapsed = (float)(now - moveStartMs);
  float alpha = easeInOutCubic(elapsed / (float)moveDurationMs);
  currentPan = startPan + (targetPan - startPan) * alpha;
  currentTilt = startTilt + (targetTilt - startTilt) * alpha;

  panServo.write(clampServoAngle((int)(currentPan + 0.5f)));
  tiltServo.write(clampServoAngle((int)(currentTilt + 0.5f)));

  // Natural idle blink every 3.5s
  if (currentExpression == "idle" && (now - lastBlinkTime > 3500)) {
    isBlinking = true;
    lastBlinkTime = now;
  }
  if (isBlinking && (now - lastBlinkTime > 150)) {
    isBlinking = false;
  }

  display.clearDisplay();
  drawEyes(currentExpression, isBlinking);
  display.display();

  delay(15);
}

void drawEyes(const String& expr, bool blink) {
  int eyeY = 32;
  int leftEyeX = 40;
  int rightEyeX = 88;
  int eyeRadius = 14;

  if (blink) {
    display.drawLine(leftEyeX - 12, eyeY, leftEyeX + 12, eyeY, SSD1306_WHITE);
    display.drawLine(rightEyeX - 12, eyeY, rightEyeX + 12, eyeY, SSD1306_WHITE);
    return;
  }

  if (expr == "happy") {
    display.drawCircle(leftEyeX, eyeY + 6, 12, SSD1306_WHITE);
    display.fillRect(leftEyeX - 14, eyeY + 6, 28, 14, SSD1306_BLACK);
    display.drawCircle(rightEyeX, eyeY + 6, 12, SSD1306_WHITE);
    display.fillRect(rightEyeX - 14, eyeY + 6, 28, 14, SSD1306_BLACK);
  } else if (expr == "listening") {
    display.fillCircle(leftEyeX, eyeY, 16, SSD1306_WHITE);
    display.fillCircle(rightEyeX, eyeY, 16, SSD1306_WHITE);
    display.fillCircle(leftEyeX - 4, eyeY - 4, 4, SSD1306_BLACK);
    display.fillCircle(rightEyeX - 4, eyeY - 4, 4, SSD1306_BLACK);
  } else if (expr == "thinking") {
    display.fillCircle(leftEyeX + 4, eyeY - 6, 12, SSD1306_WHITE);
    display.fillCircle(rightEyeX + 4, eyeY - 6, 12, SSD1306_WHITE);
  } else if (expr == "confused") {
    display.fillCircle(leftEyeX, eyeY, 16, SSD1306_WHITE);
    display.fillCircle(rightEyeX, eyeY, 8, SSD1306_WHITE);
  } else {
    display.fillCircle(leftEyeX, eyeY, eyeRadius, SSD1306_WHITE);
    display.fillCircle(rightEyeX, eyeY, eyeRadius, SSD1306_WHITE);
    display.fillCircle(leftEyeX + 3, eyeY - 3, 4, SSD1306_BLACK);
    display.fillCircle(rightEyeX + 3, eyeY - 3, 4, SSD1306_BLACK);
  }
}
