#include <Adafruit_NeoPixel.h>

// Конфигурация
#define LED_PIN     6
#define LED_COUNT   8  // 3 этажа * 12 окон

// Создаем объект для управления светодиодами
Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Определение эффектов
enum Effect {
  OFF,            // Выключено
  LIGHT,          // Просто свет
  TV,             // Эффект телевизора
  PARTY,          // Эффект вечеринки
  FADING          // Мерцание (затухание/усиление)
};

// Структура для настроек окна
struct Window {
  Effect effect;  // Эффект
  int brightness; // Яркость (0-255)
  int hue;        // Оттенок (0-360)
};

Window windows[LED_COUNT]; // Массив окон

void setup() {
  pixels.begin();
  pixels.setBrightness(100); // Общая яркость (можно регулировать)
  
  // Инициализация всех окон (по умолчанию - свет)
  for (int i = 0; i < LED_COUNT; i++) {
    windows[i] = {LIGHT, random(100, 255), random(0, 60)};
  }
  
  // Установка специальных эффектов (можно менять по своему усмотрению)
  setWindowEffect(0, 3, PARTY);   // 2 этаж (индекс 1), 3 окно - вечеринка
  setWindowEffect(0, 4, TV);      // 1 этаж (индекс 0), 4 окно - телевизор
  setWindowEffect(0, 5, OFF);     // 1 этаж, 4 окно - выключено (перезаписали TV)
  //setWindowEffect(0, 7, OFF);     // 1 этаж, 7 окно - выключено
  //setWindowEffect(0, 8, OFF);     // 1 этаж, 8 окно - выключено
  
  // Случайное мерцание для некоторых окон
  for (int i = 0; i < 10; i++) {
    int floor = random(0, 3);
    int window = random(0, 12);
    setWindowEffect(floor, window, FADING);
  }
}

void loop() {
  updateAllWindows();
  pixels.show();
  delay(50); // Задержка для плавности анимаций
}

// Установка эффекта для конкретного окна
void setWindowEffect(int floor, int windowNum, Effect effect) {
  int index = floor * 12 + windowNum;
  if (index >= 0 && index < LED_COUNT) {
    windows[index].effect = effect;
    
    // Установка параметров по умолчанию для эффектов
    switch(effect) {
      case LIGHT:
        windows[index].brightness = random(100, 255);
        windows[index].hue = random(0, 60); // Теплый свет
        break;
      case TV:
        windows[index].brightness = 200;
        windows[index].hue = random(0, 360); // Разные цвета
        break;
      case PARTY:
        windows[index].brightness = 255;
        windows[index].hue = random(0, 360);
        break;
      case FADING:
        windows[index].brightness = random(50, 150);
        windows[index].hue = random(0, 60);
        break;
      case OFF:
        windows[index].brightness = 0;
        break;
    }
  }
}

// Обновление всех окон
void updateAllWindows() {
  for (int i = 0; i < LED_COUNT; i++) {
    updateWindow(i);
  }
}

// Обновление конкретного окна
void updateWindow(int index) {
  Window &w = windows[index];
  
  switch(w.effect) {
    case OFF:
      setWindowColor(index, 0, 0, 0);
      break;
      
    case LIGHT:
      // Случайные небольшие колебания яркости
      w.brightness += random(-5, 5);
      w.brightness = constrain(w.brightness, 100, 255);
      setWindowHue(index, w.hue, w.brightness);
      break;
      
    case TV:
      // Эффект меняющегося телевизора
      if (random(100) < 30) {
        w.hue = random(0, 360);
        w.brightness = random(150, 255);
      }
      setWindowHue(index, w.hue, w.brightness);
      break;
      
    case PARTY:
      // Эффект вечеринки - резкие смены цвета
      if (random(100) < 40) {
        w.hue = random(0, 360);
        w.brightness = random(200, 255);
      }
      setWindowHue(index, w.hue, w.brightness);
      break;
      
    case FADING:
      // Эффект мерцания
      static int fadeDir = 1;
      w.brightness += fadeDir * random(1, 5);
      
      if (w.brightness <= 50) {
        w.brightness = 50;
        fadeDir = 1;
        // Иногда полностью выключаемся на случайное время
        if (random(100) < 10) {
          w.brightness = 0;
          delay(random(500, 3000));
        }
      } else if (w.brightness >= 200) {
        w.brightness = 200;
        fadeDir = -1;
      }
      setWindowHue(index, w.hue, w.brightness);
      break;
  }
}

// Установка цвета окна по HSV (оттенок, насыщенность, яркость)
void setWindowHue(int index, int hue, int brightness) {
  // Преобразование HSV в RGB
  int h = hue / 60;
  float f = (hue % 60) / 60.0;
  int p = brightness * (1 - 1.0);
  int q = brightness * (1 - f);
  int t = brightness * (1 - (1 - f));
  
  uint8_t r, g, b;
  switch(h) {
    case 0: r = brightness; g = t; b = p; break;
    case 1: r = q; g = brightness; b = p; break;
    case 2: r = p; g = brightness; b = t; break;
    case 3: r = p; g = q; b = brightness; break;
    case 4: r = t; g = p; b = brightness; break;
    default: r = brightness; g = p; b = q;
  }
  
  setWindowColor(index, r, g, b);
}

// Установка цвета окна по RGB
void setWindowColor(int index, uint8_t r, uint8_t g, uint8_t b) {
  pixels.setPixelColor(index, pixels.Color(r, g, b));
}
