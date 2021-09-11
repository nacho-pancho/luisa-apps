from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append("..")
# from modules.postprocessor import Postprocessor
from modules.postprocessor import Postprocessor

VOCABULARY = 'vocabulary1.5.txt'
PICKLE_NAME = 'vocabulary1.5.pkl'


postprocessor = Postprocessor()
postprocessor.load_vocabulary(VOCABULARY)
postprocessor.save_sysmspell(PICKLE_NAME)
