from itertools import compress
from pprint import pprint

class Generator:
    timers = {
        'UNO': {
            0: (8, ['CS02', 'CS01', 'CS00']),
            1: (16, ['CS12', 'CS11', 'CS10']),
            2: (8, ['CS22', 'CS21', 'CS20'])
        }
    }
    prescalers = [1, 8, 64, 256, 1024]

    ctc_regs = ["WGM01", "WGM12", "WGM21"]

    ctc_strings = [
        "TCCR0A |= (1 << WGM01)",
        "TCCR1B |= (1 << WGM12)",
        "TCCR2A |= (1 << WGM21)"]

    clock_bits = {
        1: [0, 0, 1],
        8: [0, 1, 0],
        64: [0, 1, 1],
        256: [1, 0, 0],
        1024: [1, 0, 1]
    }

    template = """
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

    def __init__(self, clock_frequency=16e6, board='UNO'):
        self._clock_frequency = clock_frequency
        self.setBoard(board)

        self._interrupt_frequency = None
        self._timer = None
        self._prescalar = None
        self._scaleCombos = {}

    def setBoard(self, board_name):
        if board_name not in self.timers:
            raise ValueError("{} is not a valid board".format(board_name))
        else:
            self._board = board_name

    def setClockFrequency(self, frequency):
        self._clock_frequency = frequency

    def setTimerNumber(self, timer_number):
        self._timer = timer_number

    def setPrescaler(self, prescalar):
        if prescalar not in self.prescalers:
            raise ValueError("{} is not a valid prescaler".format(prescalar))
        else:
            self._prescalar = prescalar

    def setInterruptFrequency(self, frequency):
        self._interrupt_frequency = frequency

    def generateScaleCombos(self):
        clock_resolution = 1 / self._clock_frequency
        output = {}
        for timer, res in self.timers[self._board].items():
            output[timer] = []
            for value in self.prescalers:
                timer_resolution = value * clock_resolution
                time_counts = int((1 / self._interrupt_frequency) / timer_resolution) - 1
                if time_counts < 2 ** res[0]:
                    output[timer].append((value, time_counts))

        self._scaleCombos = output
        return output

    def getScaleCombos(self):
        return self._scaleCombos

    def getValidTimers(self):
        validTimers = [key for key in self._scaleCombos.keys() if len(self._scaleCombos[key]) is not 0]
        return validTimers

    def _generatePrescaleCode(self):
        preSclRegs = []
        for i in range(2, -1, -1):
            preSclRegs.append("CS{}{}".format(self._timer, i))

        foo = list(compress(preSclRegs, self.clock_bits[self._prescalar]))
        bar = " | ".join(["(1 << {})".format(item) for item in foo])
        return bar

    def generateCode(self):
        count_val = dict(self._scaleCombos[self._timer])[self._prescalar]
        setup_code = self.template.format(
            timer=self._timer,
            prescale_str=self._generatePrescaleCode(),
            count_val=count_val,
            ctc_string=self.ctc_strings[self._timer],
            prescalar=self._prescalar
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
                           timer=self._timer)

def Main(ISR_Freq,board='UNO'):
    generator = Generator()
    generator.setInterruptFrequency(ISR_Freq)
    print("Here are the options:\n")
    options = generator.generateScaleCombos()
    pprint(options)
    timer = int(input("Enter Selected Timer: "))
    prescalar = int(input("Enter Selected Prescalar: "))
    generator.setTimerNumber(timer)
    generator.setPrescaler(prescalar)
    code = generator.generateCode()
    print(code)

if __name__ == '__main__':
    Desired_Interrupt_Frequency = 2
    Main(2)
