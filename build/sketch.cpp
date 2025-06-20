#include <Arduino.h>

#include <Arduino.h>

// Определяем количество пинов и массив с номерами пинов
const int numPins = 21; // Всего 21 пин: цифровые 0-13 и аналоговые A0-A7
int pins[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3, A4, A5, A6, A7};

void setup() {
  // Настраиваем все пины как выходы
  for (int i = 0; i < numPins; i++) {
    pinMode(pins[i], OUTPUT);
  }
}

void loop() {
  // Эффект 1: Последовательное включение и выключение светодиодов
  for (int i = 0; i < numPins; i++) {
    digitalWrite(pins[i], HIGH);
    delay(100);
    digitalWrite(pins[i], LOW);
  }

  // Эффект 2: Бегущая строка с задержкой
  for (int i = 0; i < numPins; i++) {
    digitalWrite(pins[i], HIGH);
    delay(100);
  }
  for (int i = 0; i < numPins; i++) {
    digitalWrite(pins[i], LOW);
    delay(100);
  }

  // Эффект 3: Плавное затухание (для пинов с ШИМ, например, 3, 5, 6, 9, 10, 11)
  for (int i = 0; i < numPins; i++) {
    if (pins[i] == 3 || pins[i] == 5 || pins[i] == 6 || pins[i] == 9 || pins[i] == 10 || pins[i] == 11) {
      for (int brightness = 0; brightness <= 255; brightness++) {
        analogWrite(pins[i], brightness);
        delay(5);
      }
      for (int brightness = 255; brightness >= 0; brightness--) {
        analogWrite(pins[i], brightness);
        delay(5);
      }
    }
  }

  // Эффект 4: Бегущая строка в обратном направлении
  for (int i = numPins - 1; i >= 0; i--) {
    digitalWrite(pins[i], HIGH);
    delay(100);
    digitalWrite(pins[i], LOW);
  }

  // Эффект 5: Случайное мигание
  for (int j = 0; j < 50; j++) { // 50 случайных миганий
    int randomPin = pins[random(numPins)]; // Выбираем случайный пин
    digitalWrite(randomPin, HIGH);
    delay(50);
    digitalWrite(randomPin, LOW);
    delay(50);
  }
}
