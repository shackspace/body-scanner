//Polulu pins
const int sleepPin = 2; 
const int stepPin = 3;
const int dirPin = 4;
 
const int sensorPin = 5; //Pins for the sensor if the bottom was reached
const int statusPin = 6; //Are we currently ready or working?

//Pins for communication with the OrangePi
const int enablePin = 7;
const int serialPin1 = 8;
const int serialPin2 = 9;

const long height = 8450;
const int ramp[] = {50, 45, 30, 25, 20, 17, 14, 11, 8, 7, 6, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};



void setup(){
	//Configure the pins
	pinMode(sleepPin, OUTPUT);
	pinMode(stepPin, OUTPUT); 
	pinMode(dirPin, OUTPUT);
	
	pinMode(sensorPin, INPUT_PULLUP);
	pinMode(statusPin, OUTPUT);
	
	pinMode(enablePin, INPUT);
	pinMode(serialPin1, INPUT);
	pinMode(serialPin2, INPUT);

        pinMode(10, OUTPUT);
        pinMode(11,OUTPUT);
        digitalWrite(10, HIGH);
        digitalWrite(11, HIGH);

        Serial.begin(9600);
        startSleep();
}

void doStep(int steps){
	endSleep();
	doRamp();
	for(int i=0; i<steps; i++) {
		digitalWrite(stepPin,HIGH);
		delay(1);
		digitalWrite(stepPin,LOW);
		delay(1);
        }
	startSleep();
}

void doRamp(){
        Serial.print("do ramp");
	//Uses the predefined ramp to avoid float mathematics
	for(int i=0; i<50; i++){
                Serial.println(ramp[i]);
		digitalWrite(stepPin,HIGH);
		delay(ramp[i]);
		digitalWrite(stepPin,LOW);
		delay(ramp[i]);
        }
}

void goUp(int steps){
        Serial.print("go up");
	setDirectionUp();
	doStep(steps);
}

void goDown(int steps){
        Serial.print("go down");
	setDirectionDown();
	doStep(steps);
}

void goTop(){
        Serial.print("go top");
	setDirectionUp();
	doStep(height-50);
}

void goBottom(){
        Serial.print("go bottom");
        int debounce = 0;
	setDirectionDown();
	endSleep();
	doRamp();
	
	for(long i=0; i<height; i++) {
		if(!(digitalRead(sensorPin))){debounce++;}
		else{debounce=0;}
		
		if (debounce > 5){
			debounce = 0;
			goUp(0); //Move out of the sensor
			startSleep();
			break;
		}
	
		digitalWrite(stepPin,HIGH); 
		delay(1);
		digitalWrite(stepPin,LOW);
		delay(1);
	}
}

void setDirectionUp(){digitalWrite(dirPin, LOW);}
void setDirectionDown(){digitalWrite(dirPin, HIGH);}

void startSleep(){
	digitalWrite(sleepPin, LOW); //Disable the StepperDriver
	digitalWrite(statusPin, HIGH); //Signal to the OrangePi Arduino is ready
}

void endSleep(){
	digitalWrite(sleepPin, HIGH); //Enable the StepperDriver
	digitalWrite(statusPin, LOW); //Signal to the OrangePi Arduino is working
}

void loop(){
	//Dont forget to set RESET and MS1 to HIGH (Half Step)!	
	if(digitalRead(enablePin) == HIGH){
		//Start the command parser
		if(digitalRead(serialPin1) == HIGH){
			if(digitalRead(serialPin2) == HIGH) goTop();
			else goBottom();
		}
		else{
			if(digitalRead(serialPin2) == HIGH) goUp(150);
                        else goDown(150);		
		}
	}
}

void loop2(){
  delay(5000);
  goBottom();
  delay(2000);
  goUp(500);
}
