from pprint import pprint
from itertools import compress

class Generator:

    def __init__(self):
        self.timers = {
            'UNO':{
                0:(8,['CS02','CS01','CS00']),
                1:(16,['CS12','CS11','CS10']),
                2:(8, ['CS22','CS21','CS20'])
                }
            }
        self.prescalers = [1, 8, 64, 256, 1024]

        self.ctc_regs = ["WGM01","WGM12","WGM21"]

        self.ctc_strings = [
            "TCCR0A |= (1 << WGM01)",
            "TCCR1B |= (1 << WGM12)",
            "TCCR2A |= (1 << WGM21)"]

        self.clock_bits = {
            1:[0,0,1],
            8:[0,1,0],
            64:[0,1,1],
            256:[1,0,0],
            1024:[1,0,1]
            }

        self.template = """
//set timer{timer} interrupt at 1Hz
  TCCR{timer}A = 0;// set entire TCCR1A register to 0
  TCCR{timer}B = 0;// same for TCCR1B
  TCNT{timer}  = 0;//initialize counter value to 0
  // set compare match register
  OCR{timer}A = {count_val};
  // turn on CTC mode
  {ctc_string};
  // Set appropriate bits for {prescalar} prescaler
  TCCR{timer}B |= {prescale_str};  
  // enable timer compare interrupt
  TIMSK{timer} |= (1 << OCIE{timer}A);
"""

    def generateScales(self, interrupt_frequency, board='UNO', clock_frequency=16e6):
        clock_resolution = 1 / clock_frequency
        output = {}
        for timer, res in self.timers[board].items():
            output[timer] = []
            for value in self.prescalers:
                timer_resolution = value * clock_resolution
                time_counts = int((1 / interrupt_frequency) / timer_resolution) - 1
                if time_counts < 2 ** res[0]:
                    output[timer].append((value, time_counts))
        return output

    def generatePrescaleCode(self, timer, prescaler):
        preSclRegs = []
        for i in range(2, -1, -1):
            preSclRegs.append("CS{}{}".format(timer, i))

        foo = list(compress(preSclRegs, self.clock_bits[prescaler]))
        bar = " | ".join(["(1 << {})".format(item) for item in foo])
        return bar

    def generateCode(self, timer, prescalar, count_val):
        setup_code = self.template.format(
            timer=timer,
            prescale_str=self.generatePrescaleCode(timer, prescalar),
            count_val=count_val,
            ctc_string=self.ctc_strings[timer],
            prescalar=prescalar
        )

        code = """
cli(); //stop interrupts
{setup_code}
sei(); //allow interrupts

ISR(TIMER{timer}_COMPA_vect){{
    // Do Something
}}
        """
        return code.format(setup_code=setup_code,
                           timer=timer)

def Main(ISR_Freq,board='UNO'):
    generator = Generator()
    print("Here are the options:\n")
    options = generator.generateScales(ISR_Freq)
    pprint(options)
    timer = int(input("Enter Selected Timer: "))
    prescalar = int(input("Enter Selected Prescalar: "))
    code = generator.generateCode(timer,prescalar,dict(options[timer])[prescalar])
    print(code)

if __name__ == '__main__':
    Desired_Interrupt_Frequency = 2
    Main(2)