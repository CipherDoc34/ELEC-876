# Define variables for paths
SRC_DIR = src
LIBS_DIR = C:/Users/leopa/BigCloneEval/libs
BIN_DIR = bin
VERSION_FILE = src/util/Version.java.template
VERSION_OUTPUT = src/util/Version.java

# Default target: build the project
all: version
	mkdir -p $(BIN_DIR)
	javac -d $(BIN_DIR) -cp "$(LIBS_DIR)/*:$(SRC_DIR)" $(SRC_DIR)/util/*.java $(SRC_DIR)/tasks/*.java

# Version target
version:
	# Get the latest Git commit hash as version
	VERSION = $(shell git log -1 --pretty=format:"%h")
	# Copy and modify version file
	cp $(VERSION_FILE) $(VERSION_OUTPUT)
	-sed "s/%%VERSION%%/$(VERSION)/g" $(VERSION_FILE) > $(VERSION_OUTPUT)

# Clean target: remove bin directory
clean:
	rm -rf $(BIN_DIR)
