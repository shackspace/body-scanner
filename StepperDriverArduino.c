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
const int[] ramp = {50, 48, 46, 44, 40, 36, 32, 26, 20, 16, 12, 10, 8, 6, 4, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}


void setup(){
	//Configure the pins
	pinMode(sleepPin, OUTPUT);
	pinMode(stepPin, OUTPUT); 
	pinMode(dirPin, OUTPUT);
	
	pinMode(sensorPin, INPUT_PULLUP);
	pinMode(statusPin, OUTPUT);
	
	pinMode(enablePin, INPUT);
	pinMode(serialPin1, INPUT);
	pinMode(serialPin2, INPUT);;
}

void doStep(int steps){
	endSleep();
	doRamp();
	
	for(int i=0; i<steps; i++) {
		digitalWrite(stepPin,HIGH);
		delay(1);
		digitalWrite(stepPin,LOW);
		delay(1);

	startSleep();
}

void doRamp(){
	//Uses the predefined ramp to avoid float mathematics
	for(int i=0; i<50; i++) {
		digitalWrite(stepPin,HIGH);
		delay(ramp[i]);
		digitalWrite(stepPin,LOW);
		delay(ramp[i]);
}

void goUp(int steps){
	setDirectionUp();
	doStep(steps);
}

void goDown(int steps){
	setDirectionDown();
	doStep(steps);
}

void goTop(){
	setDirectionUp();
	doStep(height-50);
}

void goBottom(){
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
		if(digitalRead(serialPin1 == HIGH)){
			if(digitalRead(serialPin2 == HIGH)) goTop();
			else goBottom();
		}
		else{
			if(digitalRead(serialPin2 == HIGH)) goUp(150);
			else goDown(150);			
		}
	}
}
