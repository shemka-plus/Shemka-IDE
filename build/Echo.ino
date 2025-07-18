const int numPins = 21;
int pins[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3, A4, A5, A6, A7};
unsigned long previousMillis = 0;
const long interval = 100; // Интервал между шагами эффектов

void setup() {
  for (int i = 0; i < numPins; i++) {
    pinMode(pins[i], OUTPUT);
  }
  Serial.begin(9600);
  while (!Serial) {
    ; // Ожидаем подключения последовательного порта
  }
}

void loop() {
  // Обработка UART с наивысшим приоритетом
  if (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n');
    Serial.print("ECHO: ");
    Serial.println(received); // Отправляем обратно с пометкой
  }

  // Управление световыми эффектами без delay()
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    runLightEffectsStep();
  }
}

int effect = 0;
int step = 0;
int brightness = 0;
bool direction = true;

void runLightEffectsStep() {
  switch(effect) {
    case 0: // Эффект 1: Последовательное включение
      if (step < numPins) {
        digitalWrite(pins[step], HIGH);
        if (step > 0) digitalWrite(pins[step-1], LOW);
        step++;
      } else {
        digitalWrite(pins[numPins-1], LOW);
        effect = 1;
        step = 0;
      }
      break;
      
    case 1: // Эффект 2: Бегущая строка
      if (step < numPins) {
        digitalWrite(pins[step], HIGH);
        step++;
      } else {
        for (int i = 0; i < numPins; i++) digitalWrite(pins[i], LOW);
        effect = 2;
        step = 0;
      }
      break;
      
    case 2: // Эффект 3: Плавное затухание (только PWM пины)
      if (step < numPins) {
        if (pins[step] == 3 || pins[step] == 5 || pins[step] == 6 || 
            pins[step] == 9 || pins[step] == 10 || pins[step] == 11) {
          if (direction) {
            brightness += 5;
            if (brightness >= 255) direction = false;
          } else {
            brightness -= 5;
            if (brightness <= 0) {
              direction = true;
              step++;
            }
          }
          analogWrite(pins[step], brightness);
        } else {
          step++;
        }
      } else {
        effect = 3;
        step = numPins-1;
      }
      break;
      
    case 3: // Эффект 4: Обратное направление
      if (step >= 0) {
        digitalWrite(pins[step], HIGH);
        if (step < numPins-1) digitalWrite(pins[step+1], LOW);
        step--;
      } else {
        digitalWrite(pins[0], LOW);
        effect = 4;
        step = 0;
      }
      break;
      
    case 4: // Эффект 5: Случайное мигание
      if (step < 50) {
        int randomPin = pins[random(numPins)];
        digitalWrite(randomPin, HIGH);
        delay(50);
        digitalWrite(randomPin, LOW);
        step++;
      } else {
        effect = 0;
        step = 0;
      }
      break;
  }
}