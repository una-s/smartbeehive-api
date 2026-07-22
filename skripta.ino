#include "DHT.h"

#define DHTPIN A0     
#define DHTTYPE DHT11   

DHT dht(DHTPIN, DHTTYPE);

// Ovde definises ID kosnice na kojoj se nalazi ovaj senzor:
const int KOSNICA_ID = 1;

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000); // Pauza od 2 sekunde izmedju citanja

  float vlaznost = dht.readHumidity();
  float temperatura = dht.readTemperature();

  // Ako citanje ne uspe, preskaci slanje greske kroz serial u JSON formatu
  if (isnan(vlaznost) || isnan(temperatura)) {
    return; 
  }

  // Pravljenje JSON formata: {"kosnica_id": 1, "temperatura": 25.4, "vlaznost": 58.2}
  Serial.print("{\"kosnica_id\":");
  Serial.print(KOSNICA_ID);
  Serial.print(",\"temperatura\":");
  Serial.print(temperatura);
  Serial.print(",\"vlaznost\":");
  Serial.print(vlaznost);
  Serial.println("}");
}
