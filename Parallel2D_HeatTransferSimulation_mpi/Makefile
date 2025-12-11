CC = mpicc
CFLAGS = -Wall -Wextra -O2 -std=c99
LIBS = -lm

TARGET = heat_mpi
SRC = heat_mpi.c
PYTHON_DEPS = numpy matplotlib scipy pillow

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)
	@echo "✅ Built $(TARGET)"

run: $(TARGET)
	mpirun -np 4 ./$(TARGET)

# Use an MPI hostfile to run across multiple machines
run-hosts: $(TARGET)
	mpirun -np 4 --hostfile hosts ./$(TARGET)

visualize:
	python3 visualize.py

visualize-advanced:
	python3 advanced_visualize.py

install-deps:
	pip3 install $(PYTHON_DEPS)

clean:
	rm -f $(TARGET)

clean-all: clean
	rm -f output_*.txt output_final.txt *.gif *.png
	rm -rf plots

.PHONY: all run run-hosts visualize visualize-advanced install-deps clean clean-all
