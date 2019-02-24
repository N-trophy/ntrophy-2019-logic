TARGET = solution

all: $(TARGET).pdf clean

$(TARGET).pdf: $(TARGET).tex level4.pdf
	texfot pdflatex $^

clean:
	rm -rf $(TARGET).aux $(TARGET).log $(TARGET).out

pdfclean: clean
	rm -rf $(TARGET).pdf

