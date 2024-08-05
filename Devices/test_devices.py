from gpiozero import LED, Buzzer
from time import sleep

# LED GPIO pins
led_pins = [17, 23, 27, 22]
leds = [LED(pin) for pin in led_pins]

# Buzzer GPIO pin
buzzer = Buzzer(24)

try:
    while True:
        # Turn on all LEDs and the buzzer
        for led in leds:
            led.on()
        buzzer.on()
        sleep(1)

        # Turn off all LEDs and the buzzer
        for led in leds:
            led.off()
        buzzer.off()
        sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO settings
    for led in leds:
        led.off()
    buzzer.off()
