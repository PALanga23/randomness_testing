## Randomness Testing Undergraduate Challenge
This repository contains all the necessary materials to play the randomness testing challenge. Teams should write their analysis in a separate document and send it to the challenge managers (palanga@wpi.edu and/or bswheeler@wpi.edu) for review and grading. It is expected that the setup of the NIST test suite (as outlined in NISTCodeExplanation) will take ~5 minutes and that each trial/analysis will take 5-10 minutes depending on analysis type and familiarity with Python if applicable. Teams should first follow the NIST setup explanation document, then use the Guidelines document for necessary background information about each test. 

### The directory structure is as follows:
- **Guidelines.pptx** Explains the format of the challenge and background information about each of the tests (may require downloading to view).
- **NISTCodeExplanation** Explains how to utilize the NIST code suite to perform the tests on the provided pseudorandom numbers.
- **Generators** contains the flawed Python code for analysis. 
- **PseudorandomNumbers** contains the generated random numbers to test with the NIST code suite.

### Prerequisites 
If choosing to run the NIST test suite on the provided bitstreams, you will need a way to compile and run C code.
