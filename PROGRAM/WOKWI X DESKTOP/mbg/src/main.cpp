#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

LiquidCrystal_I2C lcd(0x27, 16, 4);

#define PIN_LDR          A0  
#define PIN_DHT          2   
#define DHTTYPE          DHT22
#define PIN_SW_CHILLER   22  // Pin 22 Chiller
#define PIN_SW_FREEZER   23  // Pin 23 Freezer
#define PIN_BUZZER       6   
#define PIN_LED          11  

DHT dht(PIN_DHT, DHTTYPE);

enum ModeSistem { STANDBY, CHILLER, FREEZER };
ModeSistem modeAktif = STANDBY; 
unsigned long waktuSebelumnya = 0;
const long jedaBuzzer = 1000; 
bool statusBuzzer = LOW;

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  dht.begin();

  pinMode(PIN_SW_CHILLER, INPUT_PULLUP);
  pinMode(PIN_SW_FREEZER, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW); 

  lcd.setCursor(0, 0);
  lcd.print("  SISTEM KONTROL  ");
  lcd.setCursor(0, 1);
  lcd.print("      P2HMBG      ");
  delay(2000);
  lcd.clear();
}

void loop() {
  float kelembapan = dht.readHumidity();
  float suhu = dht.readTemperature();
  int nilaiKekeruhan = analogRead(PIN_LDR);

  if (digitalRead(PIN_SW_CHILLER) == LOW)  modeAktif = CHILLER;
  if (digitalRead(PIN_SW_FREEZER) == LOW)  modeAktif = FREEZER;
  if (isnan(kelembapan) || isnan(suhu)) return;

  bool kompresor = false;
  bool alarmSuhu = false;
  bool alarmAir = false;

  String statusAir = "";
  if (nilaiKekeruhan <= 300) {
    statusAir = "JERNIH";
  } else if (nilaiKekeruhan <= 700) {
    statusAir = "STANDAR";
  } else {
    statusAir = "KOTOR";
    if (modeAktif != STANDBY) alarmAir = true; 
  }

  String modeStr = "STANDBY";
  if (modeAktif == CHILLER) {
    modeStr = "CHILLER";
    if (suhu > 2.0) kompresor = true; 
    if (suhu >= 2.0 && suhu <= 8.0) alarmSuhu = false; 
    else alarmSuhu = true;  
  } 
  else if (modeAktif == FREEZER) {
    modeStr = "FREEZER";
    if (suhu > -25.0) kompresor = true;
    if (suhu >= -25.0 && suhu <= -15.0) alarmSuhu = false; 
    else alarmSuhu = true;  
  }

  bool alarmTotal = (alarmSuhu || alarmAir);

  if (modeAktif != STANDBY) {
    digitalWrite(PIN_LED, kompresor ? HIGH : LOW);
    if (alarmTotal == true) {
      unsigned long waktuSekarang = millis();
      if (waktuSekarang - waktuSebelumnya >= jedaBuzzer) {
        waktuSebelumnya = waktuSekarang; 
        statusBuzzer = !statusBuzzer;     
      }
      digitalWrite(PIN_BUZZER, statusBuzzer);
    } else {
      digitalWrite(PIN_BUZZER, LOW); 
      statusBuzzer = LOW;
    }
  } else {
    digitalWrite(PIN_LED, LOW);
    digitalWrite(PIN_BUZZER, LOW);
    statusBuzzer = LOW;
  }

  // --- OUTPUT JSON UNTUK PYTHON ---
  // Format: {"suhu": 4.2, "kelembapan": 63.0, "kekeruhan": 250, "status_air": "JERNIH", "mode": "CHILLER", "alarm": false}
  Serial.print("{\"suhu\": "); Serial.print(suhu);
  Serial.print(", \"kelembapan\": "); Serial.print(kelembapan);
  Serial.print(", \"kekeruhan\": "); Serial.print(nilaiKekeruhan);
  Serial.print(", \"status_air\": \""); Serial.print(statusAir);
  Serial.print("\", \"mode\": \""); Serial.print(modeStr);
  Serial.print("\", \"alarm\": "); Serial.print(alarmTotal ? "true" : "false");
  Serial.println("}");

  // TAMPILKAN KE LCD
  lcd.setCursor(0, 0);
  lcd.print("Suhu : "); lcd.print(suhu, 1); lcd.print(" C   ");
  lcd.setCursor(0, 1);
  lcd.print("Humid: "); lcd.print(kelembapan, 1); lcd.print(" %   ");
  lcd.setCursor(0, 2);
  lcd.print("Air:"); lcd.print(nilaiKekeruhan); lcd.print(" "); lcd.print(statusAir); lcd.print("   "); 
  lcd.setCursor(0, 3);
  if (modeAktif == CHILLER) {
    if (alarmSuhu) lcd.print("CHILLER: OUT RNG");
    else if (alarmAir) lcd.print("CHIL: AIR KERUH!");
    else lcd.print("CHILLER: AMAN   ");
  } 
  else if (modeAktif == FREEZER) {
    if (alarmSuhu) lcd.print("FREEZER: OUT RNG");
    else if (alarmAir) lcd.print("FREZ: AIR KERUH!");
    else lcd.print("FREEZER: AMAN   ");
  } 
  else {
    lcd.print("Mode : STANDBY  ");
  }
  delay(1000); // Delay diatur ke 1 detik agar Python tidak kewalahan menerima data
}