﻿"""
Wrappers for OUTPUT devices connected to GPIO
"""
import threading
import RPi.GPIO as GPIO


class Led(object):
    """Represent LED as output"""

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.__blinking_frequency = -1  # indicates no blinking
        self.__stop_blink_event = None
        self.__thread = None
        self.turn_off()  # reset state

    def turn_on(self):
        """turnes LED on"""

        self.__ensure_not_blinking()
        GPIO.output(self.pin, True)

    def turn_off(self):
        """turnes LED off"""

        self.__ensure_not_blinking()
        GPIO.output(self.pin, False)

    def blink_fast(self):
        """starts fast blinking of LED"""

        self.blink(0.06)

    def blink_slow(self):
        """starts slow blinking of LED"""

        self.blink(0.5)

    def blink(self, frequency):
        """starts blinking of LED"""

        if self.__blinking_frequency == -1:
            # no blinking currently => create worker for it
            self.__stop_blink_event = threading.Event()
            self.__thread = threading.Thread(target=self.__do_blinking)
            self.__thread.daemon = True
            self.__thread.start()

        self.__blinking_frequency = frequency

    def __do_blinking(self):
        state = False
        GPIO.output(self.pin, state)

        while not self.__stop_blink_event.is_set():
            state = not state
            GPIO.output(self.pin, state)
            self.__stop_blink_event.wait(self.__blinking_frequency)

    def __ensure_not_blinking(self):
        if self.__blinking_frequency == -1:
            return

        self.__stop_blink_event.set()
        self.__thread.join()
        self.__blinking_frequency = -1
