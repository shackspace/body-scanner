
// 'u' => up
// 'd' => down
// 'r' => reset to bottom
// 't' => move to top

// defines pins numbers
const int lsPin = 10; 
const int sleepPin = 2; 
const int stepPin = 3; 
const int dirPin = 4; 

const int speed = 80; 
const long count = 34700;
//const long count = 4000;

int mode;
int debounce;

 
void setup() {
  // Sets the two pins as Outputs
  pinMode(stepPin,OUTPUT); 
  pinMode(lsPin,INPUT_PULLUP); 
  pinMode(dirPin,OUTPUT);
  pinMode(sleepPin,OUTPUT);

  Serial.begin(9600);

  mode = 2;
  debounce = 0;
}



void loop() {

  if(mode==0)
  {
    go_bottom();
  }
  if (mode == 1) {
    mode = 2;  
  calibrate();
  }

  mode = 2;

  while (mode==2) {
    while(Serial.available() == 0) {};
    char rec = Serial.read();
    if(rec == 'r')
    {
      mode = 0;
      digitalWrite(dirPin,LOW); //Changes the rotations direction
    }
    if(rec == 't')
    {
      mode = 0;
      digitalWrite(dirPin,HIGH); //Changes the rotations direction
    }
    if(rec == 'u')
    {
      go_up();
    }
    if(rec == 'd')
    {
      go_down();
    }
  }

     delay(100); // One second delay
  digitalWrite(sleepPin,LOW); //Changes the rotations direction
//     delay(2000); // One second delay
   digitalWrite(sleepPin,HIGH); //Changes the rotations direction
     delay(100); // One second delay
  
}


void go_up(void)
{
       digitalWrite(dirPin,LOW); //Changes the rotations direction
      digitalWrite(sleepPin,HIGH);

      for(int x = 0; x < 500; x++) {
        digitalWrite(stepPin,HIGH);
        delayMicroseconds(500);
        digitalWrite(stepPin,LOW);
        delayMicroseconds(1000);
      } 

      digitalWrite(dirPin,HIGH); //Changes the rotations direction
      digitalWrite(sleepPin,LOW);
 
}
void go_down(void)
{
       digitalWrite(dirPin,HIGH); //Changes the rotations direction
      digitalWrite(sleepPin,HIGH);

      for(int x = 0; x < 500; x++) {
        digitalWrite(stepPin,HIGH);
        delayMicroseconds(500);
        digitalWrite(stepPin,LOW);
        delayMicroseconds(1000);
      } 

      digitalWrite(dirPin,LOW); //Changes the rotations direction
      digitalWrite(sleepPin,LOW);
 
}

void go_bottom(void)
{
    digitalWrite(sleepPin,HIGH); //Changes the rotations direction
    digitalWrite(dirPin, !digitalRead(dirPin));
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
}


void calibrate(void)
{
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
