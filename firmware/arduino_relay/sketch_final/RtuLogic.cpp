#include "RtuLogic.h"
#include "AdcManager.h"
#include "Pins.h"
#include "Config.h"

unsigned long tSWI = 0;
unsigned int swi_pin_counter = 0;

relay_state relay[RELAY_ROWS][RELAY_AMOUNT];

void RtuLogic_init()
{
  uint8_t index = 0;
  for(int pin = 0; pin < MS_OUT_NUM_CHANNELS; pin++){
    pinMode(ms_output_array[pin], OUTPUT);          // sets the digital pin as output
    digitalWrite(ms_output_array[pin], LOW);        // sets the digital pins off (green led on), breaker open
  }
  for(int pin = 0; pin < MS_IN_NUM_CHANNELS; pin++){
    pinMode(ms_input_array[pin], INPUT_PULLUP);          // sets the digital pin as input with a pullup
  }

  //init relay states
  for(int i = 0; i < RELAY_ROWS; i++){
    relay[i][TYPE_RELAY_INCOMING_INDEX].deviceType = TYPE_RELAY_INCOMING;  // incoming Relay
    relay[i][TYPE_MEASURE_INDEX].deviceType = TYPE_MEASURE;         // Mesurement device (voltage)
    relay[i][TYPE_RELAY_OUTGOING_INDEX].deviceType = TYPE_RELAY_OUTGOING;  // outgoing Relay
    relay[i][TYPE_RELAY_OUTGOING_INDEX+1].deviceType = TYPE_RELAY_OUTGOING;  // outgoing Relay
    relay[i][TYPE_RELAY_OUTGOING_INDEX+2].deviceType = TYPE_RELAY_OUTGOING;  // outgoing Relay

    for (int j = 0; j < RELAY_AMOUNT; j++) {
      relay[i][j].breakerState = false;              // Open
      relay[i][j].tripState = false;                 // Reset
      relay[i][j].faultState = false;                // No fault
      relay[i][j].faultEvent = None;
      relay[i][j].faultTime = 0;
      relay[i][j].remote = false;                    // Local
      relay[i][j].PTOC_setting_pickup_current = 5000; //500.0A
      relay[i][j].PTOC_setting_time_multiplier = 15; //0.15-0.25 
      relay[i][j].PIOC_setting_pickup_current = 50000; //5000.0 A
      relay[i][j].index = index++;

      for (int k = 0; k < 4; k++) {
          relay[i][j].Measurement[k] = 0;
          relay[i][j].PTOC_Timer[k] = 0;
      }
    }
  }
}

float residual(long Ia, long Ib, long Ic)
{
    float a = Ia / 10.0f;
    float b = Ib / 10.0f;
    float c = Ic / 10.0f;

    return sqrt(
        a*a + b*b + c*c
        - a*b - b*c - c*a
    );
}

void performLogic(int row) {
  for(int index = 0; index < RELAY_AMOUNT; index++)
  {
    if(relay[row][index].deviceType == TYPE_RELAY_INCOMING)
    {
      //simulate currents based on TYPE_RELAY_OUTGOING
      relay[row][index].faultState = false; //reset faultstate before calculation
      if(relay[row][index].breakerState == true) {      //if breaker closed
        // check for tripstate, if true(set in previous iteration), open breaker
        if(relay[row][index].tripState == true) {
          updateBreakerOutput(&relay[row][index], false); //set breakerstate to open
          relay[row][index].PTOC_Timer[0] = 0;
          relay[row][index].PTOC_Timer[1] = 0;
          relay[row][index].PTOC_Timer[2] = 0;
          relay[row][index].PTOC_Timer[3] = 0;
          continue;
        }

        for (int k = 0; k < 4; k++) {               //for each phase
          long current = 0;
          for (int j = TYPE_RELAY_OUTGOING_INDEX; j < RELAY_AMOUNT; j++) {  // add all outgoing currents, from the previous iteration
            current += relay[row][j].Measurement[k];
          }
          relay[row][index].Measurement[k] = current;
          //
          // calculate if feeder current exceeds max value, if so, set fault, set tripstate to true
          //PIOC
          if(relay[row][index].Measurement[k] >= relay[row][index].PIOC_setting_pickup_current) {
            relay[row][index].faultState = true;
            if(relay[row][index].tripState == false) { //PIOC is immediate trip
                relay[row][index].tripState = true;
                setFaultRegister(&relay[row][index], Earth_fault);
            }
          }
          else {
            //PTOC
            if(relay[row][index].Measurement[k] >= relay[row][index].PTOC_setting_pickup_current) {
              relay[row][index].faultState = true;
              //calculate TMS
              long factor = relay[row][index].Measurement[k] / relay[row][index].PTOC_setting_pickup_current;
              relay[row][index].PTOC_Timer[k] += factor; // add factor while there is a fault

              if(relay[row][index].PTOC_Timer[k] > relay[row][index].PTOC_setting_time_multiplier) { // if timer valure is exceded, trip
                relay[row][index].tripState = true;
                setFaultRegister(&relay[row][index], Phase_OC);
              }
            }
            else
            {
              relay[row][index].PTOC_Timer[k] = 0; //no cooloff period, just a reset after current below
            }
          }
        }  
      }
      else {
        for (int k = 0; k < 4; k++) {
          relay[row][index].Measurement[k] = 0;
        }        
      }
    }

    //simple voltage meausring device on the busbar
    if(relay[row][index].deviceType == TYPE_MEASURE)
    {
      // TYPE_RELAY_INCOMING must be closed
      if(relay[row][TYPE_RELAY_INCOMING_INDEX].breakerState == true) { // breaker closed
        //update voltage values from ADC
        for (int k = 0; k < 3; k++) {
          relay[row][index].Measurement[k] = (long)getAdcValue(6 + k + (row*3));
        }
        //calculate Uneutral
        relay[row][index].Measurement[4] = (long)residual(
                                                                  relay[row][index].Measurement[0],
                                                                  relay[row][index].Measurement[1],
                                                                  relay[row][index].Measurement[2]);

      }
      else {
        for (int k = 0; k < 4; k++) {
          relay[row][index].Measurement[k] = 0;
        }
      }

    }
    if(relay[row][index].deviceType == TYPE_RELAY_OUTGOING)
    {
      //get values from inputs
      //simulate currents based on U values from TYPE_MEASURE, and inputs(high means normal load, low means short)
      // if breaker closed, I must be U/Rload

      relay[row][index].faultState = false; //reset faultstate before calculation
      if(relay[row][index].breakerState == true) { // breaker closed
        // check for tripstate, if true(set in previous iteration), open breaker
        if(relay[row][index].tripState == true) {
          updateBreakerOutput(&relay[row][index], false); //set breakerstate to open
          relay[row][index].PTOC_Timer[0] = 0;
          relay[row][index].PTOC_Timer[1] = 0;
          relay[row][index].PTOC_Timer[2] = 0;
          relay[row][index].PTOC_Timer[3] = 0;
          continue;
        }

        for (int k = 0; k < 4; k++) {               //for each phase
          long rload;
          if(false/*Input low=true*/) //if input is low, a short is detected
            rload = 1;//low impedance load, so high current due to short
          else
            rload = RLOAD[row][index-TYPE_RELAY_OUTGOING_INDEX]; // nominal load value

          relay[row][index].Measurement[k] = relay[row][TYPE_MEASURE_INDEX].Measurement[k] / rload; //load current
          //
          // check for tripstate, if true(set in previous iteration), open breaker
          if(relay[row][index].tripState == true && relay[row][index].breakerState == true) {
            updateBreakerOutput(&relay[row][index], false); //set breakerstate to open
          }
          //
          // calculate if feeder current exceeds max value, if so, set fault, set tripstate to true
          //PIOC
          if(relay[row][index].Measurement[k] >= relay[row][index].PIOC_setting_pickup_current) {
            relay[row][index].faultState = true;
            if(relay[row][index].tripState == false) { //PIOC is immediate trip
                relay[row][index].tripState = true;
                setFaultRegister(&relay[row][index], Earth_fault);
            }
          }
          else {
            //PTOC
            if(relay[row][index].Measurement[k] >= relay[row][index].PTOC_setting_pickup_current) {
              relay[row][index].faultState = true;
              //calculate TMS
              long factor = relay[row][index].Measurement[k] / relay[row][index].PTOC_setting_pickup_current;
              relay[row][index].PTOC_Timer[k] += factor; // add factor while there is a fault

              if(relay[row][index].PTOC_Timer[k] > relay[row][index].PTOC_setting_time_multiplier) { // if timer valure is exceded, trip
                relay[row][index].tripState = true;
                setFaultRegister(&relay[row][index], Phase_OC);
              }
            }
            else
            {
              relay[row][index].PTOC_Timer[k] = 0; //no cooloff period, just a reset after current below
            }
          }
        } 
      }
      else { // if breaker open, I=0
        for (int k = 0; k < 4; k++) {
          relay[row][index].Measurement[k] = 0;
        }
      }
    }
  }
}


void RtuLogic_tick()
{
  uint32_t now = millis();
  if (now - tSWI < RTU_SWI_INTERVAL)
    return;
  tSWI = now;

  performLogic(0);// row 1
  performLogic(1);// row 2

  /*
  digitalWrite(ms_output_array[(swi_pin_counter % MS_OUT_NUM_CHANNELS)], HIGH);       // sets the digital pin on
  digitalWrite(ms_output_array[((swi_pin_counter+(MS_OUT_NUM_CHANNELS-1)) % MS_OUT_NUM_CHANNELS)], LOW);        // sets the previous digital pin off

  if(swi_pin_counter < (MS_OUT_NUM_CHANNELS-1))
    swi_pin_counter++;
  else
    swi_pin_counter = 0;
  */
}

relay_state* getRelayData(uint8_t row, uint8_t col)
{
  return &relay[row][col];
}

relay_state* getRelayDataByIndex(uint8_t index)
{
  if(index >= RELAY_ROWS * RELAY_AMOUNT)
    return nullptr; // invalid index

  uint8_t row = index / RELAY_AMOUNT;    // (0 or 1)
  uint8_t col = index % RELAY_AMOUNT;    // (0-4)
  return &relay[row][col];
}

void process_breaker(relay_state *relay, uint8_t breaker, Origin origin) //, 1 = Open, 2 = Close  
{
  if(origin == relay->remote) // if operarion is allowed
  {
    updateBreakerOutput(relay, (breaker - 1));
  }
}

void process_trip(relay_state *relay, uint8_t trip_reset, Origin origin) // 1 is reset
{
  if(origin == relay->remote && trip_reset == 1) // if operarion is allowed
  {
    relay->tripState = false;
  }
}

void setFaultRegister(relay_state* relay, FaultEvent event)
{
  relay->faultEvent = event;
  relay->faultTime = millis();
}

void updateBreakerOutput(relay_state *relay, uint8_t state)
{
  if(relay->breakerState != state) { // if breaker needs to move
    relay->breakerState = state;
    if(relay->breakerState == true) {
      digitalWrite(ms_output_array[(relay->index % MS_OUT_NUM_CHANNELS)], HIGH);       // sets the digital pin on
      //Serial.println("BRRR");
    }
    else {
      digitalWrite(ms_output_array[(relay->index % MS_OUT_NUM_CHANNELS)], LOW);        // sets the digital pin off
      //Serial.println("BANG");
    }
  }
}