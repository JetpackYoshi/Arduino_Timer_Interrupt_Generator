from code_generator import Generator

class CodeGenerator:

    def __init__(self):
        self.generator = Generator()
        self.timerOptions = None

    def selectFreq(self):
        freq = document.getElementById('freq').value
        self.timerOptions = self.generator.generateScales(freq)

        sel = document.getElementById('mySelect')
        sel.options.length = 0

        validTimers = [key for key in self.timerOptions.keys() if len(self.timerOptions[key]) is not 0]
        sel.options.length = len(validTimers)
        for idx,timer in enumerate(validTimers):
            sel.options[idx].text = str(timer)

    def generate(self):
        freq = document.getElementById('freq').value
        options = self.generator.generateScales(freq)
        timer = 1
        prescalar = 1024
        code = self.generator.generateCode(timer, prescalar, dict(options[timer])[prescalar])
        document.getElementById('output').innerHTML = code




codeGenerator = CodeGenerator()