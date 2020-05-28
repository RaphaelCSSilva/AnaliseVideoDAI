

class MaxDetectionBuffer:

    def __init__(self, buffSize):

        self.buffSize = buffSize

        self.arrayMaxDetectionBuffer = []

    def update(self, numPessoasDet):

        if len(self.arrayMaxDetectionBuffer) == 0:
            self.arrayMaxDetectionBuffer.append(numPessoasDet)
        elif self.arrayMaxDetectionBuffer[len(self.arrayMaxDetectionBuffer) - 1] == numPessoasDet:
            self.arrayMaxDetectionBuffer.insert(len(self.arrayMaxDetectionBuffer), numPessoasDet)
        else:
            self.arrayMaxDetectionBuffer.clear()
            self.arrayMaxDetectionBuffer.append(numPessoasDet)

    def isFull(self):

        return len(self.arrayMaxDetectionBuffer) == self.buffSize

    def getMaxDetectionNum(self):

        return self.arrayMaxDetectionBuffer[0]

    def clearBufferArray(self):
        self.arrayMaxDetectionBuffer.clear()