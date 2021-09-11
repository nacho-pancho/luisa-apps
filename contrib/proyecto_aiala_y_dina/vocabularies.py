from dotenv import load_dotenv
load_dotenv()
from modules.postprocessor import Postprocessor

postprocessor = Postprocessor()

postprocessor.load_vocabulary("vocabulary1.4.txt")

postprocessor.save_sysmspell("vocabulary1.4.pkl")