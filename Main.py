# yossef katri 322263310 asaf levi 212384507 team 50
import os
from Parser import *
from Tokenizer import *
PATH = r"C:\Users\אסף\OneDrive\שולחן העבודה\עקרונות שפות תכנה\Exercises\Targil5\project 11\ComplexArrays\\"

l = os.listdir(PATH)
for file in l:
    if file.endswith(".jack"):
        tokenaizer = Tokenizing(PATH + file)
        tokenaizer.file_to_tokens()
        tokenaizer.file.close()
        tokenaizer.fileXML.close()

l = os.listdir(PATH)
for file in l:
    if file.endswith("T.xml"):
        parser = Parser(PATH + file)
        parser.parse_class()
        parser.fileXML.close()
        parser.fileVM.close()
        parser.file.close()
        print("finished "+parser.class_name+'.vm')