
// defines pins numbers
const int lsPin = 1; 
const int sleepPin = 2; 
const int stepPin = 3; 
const int dirPin = 4; 

const int speed = 80; 

 
void setup() {
  // Sets the two pins as Outputs
  pinMode(stepPin,OUTPUT); 
  pinMode(lsPin,INPUT_PULLUP); 
  pinMode(dirPin,OUTPUT);
  pinMode(sleepPin,OUTPUT);
    digitalWrite(sleepPin,HIGH); //Changes the rotations direction

}

int mode = 0;


void loop() {

digitalWrite(dirPin, !digitalRead(dirPin));

long count = 34700;
static int debounce = 0;

//  digitalWrite(dirPin,HIGH); // Enables the motor to move in a particular direction
  // Makes 200 pulses for making one full cycle rotation
  for(long x = 0; x < count; x++) {
    if(!(digitalRead(lsPin)))
      debounce++;
    else
       debounce = 0;
    
    if (debounce >= 5) {
      debounce = 0;
      digitalWrite(sleepPin,LOW);
      mode = 1;
      break;
    }

    digitalWrite(stepPin,HIGH); 
    delayMicroseconds(200); 
    digitalWrite(stepPin,LOW);

    long y = 1000-(x);
    if (x < 1000)
      delayMicroseconds(y); 

    y = (x-(count-500))*2;
    if (x > (count-500))
      delayMicroseconds(y); 
    delayMicroseconds(speed); 
  }

    if (mode == 1) {
      mode = 2;  

      delay(100); // One second delay
      
      digitalWrite(dirPin,LOW); //Changes the rotations direction
      digitalWrite(sleepPin,HIGH);

      // Makes 400 pulses for making two full cycle rotation
      for(int x = 0; x < 200; x++) {
 
         if((digitalRead(lsPin)))
          debounce++;
        else
           debounce = 0;
        
        if (debounce >= 5) {
          debounce = 0;
          break;
        }

 
        digitalWrite(stepPin,HIGH);
        delayMicroseconds(500);
        digitalWrite(stepPin,LOW);
        delayMicroseconds(1000);
      } 
      for(int x = 0; x < 50; x++) {
        digitalWrite(stepPin,HIGH);
        delayMicroseconds(500);
        digitalWrite(stepPin,LOW);
        delayMicroseconds(1000);
      } 
      digitalWrite(dirPin,HIGH); //Changes the rotations direction
      digitalWrite(sleepPin,LOW);
    }


      delay(100); // One second delay
    digitalWrite(sleepPin,LOW); //Changes the rotations direction
      delay(10000); // One second delay
    digitalWrite(sleepPin,HIGH); //Changes the rotations direction
      delay(100); // One second delay
  
}
