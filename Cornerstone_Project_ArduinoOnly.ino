// ENGR 111 Cornerstone Project Skeleton Code

#include <LiquidCrystal_I2C.h>

/**********************************************************/
LiquidCrystal_I2C lcd(0x27, 16, 2); // set the LCD address to 0x27 for a 16 chars and 2 line display
/**********************************************************/

// pin assignments (2 & 3 are the only interrupt pins)
const int tachPin = 2;
const int buttonPin = 3;
const int motorPin = A0;
int breakCount = 0;

// LCD settings
int displaySetting = 1;
const int maxDisplays = 5;
unsigned long lastDisplaySwitch = millis();
const int displayDelay = 250;
int flag = 0;

// YOUR GLOBAL VARIABLES SHOULD BE DECLARED HERE
int inputTach = digitalRead(tachPin);
int inputMot = digitalRead(motorPin);
double twmshaft;
double rpm;
double pwmshaft;
double fanPow;
double shaftPow;
double pwind;
double mEff;
double sEff;
double pelec;

int startTime = 0;

void setup() {
  // initialize LCD & its backlight
  lcd.init();
  lcd.backlight();

  // initialize pushbutton for LCD toggle
  pinMode(buttonPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(buttonPin), changeDisplaySettingFlag, FALLING);

  // initialize proximity sensor
  pinMode(tachPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(tachPin), broken, FALLING);

  // initialize motor input
  pinMode(motorPin, INPUT);

  // start timer for RPM calculation
  startTime = millis();
}

void loop() {
  
// Calculating RPM
while(motorPin == HIGH){
  if(inputTach == LOW){
    broken();
  }
}
rpm = (breakCount / 3) / ((millis() - startTime)* 60000);

//Calculating Power Output

int r = 10;
pelec = ((5/1023) * motorPin)*((5/1023) * motorPin) / r;

//Calculating Blade Efficiency

twmshaft = (.00392266)*(4 * rpm)*(4 * rpm);
pwmshaft = (twmshaft * rpm)/ 9549;
pwind = (.5 * 1.225 * (6.575)* (6.575) * (6.575) * (14.125) * (14.125));
fanPow =  100 * ( pwmshaft / pwind);

//Calculating Motor Efficiency

mEff = 100 * (pelec / pwmshaft);

//Calculating System Efficiency

sEff = 100 *(pelec / pwind);

displayLCD();
  
  if(flag == 1) 
  {
    flag = 0;
    changeDisplaySetting();
  }

  delay(1000);
  displayLCD();

  if(buttonPin == HIGH){
    changeDisplaySetting();
  }
}

//Call this function when you want to update the LCD Display
void displayLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  switch(displaySetting)
  {
    case 1:
    lcd.print("Windmill RPM");
    lcd.setCursor(0, 1);
    lcd.print(rpm);
    break;
    case 2:
    lcd.print("Power Output");
    lcd.setCursor(0, 1);
    lcd.print(pelec);
    break;
    case 3:
    lcd.print("Blade Efficiency");
    lcd.setCursor(0, 1);
    lcd.print(fanPow);
    break;
    case 4:
    lcd.print("Motor Efficiency");
    lcd.setCursor(0, 1);
    lcd.print(mEff);
    break;
    case 5:
    lcd.print("System Efficiency");
    lcd.setCursor(0, 1);
    lcd.print(sEff);
    break;
    default:
    lcd.print("Unknown Setting!");
  }
}

void changeDisplaySettingFlag() {
    flag = 1;
}

void changeDisplaySetting() {
    if(lastDisplaySwitch + displayDelay < millis()) { // this limits how quickly the LCD Display can switch
    lastDisplaySwitch = millis();
    displaySetting++;
    if(displaySetting > maxDisplays) {
      displaySetting = 1;
    }
    displayLCD();
  }
}

void broken() {
  breakCount++;
}
